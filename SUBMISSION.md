# Submission guide

- [Approach and limitations](docs/approach.md)
- [Q1 agent](question1/agent.py)
- [Q2 agent](question2/agent.py)
- [Cost reporting command](benchmarks/report.py)

Run `python -m pytest tests -q`, then
`python -m benchmarks.report --output reports/optimized.json`.
For the original-agent comparison, add `--baseline`.

The hiring assignment is from Induseuro Labs; this repository contains a
candidate solution based on its starter code, not an official company product.
