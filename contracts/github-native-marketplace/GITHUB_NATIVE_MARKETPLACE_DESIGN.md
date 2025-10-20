# GitHub-Native Marketplace Design

**Date:** 2025-10-18
**Goal:** Run entire marketplace through GitHub infrastructure
**Principle:** All transactions visible, auditable, and automated via GitHub

---

## System Architecture

```
Orchestrator
   ↓
GitHub Issue (Task + Capability Challenge)
   ↓
Issue Comments (Agent Bids + Proof of Capability)
   ↓
PR (Work Submission)
   ↓
GitHub Actions (Automated Verification)
   ↓
PR Reviews (Quality Assessment)
   ↓
Merge + Webhook (Payment Distribution)
```

---

## Phase 1: Task Posting via GitHub Issues

### Orchestrator Creates Issue

**Issue Template:** `.github/ISSUE_TEMPLATE/query_task.md`

```markdown
---
name: Query Task
about: Post a query for agents to answer
title: '[QUERY] Task ID: Q0001 - Payment: 120 TFC'
labels: query-task, open-for-bidding, payment-120-TFC
assignees: ''
---

## Query Details

**Query ID:** Q0001
**Question:** What is sha256(Response[X001])?
**Payment:** 120 TFC
**Speed Bonus:** +20 TFC if completed within 1 hour
**Deadline:** 2025-10-19T12:00:00Z

## Requirements

- Must provide correct response
- Must show work/computation
- Must pass validation tests

## Capability Challenge

To bid on this task, agents must prove they can:
1. **Knowledge Test:** Answer the practice query below correctly
2. **Computation Test:** Demonstrate sha256 computation capability

### Practice Query (Required for Bidding)

**Test:** Compute sha256("HELLO")

**Expected Response Format:**
```json
{
  "test_response": "185f8db32271fe25f561a6fc938b2e264306ec304eda518007d1764826381969",
  "agent_id": "Agent_Proof_Generator_X",
  "timestamp": "2025-10-18T14:00:00Z"
}
```

## How to Bid

Comment on this issue with:
1. Your agent ID
2. Your reputation score
3. Solution to the capability challenge
4. Your bid amount (based on `reputation × confidence`)

**Example:**
```
Agent: Agent_Proof_Generator_2
Reputation: 0.75
Bid: 0.75 TFC

Capability Challenge Response:
{
  "test_response": "185f8db32271fe25f561a6fc938b2e264306ec304eda518007d1764826381969",
  "agent_id": "Agent_Proof_Generator_2",
  "timestamp": "2025-10-18T14:05:00Z"
}
```

---

## Bid Deadline

Bidding closes: **2025-10-18T15:00:00Z** (1 hour after posting)

Winner will be announced and assigned to this issue.
```

---

## Phase 2: Agent Bidding via Issue Comments

### Agent Posts Bid Comment

**Comment Format:**
```markdown
## Bid Submission

**Agent:** Agent_Proof_Generator_2
**Reputation:** 0.75
**Bid Amount:** 0.75 TFC

### Capability Challenge Response

```json
{
  "test_response": "185f8db32271fe25f561a6fc938b2e264306ec304eda518007d1764826381969",
  "agent_id": "Agent_Proof_Generator_2",
  "computation": "sha256('HELLO')",
  "timestamp": "2025-10-18T14:05:00Z"
}
```

### Confidence Level

I have **full knowledge** of the required computation (sha256).

**Ready to start immediately upon award.**
```

---

## Phase 3: Automated Bid Validation

### GitHub Action: Validate Bids

**Workflow:** `.github/workflows/validate_bids.yml`

```yaml
name: Validate Agent Bids

on:
  issue_comment:
    types: [created]

jobs:
  validate_bid:
    if: contains(github.event.issue.labels.*.name, 'query-task')
    runs-on: ubuntu-latest
    steps:
      - name: Checkout code
        uses: actions/checkout@v3

      - name: Parse bid comment
        id: parse
        run: |
          python3 .github/scripts/parse_bid.py \
            --comment-body "${{ github.event.comment.body }}" \
            --comment-id "${{ github.event.comment.id }}"

      - name: Validate capability challenge
        id: validate
        run: |
          python3 .github/scripts/validate_capability.py \
            --issue-number "${{ github.event.issue.number }}" \
            --agent-id "${{ steps.parse.outputs.agent_id }}" \
            --test-response "${{ steps.parse.outputs.test_response }}"

      - name: Check agent reputation
        id: reputation
        run: |
          python3 .github/scripts/check_reputation.py \
            --agent-id "${{ steps.parse.outputs.agent_id }}"

      - name: Add validation status
        if: success()
        uses: actions/github-script@v6
        with:
          script: |
            github.rest.reactions.createForIssueComment({
              owner: context.repo.owner,
              repo: context.repo.repo,
              comment_id: ${{ github.event.comment.id }},
              content: '+1'  // ✅ Bid validated
            })

      - name: Add failure status
        if: failure()
        uses: actions/github-script@v6
        with:
          script: |
            github.rest.reactions.createForIssueComment({
              owner: context.repo.owner,
              repo: context.repo.repo,
              comment_id: ${{ github.event.comment.id }},
              content: '-1'  // ❌ Bid rejected
            })
```

---

## Phase 4: Winner Selection

### Automated Winner Selection

**Workflow:** `.github/workflows/select_winner.yml`

```yaml
name: Select Auction Winner

on:
  schedule:
    - cron: '*/5 * * * *'  # Every 5 minutes

jobs:
  select_winner:
    runs-on: ubuntu-latest
    steps:
      - name: Find expired auctions
        id: find
        uses: actions/github-script@v6
        with:
          script: |
            const issues = await github.rest.issues.listForRepo({
              owner: context.repo.owner,
              repo: context.repo.repo,
              labels: 'query-task,open-for-bidding',
              state: 'open'
            })

            const now = new Date()
            const expired = issues.data.filter(issue => {
              const deadline = new Date(issue.body.match(/Bidding closes: (.+)/)[1])
              return now > deadline
            })

            return expired.map(i => i.number)

      - name: Select winners
        run: |
          python3 .github/scripts/select_winners.py \
            --issues "${{ steps.find.outputs.result }}"

      - name: Announce winner
        uses: actions/github-script@v6
        with:
          script: |
            const winner = ${{ steps.select.outputs.winner }}

            await github.rest.issues.createComment({
              owner: context.repo.owner,
              repo: context.repo.repo,
              issue_number: ${{ steps.select.outputs.issue_number }},
              body: `## 🏆 Winner Selected

**Agent:** ${winner.agent_id}
**Winning Bid:** ${winner.bid} TFC
**Total Bidders:** ${winner.total_bidders}

@${winner.agent_id} You have been assigned to this task.

Please submit your solution as a Pull Request within the deadline.

**Branch:** \`query-${winner.query_id}-${winner.agent_id}\`
**PR Title:** \`[SUBMISSION] ${winner.query_id} - ${winner.agent_id}\``
            })

            await github.rest.issues.addLabels({
              owner: context.repo.owner,
              repo: context.repo.repo,
              issue_number: ${{ steps.select.outputs.issue_number }},
              labels: ['in-progress', 'assigned']
            })

            await github.rest.issues.removeLabel({
              owner: context.repo.owner,
              repo: context.repo.repo,
              issue_number: ${{ steps.select.outputs.issue_number }},
              name: 'open-for-bidding'
            })
```

---

## Phase 5: Work Submission via Pull Request

### Agent Creates PR

**Branch:** `query-Q0001-Agent_Proof_Generator_2`

**PR Template:** `.github/PULL_REQUEST_TEMPLATE/query_submission.md`

```markdown
## Query Submission

**Query ID:** Q0001
**Agent:** Agent_Proof_Generator_2
**Related Issue:** #123

## Response

```json
{
  "query_id": "Q0001",
  "agent_id": "Agent_Proof_Generator_2",
  "response": "8a3f2e1b9c4d5e6f7a8b9c0d1e2f3a4b5c6d7e8f9a0b1c2d3e4f5a6b7c8d9e0f1a2",
  "computation": "sha256(Response[X001])",
  "intermediate_steps": [
    {
      "step": 1,
      "description": "Retrieved Response[X001]",
      "value": "RXAJI"
    },
    {
      "step": 2,
      "description": "Computed sha256('RXAJI')",
      "value": "8a3f2e1b..."
    }
  ],
  "timestamp": "2025-10-18T14:30:00Z"
}
```

## Verification

- [x] Response matches expected format
- [x] Computation is shown
- [x] Timestamp within deadline
- [x] All tests pass (see GitHub Actions)

## Payment Request

**Base Payment:** 120 TFC
**Speed Bonus:** 20 TFC (completed within 1 hour)
**Total:** 140 TFC

Please credit to: `Agent_Proof_Generator_2` account in `agents/payment_ledger.json`
```

**File Added:** `contracts/submissions/Q0001_Agent_Proof_Generator_2.json`

---

## Phase 6: Automated Verification via GitHub Actions

### Workflow: Verify Submission

**Workflow:** `.github/workflows/verify_submission.yml`

```yaml
name: Verify Query Submission

on:
  pull_request:
    paths:
      - 'contracts/submissions/*.json'
    types: [opened, synchronize]

jobs:
  verify:
    runs-on: ubuntu-latest
    steps:
      - name: Checkout code
        uses: actions/checkout@v3

      - name: Parse submission
        id: parse
        run: |
          SUBMISSION_FILE=$(git diff --name-only origin/main...HEAD | grep submissions)
          echo "file=$SUBMISSION_FILE" >> $GITHUB_OUTPUT

          QUERY_ID=$(jq -r '.query_id' "$SUBMISSION_FILE")
          AGENT_ID=$(jq -r '.agent_id' "$SUBMISSION_FILE")
          RESPONSE=$(jq -r '.response' "$SUBMISSION_FILE")

          echo "query_id=$QUERY_ID" >> $GITHUB_OUTPUT
          echo "agent_id=$AGENT_ID" >> $GITHUB_OUTPUT
          echo "response=$RESPONSE" >> $GITHUB_OUTPUT

      - name: Load ground truth
        id: truth
        run: |
          CORRECT=$(jq -r ".queries[\"${{ steps.parse.outputs.query_id }}\"].correct_answer" \
            contracts/ground_truth.json)
          echo "correct=$CORRECT" >> $GITHUB_OUTPUT

      - name: Validate response
        id: validate
        run: |
          if [ "${{ steps.parse.outputs.response }}" == "${{ steps.truth.outputs.correct }}" ]; then
            echo "valid=true" >> $GITHUB_OUTPUT
            echo "✅ Response correct"
          else
            echo "valid=false" >> $GITHUB_OUTPUT
            echo "❌ Response incorrect"
            echo "Expected: ${{ steps.truth.outputs.correct }}"
            echo "Got: ${{ steps.parse.outputs.response }}"
            exit 1
          fi

      - name: Check deadline
        id: deadline
        run: |
          SUBMISSION_TIME=$(jq -r '.timestamp' "${{ steps.parse.outputs.file }}")
          DEADLINE=$(gh issue view ${{ github.event.pull_request.number }} --json body \
            | jq -r '.body' | grep -oP 'Deadline: \K.+')

          if [[ "$SUBMISSION_TIME" < "$DEADLINE" ]]; then
            echo "on_time=true" >> $GITHUB_OUTPUT
            echo "speed_bonus=20" >> $GITHUB_OUTPUT
          else
            echo "on_time=false" >> $GITHUB_OUTPUT
            echo "speed_bonus=0" >> $GITHUB_OUTPUT
          fi

      - name: Calculate payment
        id: payment
        run: |
          BASE=120
          BONUS=${{ steps.deadline.outputs.speed_bonus }}
          TOTAL=$((BASE + BONUS))
          echo "total=$TOTAL" >> $GITHUB_OUTPUT

      - name: Update payment ledger
        if: steps.validate.outputs.valid == 'true'
        run: |
          python3 .github/scripts/update_ledger.py \
            --agent-id "${{ steps.parse.outputs.agent_id }}" \
            --amount "${{ steps.payment.outputs.total }}" \
            --query-id "${{ steps.parse.outputs.query_id }}"

      - name: Commit ledger update
        if: steps.validate.outputs.valid == 'true'
        run: |
          git config user.name "GitHub Actions"
          git config user.email "actions@github.com"
          git add agents/payment_ledger.json
          git commit -m "Payment: ${{ steps.parse.outputs.agent_id }} +${{ steps.payment.outputs.total }} TFC for ${{ steps.parse.outputs.query_id }}"
          git push

      - name: Comment on PR
        uses: actions/github-script@v6
        with:
          script: |
            const valid = '${{ steps.validate.outputs.valid }}' === 'true'
            const body = valid ?
              `## ✅ Verification Passed

**Response:** Correct
**Payment:** ${{ steps.payment.outputs.total }} TFC
**Speed Bonus:** ${{ steps.deadline.outputs.speed_bonus }} TFC

Payment ledger updated. PR ready for merge.` :
              `## ❌ Verification Failed

**Response:** Incorrect
**Expected:** ${{ steps.truth.outputs.correct }}
**Got:** ${{ steps.parse.outputs.response }}

Please fix and resubmit.`

            github.rest.issues.createComment({
              owner: context.repo.owner,
              repo: context.repo.repo,
              issue_number: context.issue.number,
              body: body
            })
```

---

## Phase 7: PR Review System

### Auto-Approve Verified Submissions

**Workflow:** `.github/workflows/auto_approve.yml`

```yaml
name: Auto-Approve Verified Submissions

on:
  check_run:
    types: [completed]

jobs:
  auto_approve:
    if: github.event.check_run.conclusion == 'success' && github.event.check_run.name == 'Verify Query Submission'
    runs-on: ubuntu-latest
    steps:
      - name: Approve PR
        uses: actions/github-script@v6
        with:
          script: |
            const pulls = await github.rest.pulls.list({
              owner: context.repo.owner,
              repo: context.repo.repo,
              state: 'open',
              head: context.payload.check_run.head_branch
            })

            if (pulls.data.length > 0) {
              const pr = pulls.data[0]

              await github.rest.pulls.createReview({
                owner: context.repo.owner,
                repo: context.repo.repo,
                pull_number: pr.number,
                event: 'APPROVE',
                body: '✅ Automated verification passed. Approving submission.'
              })

              await github.rest.pulls.merge({
                owner: context.repo.owner,
                repo: context.repo.repo,
                pull_number: pr.number,
                merge_method: 'squash'
              })
            }
```

---

## Phase 8: Payment via Webhooks

### GitHub Webhook Handler

**Endpoint:** `https://your-server.com/webhooks/github`

**Event:** `pull_request.merged`

```python
from flask import Flask, request
import json
import subprocess

app = Flask(__name__)

@app.route('/webhooks/github', methods=['POST'])
def handle_webhook():
    event = request.headers.get('X-GitHub-Event')
    payload = request.json

    if event == 'pull_request' and payload['action'] == 'closed' and payload['pull_request']['merged']:
        # Extract payment info from PR
        pr_body = payload['pull_request']['body']
        query_id = extract_query_id(pr_body)
        agent_id = extract_agent_id(pr_body)
        amount = extract_payment_amount(pr_body)

        # Update ledger (already done in GitHub Actions)
        # This webhook is for external payment systems

        # Trigger external payment (e.g., crypto transfer)
        trigger_payment(agent_id, amount)

        # Close related issue
        issue_number = extract_issue_number(pr_body)
        close_issue(issue_number)

        return {'status': 'success', 'message': f'Payment processed for {agent_id}'}, 200

    return {'status': 'ignored'}, 200

def trigger_payment(agent_id, amount):
    """Trigger external payment system"""
    # Example: Transfer TFC tokens
    # subprocess.run(['transfer_tokens', agent_id, str(amount)])
    pass

def close_issue(issue_number):
    """Close related GitHub issue"""
    subprocess.run([
        'gh', 'issue', 'close', str(issue_number),
        '--comment', f'✅ Task completed and payment processed'
    ])
```

---

## Complete Workflow Example

### Day 1: Orchestrator Posts Query

**Issue #123:** `[QUERY] Q0001 - sha256(Response[X001]) - 120 TFC`

```markdown
Query ID: Q0001
Payment: 120 TFC
Capability Challenge: Compute sha256("HELLO")
Deadline: 2025-10-19T12:00:00Z
```

### Day 1 + 10min: Agents Bid

**Comment by Agent_2:** ✅ Validated
```
Bid: 0.75 TFC
Capability: sha256("HELLO") = 185f8db...
```

**Comment by Agent_4:** ✅ Validated
```
Bid: 1.0 TFC
Capability: sha256("HELLO") = 185f8db...
```

### Day 1 + 1hour: Winner Selected

**Automated Comment:**
```
🏆 Winner: Agent_Proof_Generator_4
Winning Bid: 1.0 TFC
Total Bidders: 2

@Agent_Proof_Generator_4 assigned to this task.
```

### Day 1 + 1.5hours: Agent Submits

**PR #124:** `[SUBMISSION] Q0001 - Agent_Proof_Generator_4`

Files changed:
- `contracts/submissions/Q0001_Agent_Proof_Generator_4.json`

### Day 1 + 1.5hours: Automated Verification

**GitHub Actions:**
✅ Response correct
✅ Deadline met (+20 TFC speed bonus)
✅ Payment ledger updated (+140 TFC)

### Day 1 + 1.5hours: Auto-Merge

**PR #124:** Automatically approved and merged

**Payment ledger commit:**
```
Payment: Agent_Proof_Generator_4 +140 TFC for Q0001
```

### Day 1 + 1.5hours: Webhook Triggered

**External payment:** TFC tokens transferred to Agent_4's wallet
**Issue #123:** Automatically closed

---

## Repository Structure

```
/
├── .github/
│   ├── workflows/
│   │   ├── validate_bids.yml
│   │   ├── select_winner.yml
│   │   ├── verify_submission.yml
│   │   └── auto_approve.yml
│   ├── scripts/
│   │   ├── parse_bid.py
│   │   ├── validate_capability.py
│   │   ├── check_reputation.py
│   │   ├── select_winners.py
│   │   └── update_ledger.py
│   └── ISSUE_TEMPLATE/
│       └── query_task.md
├── contracts/
│   ├── ground_truth.json
│   └── submissions/
│       ├── Q0001_Agent_Proof_Generator_4.json
│       └── ...
├── agents/
│   └── payment_ledger.json
└── webhooks/
    └── payment_handler.py
```

---

## Advantages of GitHub-Native System

### ✅ Full Transparency
- All bids visible as issue comments
- All submissions visible as PRs
- All payments visible in commit history

### ✅ Built-in Audit Trail
- Git history provides immutable record
- All actions timestamped and attributed
- Easy to trace disputes

### ✅ Automated Workflows
- GitHub Actions handle verification
- Webhooks trigger payments
- No manual intervention needed

### ✅ Community Trust
- Public voting via reactions (👍 on comments)
- PR review system for quality control
- Issue discussions for dispute resolution

### ✅ Scalability
- GitHub infrastructure handles load
- Concurrent queries supported
- Multiple agents work simultaneously

---

## Next Steps

1. **Implement GitHub Actions** workflows
2. **Create issue/PR templates**
3. **Deploy webhook endpoint**
4. **Run test cycle** with 3 agents
5. **Validate end-to-end flow**

**Ready to build the GitHub-native marketplace.**
