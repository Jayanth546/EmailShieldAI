from app.services.risk_engine import RiskEngine


def test_safe_email():
    engine = RiskEngine()

    result = engine.analyze(
        {"score": 0},
        {"score": 0},
        {"score": 0},
        {"score": 0},
        {"score": 0},
    )

    assert result["total_score"] == 0
    assert result["verdict"] == "SAFE"


def test_suspicious_email():
    engine = RiskEngine()

    result = engine.analyze(
        {"score": 10},
        {"score": 10},
        {"score": 10},
        {"score": 5},
        {"score": 5},
    )

    assert result["total_score"] == 40
    assert result["verdict"] == "SUSPICIOUS"


def test_phishing_email():
    engine = RiskEngine()

    result = engine.analyze(
        {"score": 20},
        {"score": 25},
        {"score": 20},
        {"score": 15},
        {"score": 20},
    )

    assert result["total_score"] == 100
    assert result["verdict"] == "PHISHING"


def test_boundary_safe():
    engine = RiskEngine()

    result = engine.analyze(
        {"score": 5},
        {"score": 5},
        {"score": 5},
        {"score": 5},
        {"score": 5},
    )

    assert result["total_score"] == 25
    assert result["verdict"] == "SAFE"


def test_boundary_suspicious():
    engine = RiskEngine()

    result = engine.analyze(
        {"score": 10},
        {"score": 5},
        {"score": 5},
        {"score": 5},
        {"score": 5},
    )

    assert result["total_score"] == 30
    assert result["verdict"] == "SUSPICIOUS"


def test_boundary_phishing():
    engine = RiskEngine()

    result = engine.analyze(
        {"score": 20},
        {"score": 20},
        {"score": 10},
        {"score": 10},
        {"score": 10},
    )

    assert result["total_score"] == 70
    assert result["verdict"] == "PHISHING"
