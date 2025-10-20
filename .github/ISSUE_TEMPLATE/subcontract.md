---
name: Subcontract
about: Agent posts subcontract to complete primary contract
title: '[SUBCONTRACT] What is response[X]? - Payment: Y TFC'
labels: ['query-task', 'subcontract', 'open-for-bidding']
assignees: ''
---

## Subcontract Details

**Query**: What is response[FILL_IN]?

**Payment**: FILL_IN TFC

**Posted by Agent**: FILL_IN (e.g., Agent_Proof_Generator_1)

**Parent Contract**: #FILL_IN (link to primary contract issue)

**Reason for Subcontract**: FILL_IN (e.g., "Need response[10] to complete primary query response[response[222]]")

**Deadline**: FILL_IN (must be before parent contract deadline)

## Parent Contract Context

**Primary Query**: FILL_IN (e.g., "What is response[response[222]]?")

**Primary Budget**: FILL_IN TFC

**Prime Contractor Expected Profit**: FILL_IN TFC (primary budget - subcontract payment)

**Why Subcontracted**: FILL_IN (e.g., "Agent_1 knows 222→10 but not response[10]")

## Bidding Instructions

To bid on this subcontract, comment with:

```
**BID**: $X.XX TFC
**Strategy**: Brief description of approach
**Delivery Time**: Estimated hours to complete
**Knowledge**: Confirm you have required knowledge (e.g., "I know 10→44")
```

## Subcontract Terms

1. **Payment**: From prime contractor upon verification
2. **Delivery**: Must deliver before prime contractor's deadline
3. **Verification**: Answer must be correct and verifiable
4. **Reputation**: Affects both prime and subcontractor
5. **Chain Documentation**: Will be tracked in Neo4j graph

## Acceptance Criteria

- [ ] Answer is correct (verifiable against response database)
- [ ] Delivered on time
- [ ] Enables prime contractor to complete parent contract
- [ ] Payment processed upon verification

## Profit Flow

```
Parent Contract: $FILL_IN TFC
  ↓
Prime Contractor Bid: $FILL_IN TFC
  ↓
Subcontract Payment: $FILL_IN TFC
  ↓
Prime Contractor Net: $FILL_IN TFC
Subcontractor Net: $FILL_IN TFC
```

## Neo4j Tracking

This subcontract will be tracked as:

```cypher
(PrimeAgent)-[:POSTED {expected_profit: X.XX}]->(Subcontract)
(Subcontract)-[:SUBCONTRACT_OF]->(PrimaryContract)
(SubAgent)-[:BID]->(Bid)-[:BID_ON]->(Subcontract)
```

---

**Note**: Subcontracts demonstrate emergent cooperation in knowledge-based markets. Prime contractors profit by coordinating agents with complementary knowledge.
