#!/usr/bin/env python3
"""Count actual market distribution from agent knowledge bases."""

import json

with open('agent_knowledge_bases.json') as f:
    data = json.load(f)

with open('master_query_database.json') as f:
    master = json.load(f)

# Get all queries
all_queries = set(master['queries'].keys())

# Count agents per query
query_counts = {}
for agent_id, agent_data in data['agents'].items():
    for query_id in agent_data['knowledge'].keys():
        if query_id not in query_counts:
            query_counts[query_id] = []
        query_counts[query_id].append(agent_id)

# Categorize by competition level
monopoly = []  # 1 agent
duopoly = []   # 2 agents
high_comp = [] # 3+ agents

for query_id in all_queries:
    agents = query_counts.get(query_id, [])
    num_agents = len(agents)

    if num_agents == 1:
        monopoly.append((query_id, agents))
    elif num_agents == 2:
        duopoly.append((query_id, agents))
    elif num_agents >= 3:
        high_comp.append((query_id, agents))

print("="*80)
print("MARKET DISTRIBUTION (Corrected)")
print("="*80)
print()

print(f"Monopoly (1 agent knows): {len(monopoly)} queries")
for q, agents in sorted(monopoly):
    print(f"  {q}: {agents[0]}")
print()

print(f"Duopoly (2 agents know): {len(duopoly)} queries")
for q, agents in sorted(duopoly):
    print(f"  {q}: {', '.join(agents)}")
print()

print(f"High Competition (3+ agents know): {len(high_comp)} queries")
for q, agents in sorted(high_comp):
    print(f"  {q}: {len(agents)} agents - {', '.join(agents)}")
print()

print("="*80)
print("SUMMARY")
print("="*80)
print(f"Total queries: {len(all_queries)}")
print(f"  Monopoly: {len(monopoly)}")
print(f"  Duopoly: {len(duopoly)}")
print(f"  High Competition: {len(high_comp)}")
print()

# Verify competition_analysis
print("="*80)
print("COMPETITION_ANALYSIS VERIFICATION")
print("="*80)

comp_analysis = data['competition_analysis']
errors = []

for query_key, listed_agents in comp_analysis.items():
    query_id = query_key.split('_')[0]
    actual_agents = query_counts.get(query_id, [])

    listed_set = set(listed_agents)
    actual_set = set(actual_agents)

    if listed_set != actual_set:
        errors.append({
            'query': query_id,
            'listed': listed_agents,
            'actual': actual_agents,
            'missing': list(actual_set - listed_set),
            'extra': list(listed_set - actual_set)
        })

if errors:
    print(f"❌ ERRORS FOUND: {len(errors)}")
    for err in errors:
        print(f"\n{err['query']}:")
        print(f"  Listed: {err['listed']}")
        print(f"  Actual: {err['actual']}")
        if err['missing']:
            print(f"  Missing: {err['missing']}")
        if err['extra']:
            print(f"  Extra (incorrect): {err['extra']}")
else:
    print("✅ All competition_analysis entries match actual agent knowledge")
