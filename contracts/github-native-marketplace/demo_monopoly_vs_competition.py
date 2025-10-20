#!/usr/bin/env python3
"""Compare monopoly vs competition pricing."""

import json

# Load data
with open('master_query_database.json') as f:
    master_db = json.load(f)
with open('agent_knowledge_bases.json') as f:
    knowledge = json.load(f)
with open('requester_trust_scores.json') as f:
    trust_data = json.load(f)

budget = 120

scenarios = [
    ("Q103", "MONOPOLY"),     # Only Agent_2 knows
    ("Q112", "3-WAY COMPETITION")  # Agents 1,2,4 know
]

print("="*80)
print("MONOPOLY vs COMPETITION PRICING")
print("="*80)
print()

results = []

for query_id, market_type in scenarios:
    correct_answer = master_db['queries'][query_id]['response']
    
    # Find knowledgeable agents
    knowledgeable_agents = []
    for agent_id, agent_data in knowledge['agents'].items():
        if query_id in agent_data['knowledge']:
            knowledgeable_agents.append(agent_id)
    
    print(f"Query {query_id} - {market_type}")
    print(f"  Answer: {correct_answer}")
    print(f"  Agents who know: {', '.join(knowledgeable_agents)}")
    
    # Simulate bids
    trust_scores = trust_data['trust_scores']
    bids = []
    
    for agent in knowledgeable_agents:
        agent_trust = trust_scores.get(agent, {})
        my_trust = agent_trust.get('score', 0.0)
        
        num_competitors = len(knowledgeable_agents) - 1
        
        if num_competitors == 0:
            # Monopoly
            bid = budget * 0.9
        else:
            # Competition
            bid = budget * (0.5 + my_trust * 0.3)
        
        bids.append({
            'agent_id': agent,
            'bid_amount': round(bid, 2),
            'my_trust': my_trust
        })
    
    # Find winner
    evaluations = []
    for bid in bids:
        my_trust = bid['my_trust']
        bid_amount = bid['bid_amount']
        
        price_score = 1.0 - (bid_amount / budget)
        value_score = (my_trust * 0.6 + price_score * 0.4) * 100
        
        evaluations.append({
            **bid,
            'value_score': value_score
        })
    
    evaluations.sort(key=lambda x: x['value_score'], reverse=True)
    winner = evaluations[0]
    
    print(f"  Winner: {winner['agent_id']}")
    print(f"  Winning bid: {winner['bid_amount']} TFC ({winner['bid_amount']/budget*100:.0f}% of budget)")
    print()
    
    results.append({
        'query_id': query_id,
        'market_type': market_type,
        'num_competitors': len(knowledgeable_agents),
        'winner': winner['agent_id'],
        'winning_bid': winner['bid_amount']
    })

print("="*80)
print("COMPARISON")
print("="*80)
print()

monopoly_price = results[0]['winning_bid']
competition_price = results[1]['winning_bid']
savings = monopoly_price - competition_price
savings_pct = (savings / monopoly_price) * 100

print(f"MONOPOLY (Q103):")
print(f"  Only 1 agent knows answer")
print(f"  Price: {monopoly_price} TFC")
print(f"  Agent can charge 90% of budget (no alternatives)")
print()

print(f"COMPETITION (Q112):")
print(f"  3 agents know answer")
print(f"  Price: {competition_price} TFC")
print(f"  Price war drives bids down")
print()

print(f"💰 SAVINGS FROM COMPETITION:")
print(f"  Difference: {savings:.2f} TFC")
print(f"  Savings: {savings_pct:.1f}%")
print(f"  Requester pays {savings_pct:.1f}% LESS due to competition!")
print()

print("="*80)
print("MARKET EFFICIENCY INSIGHT")
print("="*80)
print()
print("When multiple agents have the SAME knowledge:")
print("  ✅ Competition emerges naturally")
print("  ✅ Prices drop (agents compete on price)")
print("  ✅ Trust becomes key differentiator")
print("  ✅ Requester gets better value")
print()
print("When only ONE agent has knowledge:")
print("  ⚠️  Monopoly pricing")
print("  ⚠️  High prices (90% of budget)")
print("  ⚠️  No price competition")
print("  ⚠️  Requester pays premium")
print()
print("This marketplace creates REAL economic incentives:")
print("  📚 Agents learn MORE queries (expand knowledge)")
print("  💪 Competition keeps prices fair")
print("  🏆 Quality (trust) matters when prices converge")
print("="*80)
