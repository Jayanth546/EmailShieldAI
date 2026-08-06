from app.analyzers.header_analyzer import HeaderAnalyzer


def test_valid_email():
    analyzer = HeaderAnalyzer()

    email = {
        "from": "alice@example.com",
        "reply_to": "alice@example.com",
        "message_id": "<123@example.com>",
    }

    result = analyzer.analyze(email)

    assert result["score"] == 0
    assert result["issues"] == []


def test_missing_from():
    analyzer = HeaderAnalyzer()

    email = {
        "from": None,
        "reply_to": None,
        "message_id": "<123@example.com>",
    }

    result = analyzer.analyze(email)

    assert "Missing From header" in result["issues"]
    assert result["score"] == 10


def test_missing_message_id():
    analyzer = HeaderAnalyzer()

    email = {
        "from": "alice@example.com",
        "reply_to": "alice@example.com",
        "message_id": None,
    }

    result = analyzer.analyze(email)

    assert "Missing Message-ID" in result["issues"]
    assert result["score"] == 10


def test_reply_to_mismatch():
    analyzer = HeaderAnalyzer()

    email = {
        "from": "paypal@example.com",
        "reply_to": "attacker@gmail.com",
        "message_id": "<123@example.com>",
    }

    result = analyzer.analyze(email)

    assert "Reply-To differs from From" in result["issues"]
    assert result["score"] == 10


def test_multiple_issues():
    analyzer = HeaderAnalyzer()

    email = {
        "from": None,
        "reply_to": "attacker@gmail.com",
        "message_id": None,
    }

    result = analyzer.analyze(email)

    assert len(result["issues"]) == 3
    assert result["score"] == 30
