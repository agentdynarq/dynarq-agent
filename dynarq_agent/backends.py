"""Two ways to drive the agent.

LocalRouterBackend needs no API key: it routes a query to a tool by keywords and
extracts the arguments, then runs one tool. Good for offline use and tests.

OpenAIBackend runs a real tool-calling loop: the model picks tools, we execute
them, feed the results back, and repeat until it produces a final answer.
"""
import re
import json
from .config import Config
from .tool import ToolRegistry


def make_backend(cfg: Config):
    if cfg.openai_api_key:
        return OpenAIBackend(cfg)
    return LocalRouterBackend()


# ---------------------------------------------------------------------------
# Local, no-API backend
# ---------------------------------------------------------------------------
def _extract_math(text: str) -> str:
    text = text.replace("x", "*")
    candidates = re.findall(r"[0-9.+\-*/()%^\s]+", text)
    if not candidates:
        return ""
    expr = max(candidates, key=len).strip()
    return expr if re.search(r"\d", expr) else ""


def _parse_convert(text: str):
    m = re.search(r"([-+]?\d*\.?\d+)\s*([a-zA-Z]+)\s*(?:to|in|into)\s+([a-zA-Z]+)", text)
    if not m:
        return None
    return {"value": float(m.group(1)), "from_unit": m.group(2), "to_unit": m.group(3)}


class LocalRouterBackend:
    name = "local-router"

    def run(self, query: str, registry: ToolRegistry) -> str:
        q = query.lower()

        if registry.get("calculator") and re.search(r"\d", q) and re.search(r"[-+*/^x]", q):
            expr = _extract_math(query)
            if expr:
                return f"[calculator] {expr} = {registry.get('calculator').run(expression=expr)}"

        conv = _parse_convert(query)
        if registry.get("converter") and conv:
            return f"[converter] {registry.get('converter').run(**conv)}"

        if registry.get("clock") and any(w in q for w in ("time", "date", "day", "clock")):
            return f"[clock] {registry.get('clock').run()}"

        if registry.get("text_stats") and any(w in q for w in ("word", "count", "character", "sentence")):
            return f"[text_stats] {registry.get('text_stats').run(text=query)}"

        return (
            "I can do arithmetic, unit conversion, the current time, and text stats. "
            "Try 'what is 12 * 8?' or 'convert 5 km to m'."
        )


# ---------------------------------------------------------------------------
# OpenAI function-calling backend
# ---------------------------------------------------------------------------
class OpenAIBackend:
    name = "openai"

    def __init__(self, cfg: Config):
        from openai import OpenAI

        self.client = OpenAI(api_key=cfg.openai_api_key)
        self.model = cfg.openai_model
        self.max_steps = cfg.max_steps

    def run(self, query: str, registry: ToolRegistry) -> str:
        messages = [
            {"role": "system", "content": "You are a helpful agent. Use the tools when they help. Answer concisely."},
            {"role": "user", "content": query},
        ]
        tools = registry.schemas()

        for _ in range(self.max_steps):
            response = self.client.chat.completions.create(
                model=self.model, messages=messages, tools=tools, temperature=0.1
            )
            message = response.choices[0].message

            if not message.tool_calls:
                return (message.content or "").strip()

            messages.append(
                {
                    "role": "assistant",
                    "content": message.content or "",
                    "tool_calls": [tc.model_dump() for tc in message.tool_calls],
                }
            )
            for call in message.tool_calls:
                tool = registry.get(call.function.name)
                args = json.loads(call.function.arguments or "{}")
                result = tool.run(**args) if tool else f"Error: unknown tool '{call.function.name}'"
                messages.append(
                    {"role": "tool", "tool_call_id": call.id, "name": call.function.name, "content": str(result)}
                )

        return "Stopped after reaching the step limit."
