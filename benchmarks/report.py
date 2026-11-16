"""Reproduce per-call baseline and optimized costs with the unchanged client."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from eval.reference import TICKET_EXPECTATIONS

from benchmarks.baseline.q1 import SupportCopilot as BaselineCopilot
from benchmarks.baseline.q2 import SupportPipeline as BaselinePipeline
from question1.agent import SupportCopilot
from question2.agent import SupportPipeline

TICKETS = ["T-1001", "T-1002", "T-1003", "T-1004", "T-1091"]


def measure(agent_type, cost_limit=None):
    # Reuse an agent as in the supplied runners, but never claim cache credits.
    agent = agent_type()
    rows = []
    for tid in TICKETS:
        before = len(agent.session.calls)
        result = agent.handle_ticket(tid)
        calls = agent.session.calls[before:]
        expected = TICKET_EXPECTATIONS[tid]
        points = sum(c.points() for c in calls)
        rows.append({
            "ticket_id": tid,
            "expected_action": expected.action,
            "action": result.action,
            "expected_kb_article": expected.kb_article,
            "kb_article": result.kb_article,
            "correct": (result.action, result.kb_article) == (expected.action, expected.kb_article),
            "input_tokens": sum(c.input_tokens for c in calls),
            "output_tokens": sum(c.output_tokens for c in calls),
            "cached_input_tokens": sum(c.cached_prefix_tokens for c in calls),
            "points": points,
            "llm_calls": len(calls),
            "cost_limit": cost_limit,
            "within_cost_limit": None if cost_limit is None else points <= cost_limit,
            "calls": [{
                "label": c.label,
                "input_tokens": c.input_tokens,
                "cached_input_tokens": c.cached_prefix_tokens,
                "output_tokens": c.output_tokens,
                "points": c.points(),
            } for c in calls],
        })
    return rows


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--baseline", action="store_true")
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    report = {
        "upstream_commit": "d9989e294615046519a1658ff76c4343f465fb0c",
        "billing": {"input": 3, "cached_input": 0.3, "output": 15},
        "optimized": {"q1": measure(SupportCopilot, 3000), "q2": measure(SupportPipeline, 2500)},
    }
    if args.baseline:
        report["baseline"] = {
            "q1": measure(BaselineCopilot), "q2": measure(BaselinePipeline),
        }
    payload = json.dumps(report, indent=2) + "\n"
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(payload, encoding="utf-8")
    print(payload)


if __name__ == "__main__":
    main()
