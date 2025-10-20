#!/usr/bin/env python3
"""
Run agents to analyze and bid on open contracts.
"""

import json
import subprocess
from agents.agent_subcontracting import (
    AgentKnowledge,
    SubcontractingAgent,
    ProfitLedger,
    QueryParser
)


def get_open_issues():
    """Get all open query-task issues."""
    result = subprocess.run(
        ['gh', 'issue', 'list', '--label', 'query-task', '--json', 'number,title,body'],
        capture_output=True,
        text=True,
        check=True
    )
    return json.loads(result.stdout)


def post_bid(issue_number, agent_id, bid_amount, strategy):
    """Post a bid as a comment on an issue."""
    comment = f"""## Bid from {agent_id}

**Bid Amount:** {bid_amount} TFC

**Strategy:** {strategy}

**Status:** Ready to execute
"""

    subprocess.run(
        ['gh', 'issue', 'comment', str(issue_number), '--body', comment],
        capture_output=True,
        text=True,
        check=True
    )
    print(f"  ✅ {agent_id} bid ${bid_amount} on Issue #{issue_number}")


def main():
    print("="*80)
    print("RUNNING AGENTS ON OPEN CONTRACTS")
    print("="*80)
    print()

    # Initialize agents
    agents = {
        "Agent_Proof_Generator_1": AgentKnowledge("Agent_Proof_Generator_1", {
            "12": "22",
            "222": "10"
        }),
        "Agent_Proof_Generator_2": AgentKnowledge("Agent_Proof_Generator_2", {
            "10": "44",
            "34": "09"
        }),
        "Agent_Proof_Generator_3": AgentKnowledge("Agent_Proof_Generator_3", {
            "44": "88",
            "55": "77"
        }),
    }

    ledger = ProfitLedger("agents/payment_ledger.json")

    # Get open issues
    issues = get_open_issues()
    print(f"Found {len(issues)} open contracts")
    print()

    # Have each agent analyze each issue
    for issue in issues:
        print(f"Issue #{issue['number']}: {issue['title']}")
        print("-" * 80)

        # Extract query from body
        body = issue['body']
        query_line = [line for line in body.split('\n') if '**Query:**' in line]
        if not query_line:
            print("  ⚠️  Could not extract query")
            continue

        query = query_line[0].replace('**Query:**', '').strip()

        # Extract budget
        budget_line = [line for line in body.split('\n') if '**Budget:**' in line]
        if not budget_line:
            print("  ⚠️  Could not extract budget")
            continue

        budget_str = budget_line[0].replace('**Budget:**', '').replace('TFC', '').strip()
        budget = float(budget_str)

        print(f"  Query: {query}")
        print(f"  Budget: ${budget} TFC")
        print()

        # Each agent analyzes
        for agent_id, knowledge in agents.items():
            agent = SubcontractingAgent(knowledge, ledger)
            strategy = agent.analyze_contract(query, budget)

            print(f"  {agent_id}:")
            print(f"    Action: {strategy['action']}")

            if strategy['action'] == 'bid_directly':
                print(f"    Bid: ${strategy['bid_amount']:.2f}")
                # Post bid
                post_bid(
                    issue['number'],
                    agent_id,
                    f"{strategy['bid_amount']:.2f}",
                    "Direct knowledge - can solve immediately"
                )
            elif strategy['action'] == 'subcontract':
                print(f"    Would subcontract: {strategy['subcontract_query']}")
                print(f"    Subcontract budget: ${strategy['subcontract_budget']:.2f}")
                # Post bid indicating subcontracting strategy
                post_bid(
                    issue['number'],
                    agent_id,
                    f"{budget * 0.9:.2f}",
                    f"Will subcontract for {strategy['subcontract_query']} to complete"
                )
            else:
                print(f"    Cannot bid - no knowledge")

            print()

        print()


if __name__ == "__main__":
    main()
