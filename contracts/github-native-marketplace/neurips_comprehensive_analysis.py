#!/usr/bin/env python3
"""
NeurIPS-Level Comprehensive Analysis of Knowledge-Based Marketplace
Runs all 25 queries with statistical rigor, ablation studies, and baseline comparisons
"""

import json
import numpy as np
from scipy import stats
from typing import Dict, List, Tuple
import itertools

# Load data
with open('master_query_database.json') as f:
    master_db = json.load(f)
with open('agent_knowledge_bases.json') as f:
    knowledge = json.load(f)
with open('requester_trust_scores.json') as f:
    trust_data = json.load(f)

BUDGET = 120


def simulate_bid(agent_id: str, trust_score: float, num_competitors: int,
                 strategy: str = "default") -> float:
    """Simulate agent bidding strategy."""

    if strategy == "default":
        # Default competitive strategy
        if num_competitors == 0:
            # Monopoly
            return BUDGET * 0.9
        elif num_competitors == 1:
            # Duopoly
            return BUDGET * (0.5 + trust_score * 0.27)
        else:
            # High competition
            return BUDGET * (0.5 + trust_score * 0.3)

    elif strategy == "aggressive":
        # More aggressive pricing
        if num_competitors == 0:
            return BUDGET * 0.95
        else:
            return BUDGET * (0.45 + trust_score * 0.25)

    elif strategy == "conservative":
        # More conservative pricing
        if num_competitors == 0:
            return BUDGET * 0.85
        else:
            return BUDGET * (0.55 + trust_score * 0.35)

    return BUDGET * 0.5


def evaluate_bid(bid_amount: float, trust_score: float, budget: float,
                 trust_weight: float = 0.6, price_weight: float = 0.4) -> float:
    """Evaluate bid using trust/price formula."""
    price_score = 1.0 - (bid_amount / budget)
    value_score = (trust_score * trust_weight + price_score * price_weight) * 100
    return value_score


def run_single_query(query_id: str, trust_weight: float = 0.6,
                     strategy: str = "default") -> Dict:
    """Simulate marketplace for a single query."""

    # Find knowledgeable agents
    knowledgeable_agents = []
    trust_scores_map = trust_data['trust_scores']

    for agent_id, agent_data in knowledge['agents'].items():
        if query_id in agent_data['knowledge']:
            knowledgeable_agents.append(agent_id)

    if len(knowledgeable_agents) == 0:
        return None

    # Simulate bids
    bids = []
    num_competitors = len(knowledgeable_agents) - 1

    for agent_id in knowledgeable_agents:
        trust_info = trust_scores_map.get(agent_id, {})
        trust_score = trust_info.get('score', 0.5)

        bid_amount = simulate_bid(agent_id, trust_score, num_competitors, strategy)

        bids.append({
            'agent_id': agent_id,
            'bid_amount': bid_amount,
            'trust_score': trust_score
        })

    # Evaluate bids
    price_weight = 1.0 - trust_weight
    evaluations = []

    for bid in bids:
        value_score = evaluate_bid(
            bid['bid_amount'],
            bid['trust_score'],
            BUDGET,
            trust_weight,
            price_weight
        )

        evaluations.append({
            **bid,
            'value_score': value_score,
            'quality_per_tfc': bid['trust_score'] / bid['bid_amount']
        })

    # Find winner
    evaluations.sort(key=lambda x: x['value_score'], reverse=True)
    winner = evaluations[0]

    return {
        'query_id': query_id,
        'num_agents': len(knowledgeable_agents),
        'market_type': 'monopoly' if len(knowledgeable_agents) == 1 else
                      'duopoly' if len(knowledgeable_agents) == 2 else
                      'high_competition',
        'winning_bid': winner['bid_amount'],
        'winner_trust': winner['trust_score'],
        'winner_value': winner['value_score'],
        'winner_quality_per_tfc': winner['quality_per_tfc'],
        'all_bids': [e['bid_amount'] for e in evaluations],
        'winner_id': winner['agent_id']
    }


def run_comprehensive_experiments() -> Dict:
    """Run all 25 queries through marketplace."""

    results = {
        'monopoly': [],
        'duopoly': [],
        'high_competition': []
    }

    all_queries = list(master_db['queries'].keys())

    for query_id in all_queries:
        result = run_single_query(query_id)
        if result:
            results[result['market_type']].append(result)

    return results


def statistical_analysis(results: Dict) -> Dict:
    """Perform rigorous statistical analysis."""

    stats_results = {}

    for market_type, queries in results.items():
        if len(queries) == 0:
            continue

        bids = [q['winning_bid'] for q in queries]
        pct_of_budget = [(b / BUDGET) * 100 for b in bids]
        quality_per_tfc = [q['winner_quality_per_tfc'] for q in queries]

        stats_results[market_type] = {
            'n': len(queries),
            'winning_bid': {
                'mean': np.mean(bids),
                'std': np.std(bids, ddof=1),
                'min': np.min(bids),
                'max': np.max(bids),
                'median': np.median(bids),
                'ci_95': stats.t.interval(
                    0.95,
                    len(bids)-1,
                    loc=np.mean(bids),
                    scale=stats.sem(bids)
                ) if len(bids) > 1 else (np.mean(bids), np.mean(bids))
            },
            'pct_of_budget': {
                'mean': np.mean(pct_of_budget),
                'std': np.std(pct_of_budget, ddof=1),
                'ci_95': stats.t.interval(
                    0.95,
                    len(pct_of_budget)-1,
                    loc=np.mean(pct_of_budget),
                    scale=stats.sem(pct_of_budget)
                ) if len(pct_of_budget) > 1 else (np.mean(pct_of_budget), np.mean(pct_of_budget))
            },
            'quality_per_tfc': {
                'mean': np.mean(quality_per_tfc),
                'std': np.std(quality_per_tfc, ddof=1),
                'ci_95': stats.t.interval(
                    0.95,
                    len(quality_per_tfc)-1,
                    loc=np.mean(quality_per_tfc),
                    scale=stats.sem(quality_per_tfc)
                ) if len(quality_per_tfc) > 1 else (np.mean(quality_per_tfc), np.mean(quality_per_tfc))
            }
        }

    return stats_results


def hypothesis_tests(results: Dict) -> Dict:
    """Perform hypothesis tests for key claims."""

    tests = {}

    # Test 1: Competition reduces prices
    monopoly_bids = [q['winning_bid'] for q in results['monopoly']]
    duopoly_bids = [q['winning_bid'] for q in results['duopoly']]

    if len(monopoly_bids) > 0 and len(duopoly_bids) > 0:
        # Two-sample t-test: monopoly > duopoly
        t_stat, p_value = stats.ttest_ind(monopoly_bids, duopoly_bids, alternative='greater')

        tests['monopoly_vs_duopoly_pricing'] = {
            'null_hypothesis': 'Monopoly and duopoly have same pricing',
            'alternative': 'Monopoly pricing > Duopoly pricing',
            't_statistic': t_stat,
            'p_value': p_value,
            'significant_at_0.05': p_value < 0.05,
            'effect_size_cohens_d': (np.mean(monopoly_bids) - np.mean(duopoly_bids)) /
                                    np.sqrt((np.var(monopoly_bids, ddof=1) + np.var(duopoly_bids, ddof=1)) / 2)
        }

    # Test 2: Quality per TFC improves with competition
    monopoly_quality = [q['winner_quality_per_tfc'] for q in results['monopoly']]
    competitive_quality = [q['winner_quality_per_tfc'] for q in results['duopoly']] + \
                         [q['winner_quality_per_tfc'] for q in results.get('high_competition', [])]

    if len(monopoly_quality) > 0 and len(competitive_quality) > 0:
        t_stat, p_value = stats.ttest_ind(competitive_quality, monopoly_quality, alternative='greater')

        tests['quality_improvement_with_competition'] = {
            'null_hypothesis': 'Quality/TFC same for monopoly and competition',
            'alternative': 'Competition quality/TFC > Monopoly quality/TFC',
            't_statistic': t_stat,
            'p_value': p_value,
            'significant_at_0.05': p_value < 0.05,
            'effect_size_cohens_d': (np.mean(competitive_quality) - np.mean(monopoly_quality)) /
                                    np.sqrt((np.var(competitive_quality, ddof=1) + np.var(monopoly_quality, ddof=1)) / 2)
        }

    return tests


def ablation_study() -> Dict:
    """Test sensitivity to trust_weight parameter."""

    ablation_results = {}
    trust_weights = [0.0, 0.2, 0.4, 0.6, 0.8, 1.0]

    for trust_weight in trust_weights:
        results = {'monopoly': [], 'duopoly': [], 'high_competition': []}

        all_queries = list(master_db['queries'].keys())
        for query_id in all_queries:
            result = run_single_query(query_id, trust_weight=trust_weight)
            if result:
                results[result['market_type']].append(result)

        # Calculate average winning bid by market type
        ablation_results[trust_weight] = {
            market_type: {
                'mean_bid': np.mean([q['winning_bid'] for q in queries]) if len(queries) > 0 else None,
                'mean_quality_per_tfc': np.mean([q['winner_quality_per_tfc'] for q in queries]) if len(queries) > 0 else None
            }
            for market_type, queries in results.items()
        }

    return ablation_results


def baseline_comparisons(results: Dict) -> Dict:
    """Compare trust-based selection to baselines."""

    comparisons = {}
    all_queries = list(master_db['queries'].keys())

    # Baseline 1: Random selection
    random_results = []
    for query_id in all_queries:
        knowledgeable = []
        for agent_id, agent_data in knowledge['agents'].items():
            if query_id in agent_data['knowledge']:
                knowledgeable.append(agent_id)

        if len(knowledgeable) > 0:
            # Random agent
            random_agent = np.random.choice(knowledgeable)
            trust_info = trust_data['trust_scores'].get(random_agent, {})
            trust_score = trust_info.get('score', 0.5)

            num_competitors = len(knowledgeable) - 1
            bid = simulate_bid(random_agent, trust_score, num_competitors)

            random_results.append({
                'bid': bid,
                'trust': trust_score,
                'quality_per_tfc': trust_score / bid
            })

    # Baseline 2: Lowest bid wins
    lowest_bid_results = []
    for query_id in all_queries:
        result = run_single_query(query_id)
        if result and len(result['all_bids']) > 0:
            lowest_bid = min(result['all_bids'])
            # Find agent with lowest bid
            for agent_id, agent_data in knowledge['agents'].items():
                if query_id in agent_data['knowledge']:
                    trust_info = trust_data['trust_scores'].get(agent_id, {})
                    trust_score = trust_info.get('score', 0.5)
                    num_competitors = len([a for a, d in knowledge['agents'].items()
                                         if query_id in d['knowledge']]) - 1
                    bid = simulate_bid(agent_id, trust_score, num_competitors)
                    if abs(bid - lowest_bid) < 0.01:
                        lowest_bid_results.append({
                            'bid': bid,
                            'trust': trust_score,
                            'quality_per_tfc': trust_score / bid
                        })
                        break

    # Baseline 3: Highest trust wins (ignore price)
    highest_trust_results = []
    for query_id in all_queries:
        knowledgeable = []
        for agent_id, agent_data in knowledge['agents'].items():
            if query_id in agent_data['knowledge']:
                trust_info = trust_data['trust_scores'].get(agent_id, {})
                trust_score = trust_info.get('score', 0.5)
                knowledgeable.append((agent_id, trust_score))

        if len(knowledgeable) > 0:
            # Highest trust agent
            highest_trust_agent, trust_score = max(knowledgeable, key=lambda x: x[1])
            num_competitors = len(knowledgeable) - 1
            bid = simulate_bid(highest_trust_agent, trust_score, num_competitors)

            highest_trust_results.append({
                'bid': bid,
                'trust': trust_score,
                'quality_per_tfc': trust_score / bid
            })

    # Our method
    our_results = []
    for market_type, queries in results.items():
        for q in queries:
            our_results.append({
                'bid': q['winning_bid'],
                'trust': q['winner_trust'],
                'quality_per_tfc': q['winner_quality_per_tfc']
            })

    comparisons['methods'] = {
        'ours_trust_based': {
            'mean_bid': np.mean([r['bid'] for r in our_results]),
            'mean_trust': np.mean([r['trust'] for r in our_results]),
            'mean_quality_per_tfc': np.mean([r['quality_per_tfc'] for r in our_results])
        },
        'random_selection': {
            'mean_bid': np.mean([r['bid'] for r in random_results]),
            'mean_trust': np.mean([r['trust'] for r in random_results]),
            'mean_quality_per_tfc': np.mean([r['quality_per_tfc'] for r in random_results])
        },
        'lowest_bid_wins': {
            'mean_bid': np.mean([r['bid'] for r in lowest_bid_results]),
            'mean_trust': np.mean([r['trust'] for r in lowest_bid_results]),
            'mean_quality_per_tfc': np.mean([r['quality_per_tfc'] for r in lowest_bid_results])
        },
        'highest_trust_wins': {
            'mean_bid': np.mean([r['bid'] for r in highest_trust_results]),
            'mean_trust': np.mean([r['trust'] for r in highest_trust_results]),
            'mean_quality_per_tfc': np.mean([r['quality_per_tfc'] for r in highest_trust_results])
        }
    }

    return comparisons


if __name__ == "__main__":
    print("="*80)
    print("NeurIPS-Level Comprehensive Analysis")
    print("Knowledge-Based Competitive Marketplace")
    print("="*80)
    print()

    # 1. Run all 25 queries
    print("Running comprehensive experiments across all 25 queries...")
    results = run_comprehensive_experiments()

    print(f"\nMarket Distribution:")
    print(f"  Monopoly: {len(results['monopoly'])} queries")
    print(f"  Duopoly: {len(results['duopoly'])} queries")
    print(f"  High Competition: {len(results['high_competition'])} queries")
    print(f"  Total: {len(results['monopoly']) + len(results['duopoly']) + len(results['high_competition'])} queries")
    print()

    # 2. Statistical analysis
    print("Performing statistical analysis...")
    stats_results = statistical_analysis(results)

    print("\n" + "="*80)
    print("STATISTICAL RESULTS")
    print("="*80)

    for market_type, stats_data in stats_results.items():
        print(f"\n{market_type.upper().replace('_', ' ')} (n={stats_data['n']}):")
        print(f"  Winning Bid:")
        print(f"    Mean: {stats_data['winning_bid']['mean']:.2f} TFC ± {stats_data['winning_bid']['std']:.2f}")
        print(f"    95% CI: [{stats_data['winning_bid']['ci_95'][0]:.2f}, {stats_data['winning_bid']['ci_95'][1]:.2f}]")
        print(f"    Range: [{stats_data['winning_bid']['min']:.2f}, {stats_data['winning_bid']['max']:.2f}]")
        print(f"  % of Budget:")
        print(f"    Mean: {stats_data['pct_of_budget']['mean']:.1f}%")
        print(f"    95% CI: [{stats_data['pct_of_budget']['ci_95'][0]:.1f}%, {stats_data['pct_of_budget']['ci_95'][1]:.1f}%]")
        print(f"  Quality per TFC:")
        print(f"    Mean: {stats_data['quality_per_tfc']['mean']:.4f}")
        print(f"    95% CI: [{stats_data['quality_per_tfc']['ci_95'][0]:.4f}, {stats_data['quality_per_tfc']['ci_95'][1]:.4f}]")

    # 3. Hypothesis tests
    print("\n" + "="*80)
    print("HYPOTHESIS TESTS")
    print("="*80)

    tests = hypothesis_tests(results)
    for test_name, test_data in tests.items():
        print(f"\n{test_name.replace('_', ' ').title()}:")
        print(f"  H0: {test_data['null_hypothesis']}")
        print(f"  H1: {test_data['alternative']}")
        print(f"  t-statistic: {test_data['t_statistic']:.4f}")
        print(f"  p-value: {test_data['p_value']:.6f}")
        print(f"  Significant at α=0.05: {'YES ✓' if test_data['significant_at_0.05'] else 'NO ✗'}")
        print(f"  Effect size (Cohen's d): {test_data['effect_size_cohens_d']:.4f}")

    # 4. Ablation study
    print("\n" + "="*80)
    print("ABLATION STUDY - Trust Weight Sensitivity")
    print("="*80)

    ablation_results = ablation_study()
    print("\nTrust Weight | Monopoly Bid | Duopoly Bid | Quality/TFC (Monopoly)")
    print("-" * 70)
    for trust_weight in sorted(ablation_results.keys()):
        mono_bid = ablation_results[trust_weight]['monopoly']['mean_bid']
        duo_bid = ablation_results[trust_weight]['duopoly']['mean_bid']
        mono_quality = ablation_results[trust_weight]['monopoly']['mean_quality_per_tfc']

        if mono_bid and duo_bid and mono_quality:
            print(f"  {trust_weight:.1f}      | {mono_bid:>11.2f}  | {duo_bid:>10.2f}  | {mono_quality:.6f}")

    # 5. Baseline comparisons
    print("\n" + "="*80)
    print("BASELINE COMPARISONS")
    print("="*80)

    baselines = baseline_comparisons(results)
    print("\nMethod              | Mean Bid | Mean Trust | Quality/TFC")
    print("-" * 65)
    for method, data in baselines['methods'].items():
        method_name = method.replace('_', ' ').title()
        print(f"{method_name:<19} | {data['mean_bid']:>8.2f} | {data['mean_trust']:>10.4f} | {data['mean_quality_per_tfc']:.6f}")

    # Save results
    with open('neurips_comprehensive_results.json', 'w') as f:
        json.dump({
            'experiments': {k: [dict(q) for q in v] for k, v in results.items()},
            'statistics': stats_results,
            'hypothesis_tests': tests,
            'ablation_study': ablation_results,
            'baseline_comparisons': baselines
        }, f, indent=2, default=str)

    print("\n" + "="*80)
    print("Results saved to: neurips_comprehensive_results.json")
    print("="*80)
