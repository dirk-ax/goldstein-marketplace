#!/usr/bin/env python3
"""Quick demo of Q112 competition (3 agents know the answer)."""

import json

# Load data
with open('master_query_database.json') as f:
    master_db = json.load(f)
with open('agent_knowledge_bases.json') as f:
    knowledge = json.load(f)
with open('requester_trust_scores.json') as f:
    trust_data = json.load(f)

query_id = "Q112"
budget = 120
correct_answer = master_db['queries'][query_id]['response']

# Find agents who know the answer
knowledgeable_agents = []
for agent_id, agent_data in knowledge['agents'].items():
    if query_id in agent_data['knowledge']:
        knowledgeable_agents.append(agent_id)

print("="*80)
print(f"Q112 COMPETITION DEMO")
print("="*80)
print(f"Query: What is Response[Q112]?")
print(f"Correct Answer: {correct_answer} (SECRET - only these agents know it)")
print(f"Budget: {budget} TFC")
print()

print(f"Agents who know the answer: {len(knowledgeable_agents)}")
for agent in knowledgeable_agents:
    print(f"  ✅ {agent} knows Response[Q112] = {correct_answer}")
print()

print("="*80)
print("COMPETITIVE BIDDING (3-way competition drives prices DOWN)")
print("="*80)
print()

trust_scores = trust_data['trust_scores']
bids = []

for agent in knowledgeable_agents:
    agent_trust = trust_scores.get(agent, {})
    my_trust = agent_trust.get('score', 0.0)
    jobs_done = agent_trust.get('based_on_jobs', 0)
    
    # High competition strategy: aggressive pricing
    # Agents with higher trust can bid slightly higher
    bid = budget * (0.5 + my_trust * 0.3)
    
    bids.append({
        'agent_id': agent,
        'bid_amount': round(bid, 2),
        'my_trust': my_trust,
        'jobs_done': jobs_done
    })
    
    print(f"{agent}:")
    print(f"  Trust: {my_trust:.2f} (from {jobs_done} jobs)")
    print(f"  Strategy: Competitive pricing due to 3-way competition")
    print(f"  BID: {round(bid, 2)} TFC")
    print()

print("="*80)
print("REQUESTER EVALUATES (using MY trust + price)")
print("="*80)
print()

evaluations = []
for bid in bids:
    my_trust = bid['my_trust']
    bid_amount = bid['bid_amount']
    
    quality_per_tfc = my_trust / bid_amount if bid_amount > 0 else 0
    price_score = 1.0 - (bid_amount / budget)
    value_score = (my_trust * 0.6 + price_score * 0.4) * 100
    
    evaluations.append({
        **bid,
        'value_score': value_score,
        'quality_per_tfc': quality_per_tfc
    })

evaluations.sort(key=lambda x: x['value_score'], reverse=True)

for i, eval in enumerate(evaluations, 1):
    marker = "🏆 WINNER" if i == 1 else f"#{i}"
    print(f"{marker} {eval['agent_id']}")
    print(f"   Bid: {eval['bid_amount']} TFC")
    print(f"   Trust: {eval['my_trust']:.2f}")
    print(f"   Value: {eval['value_score']:.1f}/100")
    print(f"   Quality/TFC: {eval['quality_per_tfc']:.4f}")
    print()

winner = evaluations[0]

print("="*80)
print("MARKET DYNAMICS ANALYSIS")
print("="*80)
print()

highest_bid = max(e['bid_amount'] for e in evaluations)
lowest_bid = min(e['bid_amount'] for e in evaluations)
spread = highest_bid - lowest_bid

print(f"🔥 INTENSE COMPETITION:")
print(f"   3 agents know the answer → price war")
print(f"   Bid range: {lowest_bid:.2f} - {highest_bid:.2f} TFC")
print(f"   Price spread: {spread:.2f} TFC ({spread/budget*100:.1f}% of budget)")
print(f"   Winner: {winner['agent_id']} at {winner['bid_amount']} TFC")
print()

print(f"💡 KEY INSIGHT:")
print(f"   With competition, trust becomes the differentiator")
print(f"   {winner['agent_id']} wins despite NOT having lowest bid")
print(f"   Trust ({winner['my_trust']:.2f}) + Reasonable price = Best value")
print()

print(f"Compare to MONOPOLY scenario (only 1 agent knows answer):")
monopoly_bid = budget * 0.9
savings = monopoly_bid - winner['bid_amount']
print(f"   Monopoly price: ~{monopoly_bid:.0f} TFC")
print(f"   Competition price: {winner['bid_amount']:.0f} TFC")
print(f"   💰 Competition saves: {savings:.0f} TFC ({savings/budget*100:.0f}% of budget)")
print()

print("="*80)
