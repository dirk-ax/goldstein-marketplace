import sys
import asyncio
from pathlib import Path

# Add shared library to path
sys.path.insert(0, str(Path.home() / ".claude" / "agents" / "lib"))

from stateful_agent import StatefulAgent

async def main():
    # Initialize agent
    agent = StatefulAgent(
        agent_dir=str(Path(__file__).parent),
        persona_file="persona.md"
    )

    # Register in Neo4j (first run only)
    if "--register" in sys.argv:
        agent.register_in_neo4j()
        print("✅ Agent registered in Neo4j")
        return

    # Get message from command line
    if len(sys.argv) < 2:
        print("Usage: python agent.py <message>")
        print("   or: python agent.py --register  (register in Neo4j)")
        return

    message = " ".join(sys.argv[1:])

    # Chat with agent (automatic Neo4j logging via hooks)
    async for msg in agent.chat(message):
        # Messages are already displayed by SDK
        pass

if __name__ == "__main__":
    asyncio.run(main())
