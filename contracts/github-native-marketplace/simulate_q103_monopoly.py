#!/usr/bin/env python3
"""Simulate monopoly pricing for Q103 (only Agent_2 knows answer)."""

import json

# Load data
with open('master_query_database.json') as f:
    master_db = json.load(f)
with open('agent_knowledge_bases.json') as f:
    knowledge = json.load(f)
with open('requester_trust_scores.json') as f:
    trust_data = json.load(f)

query_id = "Q103"
budget = 120

print("="*80)
print(f"MONOPOLY PRICING DEMONSTRATION: {query_id}")
print("="*80)
print()

# Verify only Agent_2 knows
correct_answer = master_db['queries'][query_id]['response']
knowledgeable_agents = []
for agent_id, agent_data in knowledge['agents'].items():
    if query_id in agent_data['knowledge']:
        knowledgeable_agents.append(agent_id)

print(f"Query: {query_id}")
print(f"Correct Answer: {correct_answer} (SECRET)")
print(f"Budget: {budget} TFC")
print()

print(f"Agents who know the answer: {len(knowledgeable_agents)}")
for agent in knowledgeable_agents:
    print(f"  - {agent}")
print()

if len(knowledgeable_agents) != 1:
    print(f"⚠️  Expected monopoly (1 agent), found {len(knowledgeable_agents)} agents!")
else:
    print("✅ MONOPOLY CONFIRMED - Only 1 agent knows the answer")
print()

# Simulate Agent_2's monopoly bid
agent = knowledgeable_agents[0]
trust_scores = trust_data['trust_scores']
agent_trust = trust_scores.get(agent, {})
my_trust = agent_trust.get('score', 0.0)
jobs_done = agent_trust.get('based_on_jobs', 0)

# Monopoly pricing strategy
bid = budget * 0.9  # Can charge 90% since no alternatives

print("="*80)
print("MONOPOLY BIDDING STRATEGY")
print("="*80)
print()

print(f"{agent}:")
print(f"  Trust score: {my_trust:.2f} (from {jobs_done} jobs)")
print(f"  Market position: MONOPOLY (no competitors)")
print(f"  Pricing strategy: Charge high (90% of budget)")
print(f"  Bid: {round(bid, 2)} TFC")
print()

print("💰 MONOPOLY DYNAMICS:")
print(f"  - No competition → can charge premium")
print(f"  - Requester has NO alternatives")
print(f"  - Take it or leave it pricing")
print(f"  - Agent captures {bid/budget*100:.0f}% of budget")
print()

# Compare to competitive pricing
print("="*80)
print("COMPARISON: MONOPOLY vs COMPETITION")
print("="*80)
print()

# Q112 competitive pricing
q112_winning_bid = 94.2  # From previous Q112 demonstration
q112_agents = 3

print(f"Q112 (COMPETITION - 3 agents know answer):")
print(f"  Winner bid: {q112_winning_bid} TFC")
print(f"  % of budget: {q112_winning_bid/budget*100:.0f}%")
print(f"  Market: Price war, trust differentiates")
print()

print(f"Q103 (MONOPOLY - only {agent} knows):")
print(f"  Bid: {round(bid, 2)} TFC")
print(f"  % of budget: {bid/budget*100:.0f}%")
print(f"  Market: No alternatives, premium pricing")
print()

savings = bid - q112_winning_bid
savings_pct = (savings / bid) * 100

print(f"💡 ECONOMIC INSIGHT:")
print(f"  Monopoly premium: {savings:.2f} TFC")
print(f"  Competition saves: {savings_pct:.1f}%")
print(f"  Requester pays {savings_pct:.1f}% MORE in monopoly!")
print()

print("="*80)
print("MARKET INCENTIVES CREATED")
print("="*80)
print()

print("For Agents:")
print("  📚 Learn MORE queries → expand market access")
print("  💰 Find unique knowledge → monopoly pricing")
print("  💪 Build reputation → win competitive bids")
print()

print("For Requesters:")
print("  🎯 Seek queries with multiple knowledgeable agents")
print("  💡 Competition drives better value")
print("  ⚖️  Balance trust vs price when choosing winner")
print()

print("="*80)
print("GITHUB ISSUE #11 - MONOPOLY BID")
print("="*80)
print()

print(f"Agent: {agent}")
print(f"Bid: {round(bid, 2)} TFC")
print(f"Capability: sha256('test') = 9f86d081884c7d659a2feaa0c55ad015a3bf4f1b2b0b822cd15d6c15b0f00a08")
print()
print("This bid represents monopoly pricing - agent can charge premium")
print("because requester has no alternatives.")
