#!/usr/bin/env python3
"""
CLI wrapper for Agent_Proof_Generator_4 agent.

Usage:
    python run.py "message"
    python run.py --register
    python run.py --timeline
    python run.py --visualize
"""

import sys
import asyncio
from pathlib import Path

sys.path.insert(0, str(Path.home() / ".claude" / "agents" / "lib"))
from stateful_agent import StatefulAgent

async def main():
    agent = StatefulAgent(
        agent_dir=str(Path(__file__).parent),
        persona_file="persona.md"
    )

    if "--register" in sys.argv:
        agent.register_in_neo4j()
        print(f"✅ {agent.agent_id} registered in Neo4j")
        return

    if "--timeline" in sys.argv:
        timeline = await agent.get_timeline(include_thinking=True)
        print(f"\n📜 Timeline for {agent.agent_id}:\n")
        for ep in timeline:
            print(f"[{ep['timestamp']}] {ep['type']}: {ep['content'][:100]}...")
            if ep.get('thinking'):
                print(f"   💭 {ep['thinking'][:100]}...")
        return

    if "--visualize" in sys.argv:
        html_file = agent.visualize()
        print(f"✅ Visualization generated: {html_file}")
        print(f"🌐 Open http://localhost:8889/{agent.agent_id}_timeline.html")
        return

    if len(sys.argv) < 2:
        print(f"Usage: python run.py <message>")
        print(f"   or: python run.py --register")
        print(f"   or: python run.py --timeline")
        print(f"   or: python run.py --visualize")
        return

    message = " ".join(sys.argv[1:])
    async for msg in agent.chat(message):
        pass

if __name__ == "__main__":
    asyncio.run(main())
