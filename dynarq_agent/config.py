"""Runtime settings. If an OpenAI key is present the agent uses function-calling;
otherwise it falls back to a local keyword router so it still runs offline."""
import os
from dataclasses import dataclass, field
from dotenv import load_dotenv

load_dotenv()


@dataclass
class Config:
    openai_api_key: str = field(default_factory=lambda: os.getenv("OPENAI_API_KEY"))
    openai_model: str = field(default_factory=lambda: os.getenv("OPENAI_MODEL", "gpt-4o-mini"))
    max_steps: int = 5
