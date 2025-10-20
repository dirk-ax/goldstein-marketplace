#!/usr/bin/env python3
"""
Bid Evaluation Tool for Requesters

Usage:
    python evaluate_bids.py --issue 6 --budget 120

Helps requesters evaluate agent bids using their trust scores.
"""

import json
import sys
from pathlib import Path
from datetime import datetime
from typing import Dict, List


def load_trust_scores(requester_id: str = "dirk-ax") -> Dict:
    """Load requester's trust assessments."""
    trust_file = Path(__file__).parent / "requester_trust_scores.json"
    with open(trust_file) as f:
        data = json.load(f)
    return data if data["requester_id"] == requester_id else {"trust_scores": {}}


def parse_bid(comment_body: str) -> Dict:
    """Parse bid from GitHub issue comment."""
    lines = comment_body.split("\n")
    bid = {}

    for line in lines:
        if line.startswith("**Agent ID:**"):
            bid["agent_id"] = line.split(":**")[1].strip()
        elif line.startswith("**Bid Amount:**"):
            amount_str = line.split(":**")[1].strip().replace(" TFC", "")
            bid["bid_amount"] = float(amount_str)
        elif '"test_response"' in line:
            # Capability challenge passed (present in bid)
            bid["capability_passed"] = True

    return bid


def compute_value_score(trust: float, price: float, budget: float, risk_penalty: float = 1.0) -> float:
    """
    Compute value score for a bid.

    Args:
        trust: Requester's trust score for agent (0.0-1.0)
        price: Bid amount in TFC
        budget: Maximum budget
        risk_penalty: Penalty for unknown agents (0.5-1.0)

    Returns:
        Value score (higher is better)
    """
    if price > budget or price == 0:
        return 0.0

    # Quality per TFC
    quality_per_tfc = trust / price if trust > 0 else 0.0

    # Normalize price (prefer lower prices within budget)
    price_score = 1.0 - (price / budget)

    # Combined score
    TRUST_WEIGHT = 0.6
    PRICE_WEIGHT = 0.3
    RISK_WEIGHT = 0.1

    score = (
        trust * TRUST_WEIGHT +
        price_score * PRICE_WEIGHT +
        risk_penalty * RISK_WEIGHT
    )

    return score * 100  # Scale to 0-100


def evaluate_bids(bids: List[Dict], trust_data: Dict, budget: float) -> List[Dict]:
    """Evaluate all bids using requester's trust scores."""
    trust_scores = trust_data.get("trust_scores", {})
    risk_policy = trust_data.get("risk_policy", {})

    evaluations = []

    for bid in bids:
        agent_id = bid.get("agent_id")
        bid_amount = bid.get("bid_amount", 0)
        capability_passed = bid.get("capability_passed", False)

        # Get trust score (0.0 if never worked together)
        trust_info = trust_scores.get(agent_id, {})
        trust_score = trust_info.get("score", 0.0)
        jobs_done = trust_info.get("based_on_jobs", 0)

        # Risk penalty for unknown agents
        min_jobs = risk_policy.get("min_jobs_for_full_trust", 3)
        risk_penalty = min(1.0, jobs_done / min_jobs) if jobs_done < min_jobs else 1.0

        # Unknown agent budget cap
        max_unknown = risk_policy.get("max_budget_for_unknown", 50)
        if jobs_done == 0 and bid_amount > max_unknown:
            risk_penalty = 0.0  # Too risky

        # Compute scores
        value_score = compute_value_score(trust_score, bid_amount, budget, risk_penalty)

        evaluations.append({
            "agent_id": agent_id,
            "bid_amount": bid_amount,
            "trust_score": trust_score,
            "jobs_done": jobs_done,
            "capability_passed": capability_passed,
            "risk_penalty": risk_penalty,
            "value_score": value_score,
            "within_budget": bid_amount <= budget,
            "notes": trust_info.get("notes", "No history")
        })

    # Sort by value score (descending)
    evaluations.sort(key=lambda x: x["value_score"], reverse=True)

    return evaluations


def display_evaluation(evaluations: List[Dict], budget: float):
    """Display bid evaluation results."""
    print(f"\n{'='*80}")
    print(f"BID EVALUATION REPORT")
    print(f"Budget: {budget} TFC")
    print(f"{'='*80}\n")

    print(f"{'Rank':<6}{'Agent':<25}{'Bid':<10}{'Trust':<8}{'Jobs':<6}{'Cap':<6}{'Value':<8}{'Status'}")
    print(f"{'-'*80}")

    for i, eval in enumerate(evaluations, 1):
        rank = f"#{i}"
        agent = eval["agent_id"][:24]
        bid = f"{eval['bid_amount']:.0f} TFC"
        trust = f"{eval['trust_score']:.2f}"
        jobs = f"{eval['jobs_done']}"
        cap = "✅" if eval["capability_passed"] else "❌"
        value = f"{eval['value_score']:.1f}"

        if not eval["within_budget"]:
            status = "❌ OVER BUDGET"
        elif not eval["capability_passed"]:
            status = "❌ FAILED TEST"
        elif eval["risk_penalty"] == 0:
            status = "⚠️  TOO RISKY"
        elif i == 1:
            status = "🏆 RECOMMENDED"
        else:
            status = "✅ Valid"

        print(f"{rank:<6}{agent:<25}{bid:<10}{trust:<8}{jobs:<6}{cap:<6}{value:<8}{status}")

    # Show winner details
    if evaluations and evaluations[0]["within_budget"] and evaluations[0]["capability_passed"]:
        winner = evaluations[0]
        print(f"\n{'='*80}")
        print(f"RECOMMENDED WINNER: {winner['agent_id']}")
        print(f"{'='*80}")
        print(f"Bid Amount:     {winner['bid_amount']:.0f} TFC")
        print(f"Trust Score:    {winner['trust_score']:.2f} (based on {winner['jobs_done']} jobs)")
        print(f"Value Score:    {winner['value_score']:.1f}/100")
        print(f"Risk Penalty:   {winner['risk_penalty']:.2f}")
        print(f"Notes:          {winner['notes']}")
        print(f"{'='*80}\n")


def main():
    """Main entry point."""
    if len(sys.argv) < 3:
        print("Usage: python evaluate_bids.py --budget <amount> [--requester <id>]")
        print("Example: python evaluate_bids.py --budget 120")
        sys.exit(1)

    # Parse arguments
    budget = None
    requester_id = "dirk-ax"

    for i, arg in enumerate(sys.argv):
        if arg == "--budget" and i + 1 < len(sys.argv):
            budget = float(sys.argv[i + 1])
        elif arg == "--requester" and i + 1 < len(sys.argv):
            requester_id = sys.argv[i + 1]

    if budget is None:
        print("Error: --budget required")
        sys.exit(1)

    # Load trust scores
    trust_data = load_trust_scores(requester_id)

    # Example bids (in real usage, would fetch from GitHub Issue)
    example_bids = [
        {
            "agent_id": "Agent_Proof_Generator_1",
            "bid_amount": 90,
            "capability_passed": True
        },
        {
            "agent_id": "Agent_Proof_Generator_2",
            "bid_amount": 85,
            "capability_passed": True
        },
        {
            "agent_id": "Agent_Proof_Generator_3",
            "bid_amount": 75,
            "capability_passed": True
        },
        {
            "agent_id": "Agent_Proof_Generator_4",
            "bid_amount": 100,
            "capability_passed": True
        },
        {
            "agent_id": "Agent_Proof_Generator_5",
            "bid_amount": 60,
            "capability_passed": True
        }
    ]

    # Evaluate bids
    evaluations = evaluate_bids(example_bids, trust_data, budget)

    # Display results
    display_evaluation(evaluations, budget)

    print("\nTIP: Use your trust scores to make the final decision.")
    print("     The highest value score is recommended, but you have final say.\n")


if __name__ == "__main__":
    main()
