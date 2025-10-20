#!/usr/bin/env python3
"""
Query and visualize the marketplace graph from Neo4j.
"""

import json


def print_section(title):
    print()
    print("="*80)
    print(title)
    print("="*80)
    print()


def main():
    print_section("MARKETPLACE GRAPH VISUALIZATION")

    # This would be populated by MCP neo4j queries
    # For now, showing the structure

    print("""
Graph Schema:
------------

(Agent)-[:KNOWS]->(Knowledge)
(Agent)-[:POSTED {reason, margin, expected_profit}]->(Contract:SUBCONTRACT)
(Agent)-[:BID]->(Bid)-[:BID_ON]->(Contract)
(Contract:SUBCONTRACT)-[:SUBCONTRACT_OF]->(Contract:PRIMARY)

Current State:
-------------

Agent_Proof_Generator_1:
  KNOWS: {12→22, 222→10}
  POSTED: Issue #14 (subcontract)
    - Reason: "Needs response[10] to complete primary"
    - Expected profit: $7.00
    - Margin: 70%
  BID: $9.00 on Issue #13
    - Strategy: "Will subcontract for What is response[10]?"

Agent_Proof_Generator_2:
  KNOWS: {10→44, 34→09}
  BID: $2.40 on Issue #14
    - Strategy: "Direct knowledge - can solve immediately"

Agent_Proof_Generator_3:
  KNOWS: {44→88, 55→77}
  (no activity yet)

Contract Chain:
--------------

Issue #13 (PRIMARY)
  Query: "What is response[response[222]]?"
  Budget: $10.00
  Status: OPEN
  ↑
  |
  SUBCONTRACT_OF
  |
Issue #14 (SUBCONTRACT)
  Query: "What is response[10]?"
  Budget: $3.00
  Status: OPEN
  Posted by: Agent_Proof_Generator_1

Resolution Path:
---------------

1. Agent_Proof_Generator_1 wins Issue #13 for $9.00
2. Agent_Proof_Generator_1 accepts Agent_Proof_Generator_2's bid on Issue #14 for $2.40
3. Agent_Proof_Generator_2 provides response[10] = 44
4. Agent_Proof_Generator_1 completes response[response[222]]:
   - response[222] = 10 (own knowledge)
   - response[10] = 44 (from Agent_Proof_Generator_2)
   - Final answer: 44
5. Profit distribution:
   - Agent_Proof_Generator_1: $9.00 - $2.40 = $6.60
   - Agent_Proof_Generator_2: $2.40

Query Examples:
--------------

# Find all subcontracting chains
MATCH path = (primary:Contract {type: 'PRIMARY'})<-[:SUBCONTRACT_OF*]-(sub:Contract)
RETURN path

# Find which agent knows what
MATCH (a:Agent)-[:KNOWS]->(k:Knowledge)
RETURN a.id, collect(k.query + '→' + k.response) as knowledge

# Show profit flow
MATCH (primary:Contract {type: 'PRIMARY'})<-[:SUBCONTRACT_OF]-(sub)
MATCH (a1:Agent)-[:POSTED {expected_profit: ep}]->(sub)
MATCH (a1)-[:BID]->(b1:Bid)-[:BID_ON]->(primary)
MATCH (a2:Agent)-[:BID]->(b2:Bid)-[:BID_ON]->(sub)
RETURN
  primary.budget as total_value,
  a1.id as prime_contractor,
  b1.amount as prime_bid,
  ep as prime_expected_profit,
  a2.id as subcontractor,
  b2.amount as subcontract_bid,
  b1.amount - b2.amount as prime_actual_profit

# Find agents who can solve a query
MATCH (a:Agent)-[:KNOWS]->(k:Knowledge {query: '10'})
RETURN a.id, k.response

# Trace knowledge dependencies for recursive query
MATCH (c:Contract {query: 'What is response[response[222]]?'})
MATCH (a1:Agent)-[:KNOWS]->(k1:Knowledge {query: '222'})
MATCH (a2:Agent)-[:KNOWS]->(k2:Knowledge {query: k1.response})
RETURN
  c.query,
  a1.id as knows_first_hop,
  k1.query + '→' + k1.response as first_hop,
  a2.id as knows_second_hop,
  k2.query + '→' + k2.response as second_hop,
  k2.response as final_answer
    """)


if __name__ == "__main__":
    main()
