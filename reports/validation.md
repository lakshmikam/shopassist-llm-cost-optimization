# Local validation — 15 November 2026

- Python 3.11; pytest 9.0.2; tiktoken 0.12.0.
- 126 focused solution checks passed.
- Both supplied runners completed successfully: Q1 total 7080 points and Q2
  total 5415 points across the four public tickets.
- The optimized report was generated with the original tokenizer and billing.
- Python compilation checks passed.
- Strict parser tests cover malformed/ambiguous JSON, duplicate keys, missing
  fields, wrong types, unsupported actions, unknown articles, and safe prose.
- Review-exception tests establish that invalid output returns no action,
  citation, or customer reply and causes no second model call.
- Q2 regressions cover missing/inconsistent order fields, missing/new policies,
  damage-policy recall, thread conflicts, bounded policy mismatches and dates.
- Both tracks have exact one-call and zero-cache checks for all five fixtures,
  plus forged-snapshot marker tests. Invalid Q2 preflight facts/policies can fail
  safely before any model call; one-call claims refer to valid measured tickets.
- Eight customer-verbosity probes demonstrate the unchanged simulator weakness,
  not a mitigation. All retain original customer text, use one call and zero
  cached tokens, emit at least 480 output tokens, and exceed their track's limit.
  One fresh final-code probe measured Q1 8481–8553 points and Q2 8055–8160 points.
  Verbose UUIDs vary, so these probe numbers are examples, not fixed expectations.
- The current report includes expected/actual fields, correctness, aggregate
  tokens, call counts, per-call costs, and per-ticket budget verdicts. The original
  grading oracle is used only by the simulator/tests/benchmark, not by agents.

Commands for the completed solution checks (PowerShell):

```powershell
$env:TIKTOKEN_CACHE_DIR = Join-Path (Get-Location) '.cache/tiktoken'
$env:PYTEST_DISABLE_PLUGIN_AUTOLOAD = '1'
python -m pytest -q -k 'not help_center_exceeds_context'
python question1/run.py
python question2/run.py
python -m benchmarks.report --output reports/optimized.json
```

The cache environment variable points to a local downloaded tokenizer
vocabulary. It does not change token counts. Third-party pytest plugin autoload
was disabled to keep unrelated installed packages out of this test run.

The final public-ticket measurements are:

| Track | Ticket | Input | Output | Cached | Calls | Points | Limit | Pass |
|-------|--------|------:|-------:|-------:|------:|-------:|------:|------|
| Q1 | T-1001 | 402 | 46 | 0 | 1 | 1896 | 3000 | yes |
| Q1 | T-1002 | 394 | 39 | 0 | 1 | 1767 | 3000 | yes |
| Q1 | T-1003 | 381 | 39 | 0 | 1 | 1728 | 3000 | yes |
| Q1 | T-1004 | 383 | 36 | 0 | 1 | 1689 | 3000 | yes |
| Q2 | T-1001 | 256 | 46 | 0 | 1 | 1458 | 2500 | yes |
| Q2 | T-1002 | 248 | 39 | 0 | 1 | 1329 | 2500 | yes |
| Q2 | T-1003 | 264 | 39 | 0 | 1 | 1377 | 2500 | yes |
| Q2 | T-1004 | 237 | 36 | 0 | 1 | 1251 | 2500 | yes |

All expected/actual action and article pairs match. The subscription fixture
also matches: Q1 1731 points, Q2 1314 points, one call and zero cache each.
Read reports/optimized.json for the expected/actual strings and call details.
