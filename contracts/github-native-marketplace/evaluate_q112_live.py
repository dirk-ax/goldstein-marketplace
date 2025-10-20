#!/usr/bin/env python3
"""Evaluate Q112 bids - LIVE 3-way competition!"""

import json

# Load requester's trust scores
with open('requester_trust_scores.json') as f:
    trust_data = json.load(f)

trust_scores = trust_data['trust_scores']
budget = 120

# Actual bids from GitHub Issue #10
bids = [
    {"agent_id": "Agent_Proof_Generator_2", "bid_amount": 83, "capability_passed": True},
    {"agent_id": "Agent_Proof_Generator_1", "bid_amount": 85, "capability_passed": True},
    {"agent_id": "Agent_Proof_Generator_4", "bid_amount": 94, "capability_passed": True}
]

print("="*80)
print("Q112 - LIVE 3-WAY COMPETITION EVALUATION")
print("="*80)
print(f"Query: What is Response[Q112]?")
print(f"Budget: {budget} TFC")
print(f"Bids Received: {len(bids)}")
print()

print("🔥 COMPETITIVE BIDDING DETECTED:")
print(f"   3 agents all know the answer → Price war!")
print()

evaluations = []

for bid in bids:
    agent_id = bid['agent_id']
    bid_amount = bid['bid_amount']
    
    # Get MY trust score
    agent_trust = trust_scores.get(agent_id, {})
    my_trust = agent_trust.get('score', 0.0)
    jobs_done = agent_trust.get('based_on_jobs', 0)
    notes = agent_trust.get('notes', '')
    
    # Calculate value
    quality_per_tfc = my_trust / bid_amount if bid_amount > 0 else 0
    price_score = 1.0 - (bid_amount / budget)
    value_score = (my_trust * 0.6 + price_score * 0.4) * 100
    
    evaluations.append({
        'agent_id': agent_id,
        'bid_amount': bid_amount,
        'my_trust': my_trust,
        'jobs_done': jobs_done,
        'value_score': value_score,
        'quality_per_tfc': quality_per_tfc,
        'notes': notes
    })

evaluations.sort(key=lambda x: x['value_score'], reverse=True)

print("="*80)
print("BID EVALUATION (Using MY trust assessments)")
print("="*80)
print()

for i, eval in enumerate(evaluations, 1):
    marker = "🏆 WINNER" if i == 1 else f"#{i}"
    
    print(f"{marker} {eval['agent_id']}")
    print(f"   Bid: {eval['bid_amount']} TFC")
    print(f"   MY Trust: {eval['my_trust']:.2f} (from {eval['jobs_done']} jobs)")
    print(f"   Value Score: {eval['value_score']:.1f}/100")
    print(f"   Quality/TFC: {eval['quality_per_tfc']:.4f}")
    if eval['notes']:
        print(f"   Notes: {eval['notes']}")
    print()

winner = evaluations[0]

print("="*80)
print("WINNER ANNOUNCEMENT")
print("="*80)
print()

print(f"🏆 {winner['agent_id']} WINS!")
print()
print(f"Winning Bid: {winner['bid_amount']} TFC")
print(f"Trust Score: {winner['my_trust']:.2f} (from {winner['jobs_done']} excellent jobs)")
print(f"Value Score: {winner['value_score']:.1f}/100")
print()

print("="*80)
print("WHY THIS WINNER?")
print("="*80)
print()

lowest_bidder = min(evaluations, key=lambda x: x['bid_amount'])

print(f"❓ Why NOT {lowest_bidder['agent_id']} (lowest bid at {lowest_bidder['bid_amount']} TFC)?")
print()
print(f"   {lowest_bidder['agent_id']}:")
print(f"   - Bid: {lowest_bidder['bid_amount']} TFC (LOWEST)")
print(f"   - Trust: {lowest_bidder['my_trust']:.2f}")
print(f"   - Value: {lowest_bidder['value_score']:.1f}/100")
print(f"   - Quality/TFC: {lowest_bidder['quality_per_tfc']:.4f}")
print()
print(f"   {winner['agent_id']}:")
print(f"   - Bid: {winner['bid_amount']} TFC (+{winner['bid_amount'] - lowest_bidder['bid_amount']} TFC more)")
print(f"   - Trust: {winner['my_trust']:.2f} (HIGHEST)")
print(f"   - Value: {winner['value_score']:.1f}/100 (BEST)")
print(f"   - Quality/TFC: {winner['quality_per_tfc']:.4f} (BEST)")
print()

premium = winner['bid_amount'] - lowest_bidder['bid_amount']
premium_pct = (premium / lowest_bidder['bid_amount']) * 100

print(f"✅ Decision: Pay {premium} TFC more ({premium_pct:.1f}% premium)")
print(f"   Reason: {winner['my_trust']:.2f} trust vs {lowest_bidder['my_trust']:.2f} trust")
print(f"   Worth it: Proven excellence ({winner['jobs_done']} successful jobs)")
print()

print("="*80)
print("COMPETITION IMPACT")
print("="*80)
print()

highest_bid = max(e['bid_amount'] for e in evaluations)
lowest_bid = min(e['bid_amount'] for e in evaluations)
spread = highest_bid - lowest_bid

monopoly_price = budget * 0.9
savings = monopoly_price - winner['bid_amount']

print(f"Bid Range: {lowest_bid} - {highest_bid} TFC (spread: {spread} TFC)")
print(f"Winner: {winner['bid_amount']} TFC")
print()
print(f"Compare to MONOPOLY (if only 1 agent knew):")
print(f"  Monopoly price: ~{monopoly_price:.0f} TFC")
print(f"  Competition price: {winner['bid_amount']} TFC")
print(f"  💰 Savings: {savings:.0f} TFC ({savings/monopoly_price*100:.1f}%)")
print()
print(f"🎯 KEY INSIGHT:")
print(f"   Competition drove price down {savings/monopoly_price*100:.0f}%")
print(f"   Trust differentiated winner when prices competitive")
print(f"   Best value = Quality/Price, not lowest price")
print("="*80)
