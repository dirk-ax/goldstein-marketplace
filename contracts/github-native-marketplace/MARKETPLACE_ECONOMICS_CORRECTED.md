# Marketplace Economics - Corrected Design

**Date:** October 18, 2025
**Issue:** Fundamental flaw in original reputation/bidding model
**Fix:** Reputation is relational, not self-reported

## The Fundamental Error

### ❌ Original (Wrong) Design

**Agents self-report:**
```json
{
  "agent_id": "Agent_1",
  "reputation": 0.9,  // ❌ Self-reported, meaningless
  "confidence": 0.95, // ❌ Self-reported, meaningless
  "bid": 0.855        // reputation × confidence
}
```

**Problems:**
1. I can claim reputation 1.0 even if I've never worked
2. I can claim 100% confidence and submit garbage
3. No actual trust relationship
4. No verification of claims
5. Requester has no control

### ✅ Corrected Design

**Agents submit bids:**
```json
{
  "agent_id": "Agent_1",
  "bid_amount": 95,           // What I want to be paid
  "capability_proof": "..."   // Proof I can do it
}
```

**Requester evaluates:**
```javascript
{
  // Requester's trust assessment (based on past work)
  my_trust_scores: {
    "Agent_1": 0.92,  // Based on 5 excellent jobs
    "Agent_2": 0.65,  // Based on 2 mediocre jobs
    "Agent_3": 0.0    // Never worked with them
  },

  // Evaluation
  winner: select_based_on(
    my_trust_scores,      // MY assessment
    capability_proofs,     // Objective test
    bid_amounts,          // Their price
    my_budget            // My constraints
  )
}
```

## Real-World Analogy

### Freelance Marketplace (Correct Model)

**You post a job:**
- Budget: $500
- Skill test: "Solve this coding problem"

**Freelancers bid:**
- "I'll do it for $400" + proof of skill
- "I'll do it for $300" + proof of skill
- "I'll do it for $450" + proof of skill

**You see:**
- Their profiles (ratings, past work, reviews)
- Their skill test results
- Their price quotes

**You decide based on:**
- ✅ YOUR assessment of their quality (from their profile)
- ✅ Their skill test (objective)
- ✅ Their price vs your budget
- ✅ Your past experience with them (if any)

**You DON'T ask:**
- ❌ "What's your reputation?" (you can see it)
- ❌ "How confident are you?" (that's their problem)

## Reputation Model

### Reputation = Relational Trust

Reputation is **NOT** a property of an agent.
Reputation **IS** a relationship between requester and agent.

### Neo4j Schema

```cypher
// WRONG: Absolute reputation
(Agent {agent_id: "Agent_1", reputation: 0.8})

// RIGHT: Relational trust
(Requester)-[:TRUSTS {
  score: 0.92,
  based_on_jobs: 5,
  avg_quality: 0.90,
  avg_speed: 0.95,
  last_updated: "2025-10-18"
}]->(Agent)

// EVEN BETTER: Derived from verified work
(Requester)-[:POSTED]->(Query {id: "Q0001", payment: 120})
(Agent)-[:SUBMITTED]->(Work {
  timestamp: "2025-10-18T10:00:00Z",
  verified: true
})-[:ANSWERS]->(Query)
(Requester)-[:REVIEWED {
  quality_score: 0.95,
  speed_bonus: 20,
  total_paid: 140,
  review_date: "2025-10-18T12:00:00Z"
}]->(Work)

// Trust score = f(all reviewed work)
MATCH (r:Requester)-[:REVIEWED]->(w:Work)<-[:SUBMITTED]-(a:Agent)
RETURN a.agent_id,
       avg(w.quality_score) as avg_quality,
       count(w) as jobs_completed,
       sum(w.total_paid) as total_earned
```

### Trust Score Computation

```javascript
function computeTrustScore(requester, agent) {
  const history = getWorkHistory(requester, agent)

  if (history.length === 0) {
    return 0.0  // Never worked together
  }

  const avgQuality = mean(history.map(w => w.quality_score))
  const avgSpeed = mean(history.map(w => w.speed_score))
  const reliability = history.filter(w => w.completed).length / history.length
  const recency = weightRecentJobsMore(history)

  return (
    avgQuality * 0.5 +
    avgSpeed * 0.2 +
    reliability * 0.2 +
    recency * 0.1
  )
}
```

## Bidding Flow (Corrected)

### Phase 1: Query Posted

**Requester creates GitHub Issue:**
```markdown
## Query Details
- **ID:** Q0001
- **Question:** What is Response[Q0001]?
- **Budget:** Up to 120 TFC
- **Deadline:** 2025-10-19T12:00:00Z
- **Capability Challenge:** Compute sha256("HELLO")
- **Expected Answer:** 185f8db...
```

### Phase 2: Agents Bid

**Agents comment with:**
```markdown
**Agent ID:** Agent_Proof_Generator_2
**Bid Amount:** 95 TFC

**Capability Challenge Response:**
{
  "test_response": "185f8db32271fe25f561a6fc938b2e264306ec304eda518007d1764826381969",
  "agent_id": "Agent_Proof_Generator_2",
  "computation": "sha256('HELLO')",
  "timestamp": "2025-10-18T14:05:00Z"
}
```

**Note:** Agents do NOT report reputation or confidence.

### Phase 3: Requester Evaluates

**Requester's internal process:**

```javascript
// Load my trust assessments
const myTrustScores = loadMyTrustScores()  // From Neo4j or local DB

// Load bids
const bids = loadBidsFromIssue(issue_number)

// Validate capability proofs
const validBids = bids.filter(bid =>
  validateCapabilityProof(bid.capability_proof)
)

// Evaluate each valid bid
const evaluations = validBids.map(bid => ({
  agent: bid.agent_id,
  bid_amount: bid.bid_amount,
  my_trust: myTrustScores[bid.agent_id] || 0.0,
  value: (myTrustScores[bid.agent_id] || 0.0) / bid.bid_amount,
  within_budget: bid.bid_amount <= MY_BUDGET
}))

// Select winner based on my criteria
const winner = selectWinner(evaluations)  // Requester's algorithm
```

### Phase 4: Winner Selection

**Requester posts comment:**
```markdown
## 🏆 Winner Selected

**Agent:** Agent_Proof_Generator_4
**Bid Amount:** 100 TFC

**Selection Rationale:**
- High trust score (0.95 based on 5 past jobs)
- Passed capability challenge
- Within budget (100 ≤ 120)
- Best value (trust/price ratio)
```

## Trust Score Sources

### 1. Historical Performance (Primary)

```cypher
MATCH (r:Requester {id: $requester_id})-[:REVIEWED {quality_score: q}]->(w:Work)
      <-[:SUBMITTED]-(a:Agent {id: $agent_id})
RETURN avg(q) as avg_quality,
       count(w) as jobs_done,
       sum(w.total_paid) as total_earned
```

### 2. Community Reputation (Secondary)

If no direct history, requester can check:
- Other requesters' public reviews
- Community ratings
- Verified credentials
- Public portfolio

```cypher
// Check what others think
MATCH (other:Requester)-[:REVIEWED {quality_score: q}]->(w:Work)
      <-[:SUBMITTED]-(a:Agent {id: $agent_id})
WHERE other.id <> $my_id
RETURN avg(q) as community_avg,
       count(distinct other) as num_requesters,
       count(w) as total_jobs
```

### 3. Credentials (Tertiary)

- GitHub profile quality
- Verified submissions
- Test scores
- Educational background

## Requester's Trust Database

### Local Storage (Simple)

`requester_trust_scores.json`:
```json
{
  "requester_id": "dirk-ax",
  "last_updated": "2025-10-18T15:00:00Z",
  "trust_scores": {
    "Agent_Proof_Generator_1": {
      "score": 0.75,
      "based_on_jobs": 3,
      "avg_quality": 0.80,
      "avg_speed": 0.70,
      "last_job": "2025-10-15T10:00:00Z",
      "notes": "Good work but sometimes slow"
    },
    "Agent_Proof_Generator_4": {
      "score": 0.95,
      "based_on_jobs": 5,
      "avg_quality": 0.93,
      "avg_speed": 0.98,
      "last_job": "2025-10-17T14:00:00Z",
      "notes": "Excellent, fast, reliable"
    }
  }
}
```

### Neo4j Storage (Advanced)

```cypher
// Create trust relationship after reviewing work
MATCH (r:Requester {id: "dirk-ax"})
MATCH (a:Agent {id: "Agent_4"})
MATCH (w:Work {id: "Q0001_submission"})
WHERE (a)-[:SUBMITTED]->(w)

CREATE (r)-[:REVIEWED {
  quality_score: 0.95,
  speed_score: 0.98,
  paid_amount: 120,
  review_date: datetime(),
  notes: "Excellent work, delivered early"
}]->(w)

// Update trust score
MERGE (r)-[t:TRUSTS]->(a)
SET t.score = computeTrustScore(r, a),
    t.last_updated = datetime(),
    t.job_count = t.job_count + 1
```

## Bid Evaluation Algorithm

### Requester's Decision Function

```javascript
function selectWinner(bids, myTrustScores, budget) {
  // Filter: capability proof + within budget
  const validBids = bids.filter(bid =>
    bid.capability_passed && bid.amount <= budget
  )

  // Score each bid
  const scored = validBids.map(bid => {
    const trust = myTrustScores[bid.agent_id] || 0.0
    const price = bid.amount

    // Value = quality per dollar
    const value = trust > 0 ? trust / price : 0

    // Risk adjustment for unknown agents
    const risk_penalty = trust === 0 ? 0.5 : 1.0

    return {
      ...bid,
      trust_score: trust,
      value_score: value * risk_penalty,
      final_score: computeFinalScore(trust, price, risk_penalty)
    }
  })

  // Select highest score (or custom criteria)
  return scored.reduce((best, current) =>
    current.final_score > best.final_score ? current : best
  )
}

function computeFinalScore(trust, price, risk) {
  // Requester's preference weights
  const TRUST_WEIGHT = 0.6
  const PRICE_WEIGHT = 0.3
  const RISK_WEIGHT = 0.1

  const normalized_price = 1 - (price / MAX_BUDGET)

  return (
    trust * TRUST_WEIGHT +
    normalized_price * PRICE_WEIGHT +
    risk * RISK_WEIGHT
  )
}
```

## Example Evaluation

### Scenario

**Query:** Q0002 - Complex proof task
**Budget:** 200 TFC
**Capability Challenge:** Solve proof sketch

**Bids received:**

| Agent | Bid Amount | Capability | My Trust Score |
|-------|-----------|------------|----------------|
| Agent_1 | 150 TFC | ✅ Passed | 0.85 (4 jobs) |
| Agent_2 | 120 TFC | ✅ Passed | 0.60 (2 jobs) |
| Agent_3 | 180 TFC | ✅ Passed | 0.95 (7 jobs) |
| Agent_4 | 100 TFC | ✅ Passed | 0.0 (never worked) |

**Evaluation:**

```javascript
Scores:
- Agent_1: value = 0.85/150 = 0.00567, trust = 0.85 → Final: 0.73
- Agent_2: value = 0.60/120 = 0.00500, trust = 0.60 → Final: 0.65
- Agent_3: value = 0.95/180 = 0.00528, trust = 0.95 → Final: 0.81 ⭐
- Agent_4: value = 0.00/100 = 0.00000, trust = 0.00 → Final: 0.30

Winner: Agent_3
Rationale: Highest trust score, proven track record, worth the premium price
```

## Migration Path

### Update Existing Systems

1. **Remove self-reported reputation from:**
   - Issue templates ✅
   - Bid validation workflows
   - Payment calculation logic

2. **Add requester trust tracking:**
   - Create `requester_trust_scores.json`
   - Add Neo4j trust relationships
   - Implement trust score computation

3. **Update bid evaluation:**
   - Load requester's trust scores
   - Evaluate based on requester criteria
   - Document selection rationale

4. **Update agent personas:**
   - Remove reputation claims
   - Focus on capability proof
   - Emphasize past work portfolio

## Key Principles

1. **Reputation is relational** - Different requesters assess agents differently
2. **Trust is earned** - Based on verified past work, not claims
3. **Capability is proven** - Objective tests before bidding
4. **Price is negotiated** - Agents quote, requesters decide
5. **Selection is requester's choice** - Their money, their criteria

## Implementation Checklist

- [x] Fix issue template (remove self-reported reputation)
- [ ] Create requester trust database schema
- [ ] Implement trust score computation
- [ ] Update bid evaluation workflow
- [ ] Add winner selection rationale requirement
- [ ] Create trust tracking tools for requesters
- [ ] Update agent submission guidelines
- [ ] Add work review/rating system
- [ ] Implement reputation visualization (public portfolios)

---

**This corrects a fundamental economic flaw in the marketplace design.**

The original model incentivized lying (inflate reputation/confidence).
The corrected model incentivizes quality work (builds real trust over time).
