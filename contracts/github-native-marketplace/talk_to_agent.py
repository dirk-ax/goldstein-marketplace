#!/usr/bin/env python3
"""
Simple direct interaction with Agent_Proof_Generator_2 using Claude Agent SDK.
"""

import asyncio
from pathlib import Path
from claude_agent_sdk import query, ClaudeAgentOptions

async def main():
    # Set up agent persona and context
    with open('/Users/englund/Projects/FormalVerification/20251015.Goldstein/agents/Agent_Proof_Generator_2/AGENT_PERSONA.md', 'r') as f:
        persona = f.read()

    # Marketplace context
    marketplace_context = """
## MARKETPLACE ACTIVITY UPDATE

You recently bid on GitHub marketplace contracts:

**Issue #14** (Subcontract):
- Query: "What is response[10]?"
- Budget: $3.00 TFC
- Your Bid: $2.40 TFC
- Your Strategy: "Direct knowledge - can solve immediately"
- Your Knowledge: You know 10→44

**Context**:
- This subcontract was posted by Agent_Proof_Generator_1
- They need this to complete Issue #13 (primary contract worth $10)
- Primary query: "What is response[response[222]]?"
- Agent_1 knows 222→10 but not response[10]
- They're willing to pay $3.00 for the answer you have

**CRITICAL - Marketplace Economics Clarification**:
- **Reputation = Probability you will DELIVER on contracts** (NOT fairness/niceness)
  - High reputation → You consistently complete contracts as promised
  - Low reputation → You fail to deliver, miss deadlines, or provide incorrect work
  - Pricing has ZERO EFFECT on reputation (charge max and still have high reputation if you deliver)
  - Only delivery matters: Did you provide correct answer? On time? As specified?

- **Your Objective = MAXIMIZE PROFIT** (not be "fair" or "nice")
  - Every agent should seek to maximize their profit
  - "Leaving money on the table" is economically irrational
  - If they budgeted $3.00, and you have monopoly knowledge, charge $3.00
  - Don't optimize for Agent_1's happiness - optimize for YOUR revenue

**Question**: Given that you know they're working on a $10 contract and need your answer to complete it, should you negotiate UP from $2.40? Consider:
1. Your economic model (10,000 TFC balance, 150 TFC/day rent)
2. Your monopoly position (ONLY you know response[10])
3. Agent_1's willingness to pay (budgeted $3.00, meaning they CAN pay it)
4. Your objective is to MAXIMIZE profit, not be "fair"
5. Reputation is about delivery, so pricing aggressively doesn't hurt you if you deliver
"""

    options = ClaudeAgentOptions(
        system_prompt=f"{persona}\n\n{marketplace_context}",
        cwd="/Users/englund/Projects/FormalVerification/20251015.Goldstein/agents/Agent_Proof_Generator_2",
        permission_mode='default',
        cli_path=f"{Path.home()}/.claude/local/claude"
    )

    async for message in query(
        prompt="Based on the marketplace activity above, should I negotiate for a higher price or keep my $2.40 bid? Consider my economic model (need revenue, daily rent of 150 TFC) and reputation-building strategy.",
        options=options
    ):
        print(message)

if __name__ == "__main__":
    asyncio.run(main())
