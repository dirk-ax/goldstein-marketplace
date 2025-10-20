#!/usr/bin/env python3
"""
Evaluate Q0002 bids using requester's trust scores.
Demonstrates CORRECTED marketplace economics.
"""

import json

# Load MY trust assessments
with open('requester_trust_scores.json') as f:
    trust_data = json.load(f)

trust_scores = trust_data['trust_scores']
risk_policy = trust_data['risk_policy']

# Q0002 Details
budget = 150  # TFC
speed_bonus = 30  # TFC
query_id = "Q0002"

# Bids from GitHub Issue #9
# Notice: NO self-reported reputation!
bids = [
    {
        "agent_id": "Agent_Proof_Generator_1",
        "bid_amount": 110,
        "capability_passed": True,
        "speed_commitment": False
    },
    {
        "agent_id": "Agent_Proof_Generator_2",
        "bid_amount": 105,
        "capability_passed": True,
        "speed_commitment": False
    },
    {
        "agent_id": "Agent_Proof_Generator_4",
        "bid_amount": 130,
        "capability_passed": True,
        "speed_commitment": True  # 4 hours for bonus
    },
    {
        "agent_id": "Agent_Proof_Generator_5",
        "bid_amount": 95,  # LOWEST BID
        "capability_passed": True,
        "speed_commitment": False
    }
]

print("="*80)
print(f"Q0002 BID EVALUATION - CORRECTED ECONOMICS")
print(f"Budget: {budget} TFC (+ {speed_bonus} TFC speed bonus)")
print("="*80)
print()

print("KEY OBSERVATION:")
print("✅ NO agent self-reported reputation (as required!)")
print("✅ All agents provided: ID + Bid + Capability Proof only")
print()

print("="*80)
print("REQUESTER'S EVALUATION (Based on MY trust scores)")
print("="*80)
print()

evaluations = []

for bid in bids:
    agent_id = bid['agent_id']
    bid_amount = bid['bid_amount']
    
    # Get MY trust score
    trust_info = trust_scores.get(agent_id, {})
    my_trust = trust_info.get('score', 0.0)
    jobs_done = trust_info.get('based_on_jobs', 0)
    notes = trust_info.get('notes', 'No history')
    
    # Risk penalty
    min_jobs = risk_policy['min_jobs_for_full_trust']
    risk_penalty = min(1.0, jobs_done / min_jobs) if jobs_done < min_jobs else 1.0
    
    # Unknown agent budget cap
    max_unknown = risk_policy['max_budget_for_unknown']
    if jobs_done == 0 and bid_amount > max_unknown:
        risk_penalty = 0.0
    
    # Speed bonus consideration
    potential_payment = bid_amount + (speed_bonus if bid['speed_commitment'] else 0)
    
    # Value score
    if bid_amount > 0 and bid['capability_passed'] and potential_payment <= budget + speed_bonus:
        quality_per_tfc = my_trust / bid_amount if bid_amount > 0 else 0
        price_score = 1.0 - (bid_amount / budget)
        speed_value = 0.1 if bid['speed_commitment'] else 0
        
        value_score = (
            my_trust * 0.5 +
            price_score * 0.3 +
            risk_penalty * 0.1 +
            speed_value * 0.1
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
        'risk_penalty': risk_penalty,
        'speed_commitment': bid['speed_commitment'],
        'potential_payment': potential_payment
    })
    
    print(f"{agent_id}:")
    print(f"  Bid: {bid_amount} TFC")
    print(f"  MY trust: {my_trust:.2f} (from {jobs_done} past jobs)")
    print(f"  Risk penalty: {risk_penalty:.2f}")
    print(f"  Speed bonus: {'Yes (4hrs)' if bid['speed_commitment'] else 'No'}")
    print(f"  Potential cost: {potential_payment} TFC")
    print(f"  Value to me: {value_score:.1f}/100")
    print(f"  Notes: {notes}")
    print()

# Sort by value
evaluations.sort(key=lambda x: x['value_score'], reverse=True)

print("="*80)
print("RANKING BY VALUE (MY trust + price + risk + speed)")
print("="*80)
print()

for i, eval in enumerate(evaluations, 1):
    marker = "🏆" if i == 1 else f"#{i}"
    print(f"{marker} {eval['agent_id']}")
    print(f"   Trust: {eval['my_trust']:.2f} | Bid: {eval['bid_amount']} TFC | Value: {eval['value_score']:.1f}")
    if eval['speed_commitment']:
        print(f"   Speed bonus: +{speed_bonus} TFC")
    print()

winner = evaluations[0]

print("="*80)
print(f"WINNER: {winner['agent_id']}")
print("="*80)
print()
print(f"Selection Rationale:")
print(f"  MY trust score: {winner['my_trust']:.2f} (from {winner['jobs_done']} verified jobs)")
print(f"  Bid amount: {winner['bid_amount']} TFC")
print(f"  Speed commitment: {'Yes - 4 hour delivery' if winner['speed_commitment'] else 'No'}")
print(f"  Total potential cost: {winner['potential_payment']} TFC")
print(f"  Value score: {winner['value_score']:.1f}/100")
print(f"  Risk penalty: {winner['risk_penalty']:.2f}")
print()
print(f"Why not the lowest bid (Agent_5 at 95 TFC)?")
agent_5 = [e for e in evaluations if e['agent_id'] == 'Agent_Proof_Generator_5'][0]
print(f"  Agent_5 trust: {agent_5['my_trust']:.2f} (zero history)")
print(f"  Agent_5 value: {agent_5['value_score']:.1f}/100")
print(f"  Risk: Unproven agent, could waste time and money")
print(f"  Decision: Pay more for proven quality")
print()
print("="*80)
print("CORRECTED ECONOMICS IN ACTION:")
print("✅ Requester uses THEIR trust assessments (not agent claims)")
print("✅ Value = Quality/Price, not just lowest price")
print("✅ Risk management prevents betting on unknown agents")
print("✅ Past verified work builds real reputation")
print("="*80)
