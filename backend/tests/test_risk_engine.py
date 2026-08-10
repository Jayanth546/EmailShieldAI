from app.services.risk_engine import RiskEngine


def make_result(score):
    return {"score": score}


def test_risk_engine_without_ml():
    engine = RiskEngine()

    result = engine.analyze(
        make_result(5),   # header
        make_result(5),   # url
        make_result(5),   # body
        make_result(5),   # attachment
        make_result(5),   # authentication
    )

    assert result["rule_based_score"] == 25
    assert result["spam_score"] == 0
    assert result["total_score"] == 25
    assert result["verdict"] == "SAFE"


def test_risk_engine_with_ml_spam():
    engine = RiskEngine()

    spam_result = {
        "label": "spam",
        "spam_probability": 0.90,
        "ham_probability": 0.10,
    }

    result = engine.analyze(
        make_result(10),
        make_result(0),
        make_result(0),
        make_result(0),
        make_result(0),
        spam_result,
    )

    assert result["rule_based_score"] == 10
    assert result["spam_score"] == 36
    assert result["total_score"] == 46
    assert result["verdict"] == "SUSPICIOUS"


def test_risk_engine_ml_zero_probability():
    engine = RiskEngine()

    spam_result = {
        "label": "ham",
        "spam_probability": 0.0,
        "ham_probability": 1.0,
    }

    result = engine.analyze(
        make_result(0),
        make_result(0),
        make_result(0),
        make_result(0),
        make_result(0),
        spam_result,
    )

    assert result["spam_score"] == 0
    assert result["total_score"] == 0
    assert result["verdict"] == "SAFE"


def test_risk_engine_ml_full_probability():
    engine = RiskEngine()

    spam_result = {
        "label": "spam",
        "spam_probability": 1.0,
        "ham_probability": 0.0,
    }

    result = engine.analyze(
        make_result(0),
        make_result(0),
        make_result(0),
        make_result(0),
        make_result(0),
        spam_result,
    )

    assert result["spam_score"] == 40
    assert result["total_score"] == 40
    assert result["verdict"] == "SUSPICIOUS"


def test_risk_score_is_capped_at_100():
    engine = RiskEngine()

    spam_result = {
        "label": "spam",
        "spam_probability": 1.0,
        "ham_probability": 0.0,
    }

    result = engine.analyze(
        make_result(50),
        make_result(50),
        make_result(50),
        make_result(50),
        make_result(50),
        spam_result,
    )

    assert result["rule_based_score"] == 250
    assert result["spam_score"] == 40
    assert result["total_score"] == 100
    assert result["total_score"] <= 100
    assert result["verdict"] == "PHISHING"
