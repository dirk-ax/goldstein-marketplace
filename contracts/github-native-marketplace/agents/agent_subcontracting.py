#!/usr/bin/env python3
"""
Agent subcontracting system - enables agents to:
1. Parse recursive queries like "response[response[222]]"
2. Post subcontracts on GitHub
3. Track profit/loss
"""

import json
import re
import subprocess
from typing import Optional, List, Dict, Tuple


class AgentKnowledge:
    """Agent's private knowledge base."""

    def __init__(self, agent_id: str, knowledge: Dict[str, str]):
        self.agent_id = agent_id
        self.knowledge = knowledge  # {query: response}

    def knows(self, query: str) -> bool:
        """Check if agent knows response to query."""
        return query in self.knowledge

    def get_response(self, query: str) -> Optional[str]:
        """Get response if known."""
        return self.knowledge.get(query)


class QueryParser:
    """Parse recursive query expressions."""

    @staticmethod
    def parse(query_text: str) -> Tuple[List[str], int]:
        """
        Parse query like "What is response[response[222]]?"
        Returns: (dependency_chain, depth)

        Examples:
        - "What is response[222]?" -> (["222"], 1)
        - "What is response[response[222]]?" -> (["222", "response[222]"], 2)
        """
        # Extract the expression from natural language
        match = re.search(r'response\[([^\]]+)\]', query_text)
        if not match:
            # Simple query like "What is response to query 222?"
            match = re.search(r'query (\d+)', query_text)
            if match:
                return ([match.group(1)], 1)
            return ([], 0)

        expr = match.group(0)

        # Count nesting depth
        depth = expr.count('response[')

        # Extract innermost query
        inner_match = re.search(r'\[(\d+)\]', expr)
        if not inner_match:
            return ([], 0)

        innermost_query = inner_match.group(1)

        # Build dependency chain
        dependencies = []
        current = innermost_query
        for i in range(depth):
            dependencies.append(current)
            if i < depth - 1:
                current = f"response[{current}]"

        return (dependencies, depth)

    @staticmethod
    def can_solve_first_hop(query_text: str, knowledge: AgentKnowledge) -> Tuple[bool, Optional[str]]:
        """
        Check if agent can solve first hop of recursive query.
        Returns: (can_solve, next_query_needed)
        """
        dependencies, depth = QueryParser.parse(query_text)

        if depth == 0:
            return (False, None)

        if depth == 1:
            # Simple query
            first_query = dependencies[0]
            can_solve = knowledge.knows(first_query)
            return (can_solve, None)

        # Recursive query - check if we can solve first step
        first_query = dependencies[0]
        if knowledge.knows(first_query):
            # We know first hop, but need the next one
            next_response = knowledge.get_response(first_query)
            return (True, next_response)

        return (False, None)


class ProfitLedger:
    """Track agent profit/loss."""

    def __init__(self, ledger_path: str):
        self.ledger_path = ledger_path
        with open(ledger_path, 'r') as f:
            self.data = json.load(f)

    def record_revenue(self, agent_id: str, contract_id: str, amount: float, description: str):
        """Record revenue from completing a contract."""
        if agent_id not in self.data['agents']:
            self.data['agents'][agent_id] = {
                'total_revenue': 0.0,
                'total_costs': 0.0,
                'net_profit': 0.0,
                'transactions': []
            }

        agent = self.data['agents'][agent_id]
        agent['total_revenue'] += amount
        agent['net_profit'] = agent['total_revenue'] - agent['total_costs']
        agent['transactions'].append({
            'type': 'revenue',
            'contract_id': contract_id,
            'amount': amount,
            'description': description
        })

        self.save()

    def record_cost(self, agent_id: str, contract_id: str, amount: float, paid_to: str, description: str):
        """Record cost from posting subcontract."""
        if agent_id not in self.data['agents']:
            self.data['agents'][agent_id] = {
                'total_revenue': 0.0,
                'total_costs': 0.0,
                'net_profit': 0.0,
                'transactions': []
            }

        agent = self.data['agents'][agent_id]
        agent['total_costs'] += amount
        agent['net_profit'] = agent['total_revenue'] - agent['total_costs']
        agent['transactions'].append({
            'type': 'cost',
            'contract_id': contract_id,
            'amount': amount,
            'paid_to': paid_to,
            'description': description
        })

        self.save()

    def get_profit(self, agent_id: str) -> float:
        """Get current net profit for agent."""
        if agent_id not in self.data['agents']:
            return 0.0
        return self.data['agents'][agent_id]['net_profit']

    def save(self):
        """Save ledger to disk."""
        with open(self.ledger_path, 'w') as f:
            json.dump(self.data, f, indent=2)


class SubcontractingAgent:
    """Agent that can analyze contracts and post subcontracts."""

    def __init__(self, knowledge: AgentKnowledge, ledger: ProfitLedger):
        self.knowledge = knowledge
        self.ledger = ledger

    def analyze_contract(self, contract_query: str, budget: float) -> Dict:
        """
        Analyze a contract and determine strategy.
        Returns strategy dict with actions to take.
        """
        can_solve, next_query = QueryParser.can_solve_first_hop(contract_query, self.knowledge)

        if not can_solve:
            return {
                'action': 'cannot_bid',
                'reason': 'No knowledge of first hop'
            }

        if next_query is None:
            # Can solve directly
            return {
                'action': 'bid_directly',
                'bid_amount': budget * 0.8,  # Competitive pricing
                'expected_profit': budget * 0.8
            }

        # Need to subcontract
        profit_margin = 0.7  # Keep 70%
        subcontract_budget = budget * (1 - profit_margin)

        return {
            'action': 'subcontract',
            'subcontract_query': f"What is response[{next_query}]?",
            'subcontract_budget': subcontract_budget,
            'expected_revenue': budget,
            'expected_cost': subcontract_budget,
            'expected_profit': budget * profit_margin,
            'profit_margin': profit_margin
        }

    def post_subcontract_github(self, query: str, budget: float, parent_contract: str) -> str:
        """
        Post a subcontract as a GitHub issue.
        Returns: issue URL
        """
        title = f"[SUBCONTRACT] {query} - Payment: {budget} TFC"

        body = f"""## Subcontract Details

**Query:** {query}
**Budget:** {budget} TFC
**Posted by:** {self.knowledge.agent_id}
**Parent Contract:** {parent_contract}
**Status:** 🟢 Open for Bids

## How to Bid

Comment with:
1. **Agent ID** - Your identifier
2. **Bid Amount** - Payment you request (in TFC)
3. **Capability Proof** - Demonstrate you know the answer

## Selection

Lowest bid wins (if capability proven).

## Payment

Released upon verification of correct response.

---

**Note:** This is a subcontract. The posting agent ({self.knowledge.agent_id}) needs this to complete their own contract.
"""

        # Post via gh CLI
        cmd = [
            'gh', 'issue', 'create',
            '--title', title,
            '--body', body,
            '--label', 'subcontract,query-task'
        ]

        try:
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            issue_url = result.stdout.strip()
            return issue_url
        except subprocess.CalledProcessError as e:
            print(f"Error posting subcontract: {e}")
            return None

    def demonstrate_222_chain(self):
        """
        Demonstrate the 222→10→44 example.
        """
        print("="*80)
        print(f"AGENT: {self.knowledge.agent_id}")
        print("="*80)
        print()

        # Primary contract
        primary_query = "What is response[response[222]]?"
        primary_budget = 10.0

        print(f"📋 PRIMARY CONTRACT:")
        print(f"   Query: {primary_query}")
        print(f"   Budget: ${primary_budget}")
        print()

        # Analyze
        strategy = self.analyze_contract(primary_query, primary_budget)

        print(f"🧠 ANALYSIS:")
        print(f"   Action: {strategy['action']}")

        if strategy['action'] == 'cannot_bid':
            print(f"   Reason: {strategy['reason']}")
            return

        if strategy['action'] == 'bid_directly':
            print(f"   Bid: ${strategy['bid_amount']}")
            print(f"   Expected Profit: ${strategy['expected_profit']}")
            return

        # Subcontracting case
        print(f"   Subcontract Query: {strategy['subcontract_query']}")
        print(f"   Subcontract Budget: ${strategy['subcontract_budget']}")
        print(f"   Expected Revenue: ${strategy['expected_revenue']}")
        print(f"   Expected Cost: ${strategy['expected_cost']}")
        print(f"   Expected Profit: ${strategy['expected_profit']} ({strategy['profit_margin']*100:.0f}% margin)")
        print()

        # Post subcontract (simulated)
        print(f"📝 POSTING SUBCONTRACT:")
        print(f"   Title: [SUBCONTRACT] {strategy['subcontract_query']} - Payment: {strategy['subcontract_budget']} TFC")
        print(f"   Posted by: {self.knowledge.agent_id}")
        print()

        return strategy


# Example usage
if __name__ == "__main__":
    # Agent knowledge from your example
    agent_a_knowledge = AgentKnowledge("Agent_A", {
        "12": "22",
        "222": "10"
    })

    agent_b_knowledge = AgentKnowledge("Agent_B", {
        "10": "44",
        "34": "09"
    })

    # Create ledger
    ledger = ProfitLedger("agents/payment_ledger.json")

    # Create agents
    agent_a = SubcontractingAgent(agent_a_knowledge, ledger)
    agent_b = SubcontractingAgent(agent_b_knowledge, ledger)

    print("="*80)
    print("RECURSIVE QUERY MARKETPLACE DEMONSTRATION")
    print("222 → 10 → 44 Chain")
    print("="*80)
    print()

    # Agent A sees primary contract
    strategy_a = agent_a.demonstrate_222_chain()

    print()
    print("="*80)

    # Agent B sees the subcontract
    if strategy_a and strategy_a['action'] == 'subcontract':
        print()
        print(f"AGENT: {agent_b_knowledge.agent_id}")
        print("="*80)
        print()

        subcontract_query = strategy_a['subcontract_query']
        subcontract_budget = strategy_a['subcontract_budget']

        print(f"📋 SEES SUBCONTRACT:")
        print(f"   Query: {subcontract_query}")
        print(f"   Budget: ${subcontract_budget}")
        print()

        strategy_b = agent_b.analyze_contract(subcontract_query, subcontract_budget)

        print(f"🧠 ANALYSIS:")
        print(f"   Action: {strategy_b['action']}")

        if strategy_b['action'] == 'bid_directly':
            print(f"   Bid: ${strategy_b['bid_amount']}")
            print(f"   Expected Profit: ${strategy_b['expected_profit']}")
            print()

            print(f"💰 PROFIT DISTRIBUTION:")
            print(f"   Primary Contract: $10.00")
            print(f"   Agent A Revenue: $10.00")
            print(f"   Agent A Cost: ${subcontract_budget}")
            print(f"   Agent A Net Profit: ${10.0 - subcontract_budget}")
            print(f"   Agent B Revenue: ${strategy_b['bid_amount']}")
            print(f"   Agent B Cost: $0.00")
            print(f"   Agent B Net Profit: ${strategy_b['bid_amount']}")
            print()
            print(f"   Total Profit: ${10.0 - subcontract_budget + strategy_b['bid_amount']}")
            print(f"   Efficiency: {((10.0 - subcontract_budget + strategy_b['bid_amount'])/10.0)*100:.1f}%")
