#!/usr/bin/env python3
"""
Simulate competitive bidding in knowledge-based marketplace.

Demonstrates how multiple agents knowing the same answer creates price competition.
"""

import json
from typing import List, Dict

def load_data():
    """Load all marketplace data."""
    with open('master_query_database.json') as f:
        master_db = json.load(f)

    with open('agent_knowledge_bases.json') as f:
        knowledge = json.load(f)

    with open('requester_trust_scores.json') as f:
        trust_data = json.load(f)

    return master_db, knowledge, trust_data

def get_agents_who_know(query_id: str, knowledge: Dict) -> List[str]:
    """Find which agents know the answer to a query."""
    agents = []
    for agent_id, agent_data in knowledge['agents'].items():
        if query_id in agent_data['knowledge']:
            agents.append(agent_id)
    return agents

def simulate_bidding(query_id: str, budget: float, master_db: Dict, knowledge: Dict, trust_data: Dict):
    """Simulate competitive bidding for a query."""

    # Get correct answer
    correct_answer = master_db['queries'][query_id]['response']

    # Find agents who know the answer
    knowledgeable_agents = get_agents_who_know(query_id, knowledge)

    print("="*80)
    print(f"QUERY: {query_id}")
    print(f"Correct Answer: {correct_answer} (SECRET)")
    print(f"Budget: {budget} TFC")
    print("="*80)
    print()

    print(f"Agents who know the answer: {len(knowledgeable_agents)}")
    for agent in knowledgeable_agents:
        print(f"  - {agent}")
    print()

    if len(knowledgeable_agents) == 0:
        print("❌ NO BIDS - No agent knows the answer")
        return

    # Simulate strategic bidding
    print("="*80)
    print("BIDDING SIMULATION")
    print("="*80)
    print()

    trust_scores = trust_data['trust_scores']

    bids = []

    for agent in knowledgeable_agents:
        agent_trust = trust_scores.get(agent, {})
        my_trust = agent_trust.get('score', 0.0)
        jobs_done = agent_trust.get('based_on_jobs', 0)

        # Bidding strategy based on competition level
        num_competitors = len(knowledgeable_agents) - 1

        if num_competitors == 0:
            # Monopoly - can charge high
            bid = budget * 0.9  # 90% of budget
            strategy = "MONOPOLY: High price (no competition)"
        elif num_competitors == 1:
            # Duopoly - moderate competition
            # Lower trust agents bid lower to compete
            bid = budget * (0.6 + my_trust * 0.2)
            strategy = "DUOPOLY: Competitive pricing"
        else:
            # High competition - aggressive pricing
            # Trust matters more than price
            bid = budget * (0.5 + my_trust * 0.3)
            strategy = "HIGH COMPETITION: Price war + trust differentiation"

        bids.append({
            'agent_id': agent,
            'bid_amount': round(bid, 2),
            'my_trust': my_trust,
            'jobs_done': jobs_done,
            'strategy': strategy,
            'knows_answer': True
        })

        print(f"{agent}:")
        print(f"  Trust score: {my_trust:.2f} (from {jobs_done} jobs)")
        print(f"  Bid: {round(bid, 2)} TFC")
        print(f"  Strategy: {strategy}")
        print()

    # Evaluate bids
    print("="*80)
    print("REQUESTER EVALUATION")
    print("="*80)
    print()

    evaluations = []
    for bid in bids:
        my_trust = bid['my_trust']
        bid_amount = bid['bid_amount']

        # Value calculation
        if bid_amount > 0:
            quality_per_tfc = my_trust / bid_amount
            price_score = 1.0 - (bid_amount / budget)
            value_score = (my_trust * 0.6 + price_score * 0.4) * 100
        else:
            value_score = 0

        evaluations.append({
            **bid,
            'value_score': value_score
        })

    # Sort by value
    evaluations.sort(key=lambda x: x['value_score'], reverse=True)

    print("Ranking:")
    for i, eval in enumerate(evaluations, 1):
        marker = "🏆 WINNER" if i == 1 else f"#{i}"
        print(f"{marker} {eval['agent_id']}")
        print(f"   Trust: {eval['my_trust']:.2f} | Bid: {eval['bid_amount']} TFC | Value: {eval['value_score']:.1f}")
    print()

    # Show winner
    winner = evaluations[0]
    print("="*80)
    print(f"WINNER: {winner['agent_id']}")
    print("="*80)
    print(f"  Winning bid: {winner['bid_amount']} TFC")
    print(f"  Trust score: {winner['my_trust']:.2f}")
    print(f"  Value score: {winner['value_score']:.1f}")
    print(f"  Competition level: {len(knowledgeable_agents)} agents")
    print()

    # Analyze market dynamics
    if len(knowledgeable_agents) == 1:
        print("💰 MONOPOLY PRICING:")
        print(f"   Single agent can charge {winner['bid_amount']} TFC ({winner['bid_amount']/budget*100:.0f}% of budget)")
    elif len(knowledgeable_agents) == 2:
        print("⚔️  DUOPOLY COMPETITION:")
        losing_bid = evaluations[1]['bid_amount']
        savings = losing_bid - winner['bid_amount']
        print(f"   Competition drove price from {losing_bid} → {winner['bid_amount']} TFC")
        if savings > 0:
            print(f"   Requester saves {savings:.2f} TFC ({savings/budget*100:.0f}% of budget)")
    else:
        print("🔥 INTENSE COMPETITION:")
        highest_bid = max(e['bid_amount'] for e in evaluations)
        lowest_bid = min(e['bid_amount'] for e in evaluations)
        spread = highest_bid - lowest_bid
        print(f"   Price range: {lowest_bid} - {highest_bid} TFC (spread: {spread:.2f})")
        print(f"   Winner bid: {winner['bid_amount']} TFC")
        print(f"   Trust differentiation crucial when prices converge")
    print()

def main():
    """Run simulations for different competition scenarios."""

    master_db, knowledge, trust_data = load_data()
    budget = 120  # TFC

    scenarios = [
        ("Q112", "HIGH COMPETITION (3 agents know answer)"),
        ("Q106", "HIGH COMPETITION (3 agents know answer)"),
        ("Q101", "DUOPOLY (2 agents know answer)"),
        ("Q103", "MONOPOLY (1 agent knows answer)")
    ]

    for query_id, description in scenarios:
        print("\n" + "="*80)
        print(f"SCENARIO: {description}")
        print("="*80 + "\n")

        simulate_bidding(query_id, budget, master_db, knowledge, trust_data)

        print("\n")
        input("Press Enter for next scenario...")

if __name__ == "__main__":
    main()
