#!/usr/bin/env python3
"""Simple chat without hooks - just direct SDK interaction."""

import asyncio
import sys
from pathlib import Path
from claude_agent_sdk import query, ClaudeAgentOptions

async def main():
    if len(sys.argv) < 2:
        print("Usage: python3 simple_chat.py 'your message'")
        return

    message = " ".join(sys.argv[1:])

    # Load persona
    persona_path = Path(__file__).parent / "AGENT_PERSONA.md"
    with open(persona_path) as f:
        persona = f.read()

    options = ClaudeAgentOptions(
        system_prompt=persona,
        cwd=str(Path(__file__).parent),
        permission_mode='default',
        cli_path=f"{Path.home()}/.claude/local/claude"
    )

    print(f"\n🤖 Agent_Proof_Generator_2:\n")

    async for msg in query(prompt=message, options=options):
        # Only print assistant text messages
        if hasattr(msg, 'content'):
            for block in msg.content:
                if hasattr(block, 'text'):
                    print(block.text)

if __name__ == "__main__":
    asyncio.run(main())
