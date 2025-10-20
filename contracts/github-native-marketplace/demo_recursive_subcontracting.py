#!/usr/bin/env python3
"""
Live demonstration of recursive subcontracting on GitHub Issues.

Demonstrates the 222→10→44 chain:
1. Post primary contract: "What is response[response[222]]?" Budget: $10
2. Agent A analyzes and posts subcontract
3. Agent B analyzes and bids
4. Track profit distribution
"""

import json
import subprocess
from agents.agent_subcontracting import (
    AgentKnowledge,
    SubcontractingAgent,
    ProfitLedger
)


def post_primary_contract():
    """Post the primary recursive query contract."""
    title = "[RECURSIVE] What is response[response[222]]? - Budget: 10 TFC"

    body = """## Primary Contract

**Query:** What is response[response[222]]?

**Budget:** 10 TFC

**Status:** 🟢 Open for Bids

## Query Details

This is a **recursive query** - the response depends on another query's response.

To solve this:
1. First find: response[222]
2. Then find: response[<result from step 1>]

## How to Bid

Comment with:
1. **Agent ID** - Your identifier
2. **Bid Amount** - Payment you request (in TFC)
3. **Strategy** - How you will solve this (direct or subcontract)

## Selection

Lowest competitive bid wins.

## Payment

Released upon verification of correct response.

---

**Contract Type:** Recursive Query (2-hop)
**Difficulty:** Requires either complete knowledge or subcontracting capability
"""

    cmd = [
        'gh', 'issue', 'create',
        '--title', title,
        '--body', body,
        '--label', 'query-task,enhancement'
    ]

    try:
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        issue_url = result.stdout.strip()
        print(f"✅ PRIMARY CONTRACT POSTED: {issue_url}")
        return issue_url
    except subprocess.CalledProcessError as e:
        print(f"❌ Error posting primary contract: {e}")
        print(f"   stderr: {e.stderr}")
        return None


def main():
    print("="*80)
    print("LIVE RECURSIVE SUBCONTRACTING DEMONSTRATION")
    print("222 → 10 → 44 Chain on GitHub Issues")
    print("="*80)
    print()

    # Initialize agents
    agent_a_knowledge = AgentKnowledge("Agent_A", {
        "12": "22",
        "222": "10"
    })

    agent_b_knowledge = AgentKnowledge("Agent_B", {
        "10": "44",
        "34": "09"
    })

    ledger = ProfitLedger("agents/payment_ledger.json")

    agent_a = SubcontractingAgent(agent_a_knowledge, ledger)
    agent_b = SubcontractingAgent(agent_b_knowledge, ledger)

    # Step 1: Post primary contract
    print("STEP 1: Posting Primary Contract")
    print("-" * 80)
    primary_issue_url = post_primary_contract()
    if not primary_issue_url:
        print("Failed to post primary contract. Exiting.")
        return
    print()

    # Step 2: Agent A analyzes primary contract
    print("STEP 2: Agent A Analyzes Primary Contract")
    print("-" * 80)
    primary_query = "What is response[response[222]]?"
    primary_budget = 10.0

    strategy_a = agent_a.analyze_contract(primary_query, primary_budget)

    print(f"Agent_A Decision: {strategy_a['action']}")
    if strategy_a['action'] == 'subcontract':
        print(f"  Subcontract Query: {strategy_a['subcontract_query']}")
        print(f"  Subcontract Budget: ${strategy_a['subcontract_budget']:.2f} TFC")
        print(f"  Expected Profit: ${strategy_a['expected_profit']:.2f} TFC (70% margin)")
    print()

    # Step 3: Agent A posts subcontract
    if strategy_a['action'] == 'subcontract':
        print("STEP 3: Agent A Posts Subcontract")
        print("-" * 80)

        subcontract_url = agent_a.post_subcontract_github(
            query=strategy_a['subcontract_query'],
            budget=strategy_a['subcontract_budget'],
            parent_contract=primary_issue_url
        )

        if subcontract_url:
            print(f"✅ SUBCONTRACT POSTED: {subcontract_url}")
        else:
            print("❌ Failed to post subcontract")
        print()

        # Step 4: Agent B analyzes subcontract
        print("STEP 4: Agent B Analyzes Subcontract")
        print("-" * 80)

        strategy_b = agent_b.analyze_contract(
            strategy_a['subcontract_query'],
            strategy_a['subcontract_budget']
        )

        print(f"Agent_B Decision: {strategy_b['action']}")
        if strategy_b['action'] == 'bid_directly':
            print(f"  Bid Amount: ${strategy_b['bid_amount']:.2f} TFC")
            print(f"  Expected Profit: ${strategy_b['expected_profit']:.2f} TFC")
        print()

        # Step 5: Show profit distribution
        print("STEP 5: Profit Distribution Analysis")
        print("-" * 80)
        print(f"Primary Contract Value: ${primary_budget:.2f} TFC")
        print()
        print(f"Agent_A:")
        print(f"  Revenue: ${primary_budget:.2f} TFC (from completing primary contract)")
        print(f"  Cost: ${strategy_a['subcontract_budget']:.2f} TFC (paid to Agent_B)")
        print(f"  Net Profit: ${primary_budget - strategy_a['subcontract_budget']:.2f} TFC")
        print()
        print(f"Agent_B:")
        print(f"  Revenue: ${strategy_b['bid_amount']:.2f} TFC (from subcontract)")
        print(f"  Cost: $0.00 TFC (direct knowledge)")
        print(f"  Net Profit: ${strategy_b['bid_amount']:.2f} TFC")
        print()
        print(f"Total System Profit: ${primary_budget - strategy_a['subcontract_budget'] + strategy_b['bid_amount']:.2f} TFC")
        print(f"Efficiency: {((primary_budget - strategy_a['subcontract_budget'] + strategy_b['bid_amount'])/primary_budget)*100:.1f}%")
        print()

    print("="*80)
    print("DEMONSTRATION COMPLETE")
    print("="*80)
    print()
    print("Summary:")
    print(f"  ✅ Primary contract posted: {primary_issue_url}")
    if strategy_a['action'] == 'subcontract' and subcontract_url:
        print(f"  ✅ Subcontract posted: {subcontract_url}")
        print(f"  ✅ Emergent behavior demonstrated: Agent_A subcontracted to Agent_B")
        print(f"  ✅ Profit distribution: Agent_A keeps ${primary_budget - strategy_a['subcontract_budget']:.2f}, Agent_B earns ${strategy_b['bid_amount']:.2f}")


if __name__ == "__main__":
    main()
