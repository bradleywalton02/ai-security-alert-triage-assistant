import pytest

from triage import demo_triage, find_alert, validate_alert

VALID_ALERT = {
    "alert_id": "TEST-1",
    "timestamp": "2026-09-25T14:22:31Z",
    "source": "EDR",
    "severity": "high",
    "title": "Test alert",
    "description": "Synthetic test event.",
    "confidence": 0.8,
}


def test_validate_alert_accepts_valid_alert():
    validate_alert(VALID_ALERT)


def test_validate_alert_rejects_missing_fields():
    broken = dict(VALID_ALERT)
    broken.pop("title")
    with pytest.raises(ValueError):
        validate_alert(broken)


def test_validate_alert_rejects_unknown_severity():
    broken = dict(VALID_ALERT)
    broken["severity"] = "super-high"
    with pytest.raises(ValueError):
        validate_alert(broken)


def test_demo_triage_maps_high_to_p2():
    result = demo_triage(VALID_ALERT)
    assert result["recommended_priority"] == "P2"
    assert result["human_review_required"] is True
    assert result["mode"] == "local_demo_non_ai"


def test_find_alert():
    assert find_alert([VALID_ALERT], "TEST-1")["alert_id"] == "TEST-1"
