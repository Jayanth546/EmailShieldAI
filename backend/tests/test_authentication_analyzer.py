from app.analyzers.authentication_analyzer import AuthenticationAnalyzer


def test_valid_authentication():
    analyzer = AuthenticationAnalyzer()

    email = {
        "received_spf": "pass",
        "dkim_signature": "v=1;",
        "authentication_results":
            "spf=pass dkim=pass dmarc=pass"
    }

    result = analyzer.analyze(email)

    assert result["score"] == 0
    assert result["issues"] == []


def test_missing_spf():
    analyzer = AuthenticationAnalyzer()

    email = {
        "received_spf": None,
        "dkim_signature": "v=1;",
        "authentication_results": None,
    }

    result = analyzer.analyze(email)

    assert result["score"] == 15
    assert "SPF header missing" in result["issues"]


def test_missing_dkim():
    analyzer = AuthenticationAnalyzer()

    email = {
        "received_spf": "pass",
        "dkim_signature": None,
        "authentication_results": None,
    }

    result = analyzer.analyze(email)

    assert result["score"] == 15
    assert "DKIM signature missing" in result["issues"]


def test_spf_fail():
    analyzer = AuthenticationAnalyzer()

    email = {
        "received_spf": "fail",
        "dkim_signature": "v=1;",
        "authentication_results":
            "spf=fail dkim=pass dmarc=pass",
    }

    result = analyzer.analyze(email)

    assert result["score"] >= 60


def test_dkim_fail():
    analyzer = AuthenticationAnalyzer()

    email = {
        "received_spf": "pass",
        "dkim_signature": "v=1;",
        "authentication_results":
            "spf=pass dkim=fail dmarc=pass",
    }

    result = analyzer.analyze(email)

    assert result["score"] >= 30


def test_dmarc_fail():
    analyzer = AuthenticationAnalyzer()

    email = {
        "received_spf": "pass",
        "dkim_signature": "v=1;",
        "authentication_results":
            "spf=pass dkim=pass dmarc=fail",
    }

    result = analyzer.analyze(email)

    assert result["score"] >= 40
