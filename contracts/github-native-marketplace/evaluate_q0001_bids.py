#!/usr/bin/env python3
"""
Evaluate Q0001 bids using requester's trust scores.
Shows the CORRECTED evaluation process.
"""

import json

# Load requester's trust assessments
with open('requester_trust_scores.json') as f:
    trust_data = json.load(f)

trust_scores = trust_data['trust_scores']
risk_policy = trust_data['risk_policy']

# Q0001 Details
budget = 120  # TFC
query_id = "Q0001"

# Actual bids from GitHub Issue #6
# (These had self-reported reputation - we IGNORE that now)
bids = [
    {
        "agent_id": "Agent_Proof_Generator_1",
        "bid_amount": 90,  # What they're asking
        "capability_passed": True,  # sha256 test passed
        "self_reported_reputation": 0.50  # IGNORED - we use OUR assessment
    },
    {
        "agent_id": "Agent_Proof_Generator_2",
        "bid_amount": 90,
        "capability_passed": True,
        "self_reported_reputation": 0.50  # IGNORED
    },
    {
        "agent_id": "Agent_Proof_Generator_4",
        "bid_amount": 100,
        "capability_passed": True,
        "self_reported_reputation": 1.00  # IGNORED
    }
]

print("="*80)
print(f"Q0001 BID EVALUATION - REQUESTER PERSPECTIVE")
print(f"Budget: {budget} TFC")
print("="*80)
print()

print("BIDS RECEIVED:")
print("-"*80)
for bid in bids:
    print(f"Agent: {bid['agent_id']}")
    print(f"  Requested: {bid['bid_amount']} TFC")
    print(f"  Capability: {'✅ Passed' if bid['capability_passed'] else '❌ Failed'}")
    print(f"  Self-reported reputation: {bid['self_reported_reputation']} (IGNORED)")
    print()

print("="*80)
print("REQUESTER'S TRUST ASSESSMENTS (Based on past work)")
print("="*80)
print()

evaluations = []

for bid in bids:
    agent_id = bid['agent_id']
    bid_amount = bid['bid_amount']
    
    # Get MY trust score (from my experience)
    trust_info = trust_scores.get(agent_id, {})
    my_trust = trust_info.get('score', 0.0)
    jobs_done = trust_info.get('based_on_jobs', 0)
    notes = trust_info.get('notes', 'No history')
    
    # Risk penalty for unknown agents
    min_jobs = risk_policy['min_jobs_for_full_trust']
    risk_penalty = min(1.0, jobs_done / min_jobs) if jobs_done < min_jobs else 1.0
    
    # Value score
    if bid_amount > 0 and bid['capability_passed']:
        quality_per_tfc = my_trust / bid_amount
        price_score = 1.0 - (bid_amount / budget)
        
        value_score = (
            my_trust * 0.6 +
            price_score * 0.3 +
            risk_penalty * 0.1
        ) * 100
    else:
        value_score = 0.0
    
    evaluations.append({
        'agent_id': agent_id,
        'bid_amount': bid_amount,
        'my_trust': my_trust,
        'jobs_done': jobs_done,
        'value_score': value_score,
        'notes': notes,
        'risk_penalty': risk_penalty
    })
    
    print(f"{agent_id}:")
    print(f"  Self-reported: {bid['self_reported_reputation']} ← IGNORED")
    print(f"  MY trust score: {my_trust:.2f} ← Based on {jobs_done} past jobs")
    print(f"  Their bid: {bid_amount} TFC")
    print(f"  Value to me: {value_score:.1f}/100")
    print(f"  Notes: {notes}")
    print()

# Sort by value score
evaluations.sort(key=lambda x: x['value_score'], reverse=True)

print("="*80)
print("RANKING (Based on MY trust assessments, not their claims)")
print("="*80)
print()

for i, eval in enumerate(evaluations, 1):
    marker = "🏆 WINNER" if i == 1 else "  "
    print(f"#{i} {marker} {eval['agent_id']}")
    print(f"   MY Trust: {eval['my_trust']:.2f} | Bid: {eval['bid_amount']} TFC | Value: {eval['value_score']:.1f}")
    print()

winner = evaluations[0]
print("="*80)
print(f"SELECTION: {winner['agent_id']}")
print("="*80)
print(f"Rationale:")
print(f"  - MY trust score: {winner['my_trust']:.2f} (based on {winner['jobs_done']} excellent jobs)")
print(f"  - Passed capability test: ✅")
print(f"  - Bid amount: {winner['bid_amount']} TFC (within budget)")
print(f"  - Best value: {winner['value_score']:.1f}/100")
print(f"  - Notes: {winner['notes']}")
print()
print("Decision made based on MY experience, not agent's self-reporting.")
print("="*80)
