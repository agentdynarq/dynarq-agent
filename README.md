# dynarq-agent

[![tests](https://github.com/agentdynarq/dynarq-agent/actions/workflows/tests.yml/badge.svg)](https://github.com/agentdynarq/dynarq-agent/actions/workflows/tests.yml)
![python](https://img.shields.io/badge/python-3.10%2B-blue)
![license](https://img.shields.io/badge/license-MIT-green)

A minimal, readable **AI agent runtime**. It gives a language model a set of **tools** (also called skills), lets it decide which to call to answer a question, runs them, feeds the results back, and repeats until it has an answer. The whole loop is plain Python so you can see exactly how tool-calling agents work, without a big framework.

It runs two ways:

- **Offline** with a local keyword router (no API key, used for tests and quick demos).
- **With OpenAI** function-calling for a real multi-step tool-using loop.

Part of [Dynarq](https://www.dynarq.com).

## What an agent is here

An agent is a loop around a model and some tools:

```
question
   │
   ▼
 model decides:  answer now  ──►  final answer
   │
   └─ or call a tool (name + arguments)
        │  run the tool
        ▼
     tool result ──► back to the model ──► (loop, up to max_steps)
```

The model never runs code itself. It only *chooses* a tool and its arguments; the runtime executes the tool and returns the result. That separation is what keeps agents controllable.

## A tool (skill) is just a function with a description

```python
from dynarq_agent.tool import Tool

def reverse(text: str) -> str:
    return text[::-1]

REVERSE = Tool(
    name="reverse",
    description="Reverse a piece of text.",
    parameters={
        "type": "object",
        "properties": {"text": {"type": "string"}},
        "required": ["text"],
    },
    func=reverse,
)
```

Register it and the agent can use it:

```python
from dynarq_agent import build_default_agent
agent = build_default_agent()
agent.registry.register(REVERSE)
```

The `parameters` field is a JSON schema, which is exactly what OpenAI function-calling expects, so the same tool works in both backends.

## Built-in tools

| Tool | Does |
|---|---|
| `calculator` | Safe arithmetic (`ast`-based, no `eval`) |
| `converter` | Length (m, km, cm, mi, ft, in, yd) and temperature (c, f, k) |
| `clock` | Current UTC date and time |
| `text_stats` | Word, character and sentence counts |
| `read_file` | Read a local text file, confined to the working directory (no path traversal) |
| `fetch_url` | Fetch an http(s) page as readable text, with an SSRF guard (no private/loopback hosts) |

### A note on the two tools that touch the outside world

`read_file` and `fetch_url` are the useful-but-risky ones, so they ship with guardrails:

- **`read_file`** resolves the real path and refuses anything that lands outside the working directory, so `../../secrets.env` cannot escape the sandbox. It also caps file size and truncates long output.
- **`fetch_url`** allows only http/https, resolves the host, and refuses private, loopback, link-local and reserved addresses (for example `localhost` or the cloud metadata address `169.254.169.254`), re-checking on every redirect. This blocks the classic server-side request forgery abuse of a fetch tool.

## Quickstart

```bash
pip install -r requirements.txt   # only needed for the OpenAI backend

# offline (local router) — no key required
python cli.py "what is 12 * 8?"
python cli.py "convert 5 km to m"
python cli.py "what time is it?"
python cli.py "read the file README.md"
python cli.py "fetch https://example.com"

# interactive
python cli.py
```

To use the real tool-calling loop, add a key:

```bash
cp .env.example .env    # put OPENAI_API_KEY=sk-... inside
python cli.py "If a room is 4m by 5m, what is its area in square metres, and what is that in square feet?"
```

With a key the model can chain tools across several steps; offline, the router handles one tool per query.

## Project structure

```
dynarq-agent/
  cli.py                    one-shot / interactive entry point
  dynarq_agent/
    tool.py                 Tool + ToolRegistry (JSON-schema based)
    agent.py                the Agent (registry + backend)
    backends.py             LocalRouterBackend + OpenAIBackend (the loop)
    config.py               settings from environment
    tools/
      calculator.py         safe arithmetic
      converter.py          unit conversion
      datetime_tool.py      current time
      text_tools.py         text statistics
      file_reader.py        read a local file (path-traversal guarded)
      http_fetch.py         fetch a web page (SSRF guarded)
  tests/                    tool tests + local-agent routing tests
  requirements.txt
```

## Tests

The tools and the offline agent are fully tested without any API access:

```bash
python -m unittest discover -s tests -v
```

## Design notes

- Tools are described with JSON schema, so adding a skill never touches the agent loop.
- The calculator parses with `ast` and only allows numeric operators, so it cannot execute arbitrary code.
- The backend is swappable: the same tools and registry work offline or with OpenAI.

## Roadmap

- More skills: web search, JSON/HTTP POST.
- Memory across turns in interactive mode.
- A planner that breaks a big task into sub-tasks before calling tools.
- Support for other providers (Anthropic tool use).

## License

MIT
