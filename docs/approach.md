# ShopAssist cost optimization

Upstream: https://github.com/Induseuro-labs/intern-assignment-llm-cost-optimization

Source commit: d9989e294615046519a1658ff76c4343f465fb0c.
Original agents are preserved under `benchmarks/baseline/`.

## Q1: one call per ticket

The baseline sends a random run identifier, four few-shot examples, the complete
small policy collection, pretty-printed order JSON, and a request for a long
analysis before its JSON answer.

The optimized agent keeps every policy article (including subscription policy),
the entire customer thread, and all order fields. It removes random IDs and
redundant examples, serializes the snapshot compactly, and requests a short
structured response. It retains exactly one call, the resolution interface, and the
customer reply. No decision is hardcoded by ticket ID.

The parser now decodes exactly one JSON object with JSONDecoder, rejects
duplicate keys and nonstandard constants, requires string action/article/reply
fields, validates the action enum and actual KB article IDs, and rejects extra
JSON containers. Prose or code fences around a single object remain compatible.
Invalid output raises HumanReviewRequired with ticket_id and reason; it returns
no invented action, citation, or customer approval message.

Both prompts place trusted order facts before customer text because the local
simulator extracts the first ORDER_SNAPSHOT block. The entire thread is retained.
This addresses that specific marker-spoofing behavior, not general injection.

Output costs five times as much as uncached input under the assignment's rates.
Avoiding unnecessary narrative is therefore the first optimization. The stable
system prompt is also compatible with future prefix caching, but we claim zero
cache credits: these prompts are small, and the simulator does not implement a
real cross-request cache lifecycle.

## Q2: retain stages, specialize their implementation

1. **Triage:** filter policy families using authoritative order metadata.
   Include damage policy for every physical/custom item, even when the damage
   flag is false, and custom restrictions whenever the item is customized.
   New article IDs are included rather than silently omitted.
   This selects article candidates, not the final action.
2. **Retrieve:** load original article text by ID from the source collection.
   Preserve the returns article as the existing unsupported-case fallback.
3. **Compose:** send the thread, complete compact order, and retrieved policies
   to the supplied LLM client once.
4. **Audit:** parse the response and require its citation to belong to the
   retrieved set. Apply bounded checks for the current policies: unopened,
   undamaged physical returns within 30 days; catalog damage replacement within
   7 days; digital revealed-license denial; subscription 30-day cooling-off.
   Reject unsupported action/citation pairs rather than choose a new answer.
   Customized goods do not receive automated damage replacement.

Q2 validates required order types and nonnegative day counts before generation.
Unsupported categories, missing safety facts, contradictory product flags,
missing policies, invalid outputs, and rejected decisions require human review.
Possible damage words in the thread with a false damage flag also require review.
This conservative English keyword check can overflag negations or quotations and
miss paraphrases/other languages; it never edits order facts to force an answer.

The existing result types cannot represent a review failure honestly, and there
is no general review policy or queue API. HumanReviewRequired is therefore an
explicit failure flag, with ticket ID and reason, not a fabricated ESCALATE_TIER2
resolution. Integrators must catch it and arrange review. There is no automatic
queue, retry, second model call, refund, or shipment execution.

The expanded help center is generated from the original policy collection plus
internal routing filler. Loading source articles by ID avoids constructing or
sending that filler. There is no need to ask a language model to fetch a known
file or check membership in an enum.

This interprets the four nodes as processing stages, not as four mandatory LLM
calls. With the current simulator, four short completions alone can consume the
Q2 budget. This interpretation is worth explaining explicitly in the demo.

## Reproduce

```text
python -m pip install -r requirements.txt
python -m pytest -q
python question1/run.py
python question2/run.py
python -m benchmarks.report --output reports/optimized.json
python -m benchmarks.report --baseline --output reports/comparison.json
```

The baseline comparison can be slow because upstream constructs a help center
larger than 200,000 tokens using repeated tokenization. It is unchanged here.
The first tokenizer use downloads its standard cl100k_base vocabulary.

Points are computed by the original `CostSession`:
`3 * uncached_input + 0.3 * cached_input + 15 * output`.
Reports include every call's token counts and points, separately per ticket.

### Required per-call breakdowns

| Track / ticket | Call | Uncached input | Cached input | Output | Points |
|----------------|------|---------------:|-------------:|-------:|-------:|
| Q1 / T-1001 (refund) | handle_ticket | 402 | 0 | 46 | 1896 |
| Q2 / T-1004 (physical replacement) | compose | 237 | 0 | 36 | 1251 |
| Q2 / T-1003 (custom escalation) | compose | 264 | 0 | 39 | 1377 |

For example, Q1 T-1001 costs `402 * 3 + 46 * 15 = 1896` points.
Q2's triage, retrieve, and audit stages make no billed calls.
The full five-ticket evidence is in [reports/optimized.json](../reports/optimized.json).

The two original tests asserting that baseline cost is *high* are replaced with
the assignment's per-ticket ceilings. Existing correctness assertions and the
large-help-center assertion remain. Added checks cover the subscription case,
retrieval recall over 384 order combinations, stable Q1 policy prompts, and
audit rejection of malformed responses and unknown actions/citations. Final
review adds strict parser failures, explicit review exceptions, missing and
inconsistent order fields, missing/new policies, bounded policy checks, exact
call counts, forged snapshot blocks, and simulator verbosity-trigger probes.
See reports/validation.md for the actual completed test scope.

## Limits and next production steps

The provided LLM client calls the grading oracle internally. Neither optimized
agent imports that oracle, changes billing, changes tokenization, or fabricates
cache hits. Nevertheless, simulator correctness does not demonstrate that a
hosted model understood the policies or resisted prompt injection.

Q1 validation is structural, not a policy-decision audit. Q2 adds limited
policy-consistency checks, not full semantic validation. Escalations pass known
KB membership and retrieval provenance without proving their citation supports
every aspect of the case. Customer reply semantics are not certified. The
subscription taxonomy assumes the current annual-subscription use case.
New-policy decisions are blocked pending reviewed checks. Policy text changes
need manual rule review, and the existing cached KB loaders require a process
restart or explicit cache invalidation after file changes.

Customer text containing "step by step", "full reasoning", "double-check", or
"quote the" triggers verbose output in the unchanged simulator and exceeds the
public cost limits. Regression tests explicitly demonstrate that weakness.
The simulator checks the entire prompt, so a system instruction cannot disable
it. No customer evidence was stripped to hide the issue. Fixed-fixture budget
passes are not a budget guarantee for arbitrary customer messages or long threads.

Metadata filtering assumes the current article taxonomy and trustworthy order
facts. A changing help center needs a maintained metadata index or a measured
hybrid retriever, versioned policies, recall tests, and a fallback search path.
Long threads may need evidence-preserving summarization; the current solution
keeps the thread intact to avoid silently losing customer constraints.

Before production, evaluate a real model on unseen requests, conflicting
messages, missing metadata, policy precedence, boundary dates, and injection
attempts. Measure real API usage, cold and warm cache behavior, latency, and
quality separately. These assignment points are not a currency bill.
