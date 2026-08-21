import pytest

from factory.metrics import GoodhartViolation, MetricSet


def test_activity_without_outcome_is_refused():
    m = MetricSet("x")
    with pytest.raises(GoodhartViolation):
        m.activity("escalations", paired_with="fixes_applied")


def test_the_retired_agent_signature_is_flagged():
    m = MetricSet("pipeline-agent")
    m.outcome("fixes_applied")
    m.activity("escalations", paired_with="fixes_applied")
    m.get("escalations").bump(234)
    assert m.suspicious(), "234 escalations against 0 fixes must be flagged"


def test_healthy_pair_is_quiet():
    m = MetricSet("ok")
    m.outcome("connectors_green")
    m.activity("runs", paired_with="connectors_green")
    m.get("runs").bump(10)
    m.get("connectors_green").bump(1)
    assert not m.suspicious()
