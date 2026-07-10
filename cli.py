"""Command line entry point.

    python cli.py "what is 12 * 8?"      # one-shot
    python cli.py                          # interactive
"""
import argparse
from dynarq_agent.agent import build_default_agent


def main():
    parser = argparse.ArgumentParser(description="Dynarq Agent: a tiny tool-using AI agent.")
    parser.add_argument("query", nargs="?", help="a one-shot question; omit for interactive mode")
    args = parser.parse_args()

    agent = build_default_agent()
    print(f"[backend: {agent.backend.name} | tools: {len(agent.registry)}]")

    if args.query:
        print(agent.run(args.query))
        return

    print("Ask me something (type 'quit' to exit).")
    while True:
        try:
            query = input("> ").strip()
        except (EOFError, KeyboardInterrupt):
            print()
            break
        if query.lower() in {"quit", "exit"}:
            break
        if query:
            print(agent.run(query))


if __name__ == "__main__":
    main()
