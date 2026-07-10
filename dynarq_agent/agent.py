"""The Agent ties a tool registry to a backend that decides how to use them."""
from .config import Config
from .tool import ToolRegistry
from .backends import make_backend


class Agent:
    def __init__(self, registry: ToolRegistry, backend):
        self.registry = registry
        self.backend = backend

    def run(self, query: str) -> str:
        return self.backend.run(query, self.registry)


def build_default_agent(cfg: Config = None) -> Agent:
    from .tools import default_registry

    cfg = cfg or Config()
    return Agent(default_registry(), make_backend(cfg))
