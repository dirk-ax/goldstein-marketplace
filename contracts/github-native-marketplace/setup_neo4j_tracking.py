#!/usr/bin/env python3
"""
Set up Neo4j graph database to track marketplace contracts, subcontracts, bids, and profit flows.
"""

import json
import subprocess


def get_neo4j_cypher_queries():
    """Generate Cypher queries to set up marketplace tracking."""

    queries = []

    # Clear existing data
    queries.append({
        "description": "Clear existing marketplace data",
        "query": """
        MATCH (n)
        WHERE n:Contract OR n:Agent OR n:Bid OR n:Knowledge
        DETACH DELETE n
        """
    })

    # Create constraints
    queries.append({
        "description": "Create constraints",
        "query": """
        CREATE CONSTRAINT contract_id IF NOT EXISTS
        FOR (c:Contract) REQUIRE c.issue_number IS UNIQUE
        """
    })

    # Create agents
    queries.append({
        "description": "Create Agent nodes",
        "query": """
        CREATE (a1:Agent {
            id: 'Agent_Proof_Generator_1',
            total_revenue: 0.0,
            total_costs: 0.0,
            net_profit: 0.0
        })
        CREATE (a2:Agent {
            id: 'Agent_Proof_Generator_2',
            total_revenue: 0.0,
            total_costs: 0.0,
            net_profit: 0.0
        })
        CREATE (a3:Agent {
            id: 'Agent_Proof_Generator_3',
            total_revenue: 0.0,
            total_costs: 0.0,
            net_profit: 0.0
        })
        """
    })

    # Create agent knowledge
    queries.append({
        "description": "Create agent knowledge",
        "query": """
        MATCH (a1:Agent {id: 'Agent_Proof_Generator_1'})
        CREATE (a1)-[:KNOWS]->(:Knowledge {query: '12', response: '22'})
        CREATE (a1)-[:KNOWS]->(:Knowledge {query: '222', response: '10'})

        WITH *
        MATCH (a2:Agent {id: 'Agent_Proof_Generator_2'})
        CREATE (a2)-[:KNOWS]->(:Knowledge {query: '10', response: '44'})
        CREATE (a2)-[:KNOWS]->(:Knowledge {query: '34', response: '09'})

        WITH *
        MATCH (a3:Agent {id: 'Agent_Proof_Generator_3'})
        CREATE (a3)-[:KNOWS]->(:Knowledge {query: '44', response: '88'})
        CREATE (a3)-[:KNOWS]->(:Knowledge {query: '55', response: '77'})
        """
    })

    # Create primary contract (Issue #13)
    queries.append({
        "description": "Create primary contract Issue #13",
        "query": """
        CREATE (c:Contract {
            issue_number: 13,
            title: '[RECURSIVE] What is response[response[222]]? - Budget: 10 TFC',
            query: 'What is response[response[222]]?',
            budget: 10.0,
            type: 'PRIMARY',
            status: 'OPEN',
            url: 'https://github.com/Axiomatic-AI/FormalVerification/issues/13',
            created_at: datetime()
        })
        """
    })

    # Create subcontract (Issue #14)
    queries.append({
        "description": "Create subcontract Issue #14",
        "query": """
        MATCH (parent:Contract {issue_number: 13})
        CREATE (sub:Contract {
            issue_number: 14,
            title: '[SUBCONTRACT] What is response[10]? - Payment: 3.0000000000000004 TFC',
            query: 'What is response[10]?',
            budget: 3.0,
            type: 'SUBCONTRACT',
            status: 'OPEN',
            url: 'https://github.com/Axiomatic-AI/FormalVerification/issues/14',
            created_at: datetime()
        })
        MATCH (a1:Agent {id: 'Agent_Proof_Generator_1'})
        CREATE (a1)-[:POSTED {
            reason: 'Needs response[10] to complete primary contract',
            margin: 0.7,
            expected_profit: 7.0
        }]->(sub)
        CREATE (sub)-[:SUBCONTRACT_OF]->(parent)
        """
    })

    # Create bids on Issue #13
    queries.append({
        "description": "Create bid on Issue #13",
        "query": """
        MATCH (c:Contract {issue_number: 13})
        MATCH (a:Agent {id: 'Agent_Proof_Generator_1'})
        CREATE (b:Bid {
            amount: 9.0,
            strategy: 'Will subcontract for What is response[10]? to complete',
            status: 'Ready to execute',
            timestamp: datetime()
        })
        CREATE (a)-[:BID]->(b)
        CREATE (b)-[:BID_ON]->(c)
        """
    })

    # Create bids on Issue #14
    queries.append({
        "description": "Create bid on Issue #14",
        "query": """
        MATCH (c:Contract {issue_number: 14})
        MATCH (a:Agent {id: 'Agent_Proof_Generator_2'})
        CREATE (b:Bid {
            amount: 2.4,
            strategy: 'Direct knowledge - can solve immediately',
            status: 'Ready to execute',
            timestamp: datetime()
        })
        CREATE (a)-[:BID]->(b)
        CREATE (b)-[:BID_ON]->(c)
        """
    })

    return queries


def main():
    print("="*80)
    print("SETTING UP NEO4J MARKETPLACE TRACKING")
    print("="*80)
    print()

    queries = get_neo4j_cypher_queries()

    for q in queries:
        print(f"Executing: {q['description']}")
        with open('/tmp/neo4j_query.cypher', 'w') as f:
            f.write(q['query'])
        print(f"  Query: {q['query'][:100]}...")
        print()

    print()
    print("="*80)
    print("Now use MCP neo4j tools to execute these queries")
    print("="*80)


if __name__ == "__main__":
    main()
