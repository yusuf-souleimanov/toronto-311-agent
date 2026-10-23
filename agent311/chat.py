"""Chat with the agent in the terminal:   python -m agent311.chat"""

from . import config
from .agent import create_agent


def main():
    if not config.has_api_key():
        print("ANTHROPIC_API_KEY is not set. Copy .env.example to .env and add your key.")
        return

    print("Loading 311 data (takes a few seconds)...")
    agent = create_agent()
    print("Toronto 311 assistant (demo). Type 'quit' to exit.\n")

    while True:
        user_text = input("You: ").strip()
        if user_text.lower() in ("quit", "exit"):
            break
        if not user_text:
            continue
        print(f"\nAgent: {agent.send(user_text)}\n")

    print(f"Session cost: ${agent.total_cost_usd:.4f}. Audit log: {agent.audit.path}")


if __name__ == "__main__":
    main()
