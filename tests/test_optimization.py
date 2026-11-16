import json

import pytest

from eval.reference import decide_order
from question1.agent import SupportCopilot
from question2.agent import SupportPipeline


@pytest.mark.parametrize("ptype", ["physical", "digital", "custom", "subscription"])
@pytest.mark.parametrize("days", [0, 7, 8, 30, 31, 38])
def test_policy_retrieval_covers_boundary_orders(ptype, days):
    # This checks retrieval recall across combinations beyond the five fixtures.
    # It does not claim real-model accuracy: the supplied client uses this oracle.
    pipe = SupportPipeline()
    for opened in [False, True]:
        for damage in [False, True]:
            for customized in [False, True]:
                for revealed in [False, True]:
                    order = dict(
                        product_type=ptype, delivered_days_ago=days,
                        subscription_age_days=days, opened=opened,
                        damage_reported=damage, customized=customized,
                        license_revealed=revealed,
                    )
                    assert decide_order(order).kb_article in pipe._triage(order)


def test_subscription_pipeline():
    got = SupportPipeline().handle_ticket("T-1091")
    assert (got.action, got.kb_article) == ("SEND_ARTICLE", "subscription-cooling-off")


@pytest.mark.parametrize("draft", [
    "no JSON",
    '{"action":"DELETE_ORDER","kb_article":"returns-within-30-days"}',
    '{"action":"REFUND","kb_article":"invented-policy"}',
    '{"kb_article":"returns-within-30-days"}',
])
def test_audit_rejects_invalid_output(draft):
    with pytest.raises((ValueError, KeyError)):
        SupportPipeline()._audit(draft, ("returns-within-30-days",))


def test_q1_stable_policy_prefix_and_compact_snapshot():
    copilot = SupportCopilot()
    first = copilot.build_messages("T-1001")
    second = copilot.build_messages("T-1002")
    assert first[0].content == second[0].content
    snapshot = first[1].content.split("ORDER_SNAPSHOT:\n")[1].split("\nEND_SNAPSHOT")[0]
    assert "\n" not in snapshot
    assert json.loads(snapshot)["product_type"] == "physical"
