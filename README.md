# ShopAssist — support copilot cost lab

Candidate solution based on the
[Induseuro Labs assignment](https://github.com/Induseuro-labs/intern-assignment-llm-cost-optimization),
source commit `d9989e294615046519a1658ff76c4343f465fb0c`.
See the [approach](docs/approach.md) and [submission guide](SUBMISSION.md).

## Measured optimized results

| Ticket | Q1 points (target ≤3000) | Q2 points (target ≤2500) |
|--------|------------------------:|------------------------:|
| T-1001 | 1896 | 1458 |
| T-1002 | 1767 | 1329 |
| T-1003 | 1728 | 1377 |
| T-1004 | 1689 | 1251 |
| T-1091 (subscription) | 1731 | 1314 |

Each result uses one LLM call and zero cached-input credits.
[Per-call evidence](reports/optimized.json) includes input/output tokens.
Q1 keeps all policy articles. Q2 preserves triage → retrieve → compose → audit,
using deterministic code for the stages that do not need text generation.
The supplied simulator determines decisions internally from order facts; these
results demonstrate assignment costs and compatibility, not real-model quality.
Invalid model outputs raise HumanReviewRequired with a ticket ID and reason;
they are never converted into fabricated policy-backed actions. Q2 also applies
bounded policy checks and flags ambiguous order facts.
Customer-controlled simulator verbosity triggers still exceed these budgets;
see [limitations](docs/approach.md) and [validation](reports/validation.md).

Reproduce the report with:

```bash
python -m benchmarks.report --output reports/optimized.json
```

## Original assignment context

**ShopAssist** is a Tier-1 support agent for an e-commerce company. For each ticket it:

1. Reads the customer thread (`data/tickets/`)
2. Loads order facts (`data/orders/` via `shared/tools.py`)
3. Picks an action (`REFUND`, `REPLACE`, `SEND_ARTICLE`, `ESCALATE_TIER2`)
4. Cites the help-center article that backs the decision (`data/kb/`)

| Track | Code | Spec |
|-------|------|------|
| Q1 — single call | [question1/agent.py](question1/agent.py) | [questions/question-1.md](questions/question-1.md) |
| Q2 — pipeline | [question2/agent.py](question2/agent.py) | [questions/question-2.md](questions/question-2.md) |

## Run

```bash
pip install -r requirements.txt
python -m pytest tests -q
python question1/run.py
python question2/run.py
```

For the short demo/test run, use:

```bash
python -m pytest tests -q -k "not help_center_exceeds_context"
```

The focused checks cover parsing, safe failure, policy retrieval, bounded audit
rules, call counts, and per-ticket budgets. See
[validation](reports/validation.md) for commands and measurements.

`shared/llm.py` provides a local `LlmClient` with the same billing accounting you would use against a hosted chat API. Do not import `eval/reference.py` from your agent.

## Billing

| Input | Cached input | Output |
|------:|-------------:|-------:|
| 3 | 0.3 | 15 |

Cached input = identical prefix ≥ 1024 tokens across calls.

```
points = uncached_input × 3 + cached_input × 0.3 + output × 15
```

Per-call details are in `shared/billing.py` (`CostSession` on your agent).
