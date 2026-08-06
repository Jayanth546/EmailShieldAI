from app.analyzers.body_analyzer import BodyAnalyzer


def test_safe_email():
    analyzer = BodyAnalyzer()

    result = analyzer.analyze("""
    Hello John,

    Thank you for attending today's meeting.

    Regards,
    Alice
    """)

    assert result["score"] == 0
    assert result["issues"] == []


def test_single_keyword():
    analyzer = BodyAnalyzer()

    result = analyzer.analyze("""
    Please verify your account.
    """)

    assert result["score"] == 20
    assert len(result["issues"]) == 2


def test_multiple_keywords():
    analyzer = BodyAnalyzer()

    result = analyzer.analyze("""
    URGENT!

    Click here to verify your password.

    Your account has a security alert.
    """)

    assert result["score"] == 60
    assert len(result["issues"]) == 6


def test_generic_greeting():
    analyzer = BodyAnalyzer()

    result = analyzer.analyze("""
    Dear Customer,

    Welcome to our service.
    """)

    assert result["score"] == 15
    assert any(
        "Generic greeting detected" in issue
        for issue in result["issues"]
    )


def test_personal_greeting():
    analyzer = BodyAnalyzer()

    result = analyzer.analyze("""
    Dear Jayanth,

    Welcome to our service.
    """)

    assert result["score"] == 0
    assert result["issues"] == []
