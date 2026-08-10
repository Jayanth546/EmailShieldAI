from app.services.email_analysis_service import EmailAnalysisService


def test_safe_email():
    service = EmailAnalysisService()

    parsed_email = {
        "from": "alice@example.com",
        "message_id": "<123@example.com>",
        "reply_to": None,
        "authentication_results": "spf=pass dkim=pass dmarc=pass",
        "received_spf": "pass",
        "dkim_signature": "v=1;",
        "body": """
Hello John,

Thank you for your email.

Regards,
Alice
""",
        "urls": ["https://openai.com"],
        "attachments": [],
    }

    result = service.analyze(parsed_email)

    assert result["risk_level"] == "Safe"
    assert result["total_score"] < 30

    # ML result must be present.
    assert "spam" in result
    assert 0.0 <= result["spam"]["spam_probability"] <= 1.0
    assert 0.0 <= result["spam"]["ham_probability"] <= 1.0

    # Risk result must contain explanations.
    assert "risk" in result
    assert "reasons" in result["risk"]


def test_suspicious_email():
    service = EmailAnalysisService()

    parsed_email = {
        "from": "",
        "message_id": None,
        "reply_to": "attacker@gmail.com",
        "authentication_results": "spf=fail dkim=pass dmarc=pass",
        "received_spf": "fail",
        "dkim_signature": "v=1;",
        "body": """
Dear Customer,

Verify your account immediately.
Click here now.
""",
        "urls": ["http://bit.ly/login"],
        "attachments": ["invoice.zip"],
    }

    result = service.analyze(parsed_email)

    assert result["risk_level"] in [
        "Suspicious",
        "Phishing",
    ]

    assert result["total_score"] >= 30

    # Semantic body findings should survive the complete pipeline.
    semantic_findings = result["body"].get(
        "semantic_findings",
        []
    )

    categories = {
        finding["category"]
        for finding in semantic_findings
    }

    assert "urgency" in categories
    assert "call_to_action" in categories


def test_phishing_email():
    service = EmailAnalysisService()

    parsed_email = {
        "from": "",
        "message_id": None,
        "reply_to": "hacker@gmail.com",
        "authentication_results": (
            "spf=fail dkim=fail dmarc=fail"
        ),
        "received_spf": "fail",
        "dkim_signature": None,
        "body": """
URGENT!

Verify your password immediately.

Click here.

Security alert.
""",
        "urls": ["http://192.168.1.1/login.zip"],
        "attachments": [
            "invoice.pdf.exe",
            "macro.docm",
        ],
    }

    result = service.analyze(parsed_email)

    assert result["risk_level"] == "Phishing"
    assert result["total_score"] >= 70

    # ML prediction must be included.
    assert result["spam"]["label"] in [
        "spam",
        "ham",
    ]

    # Risk engine must contain reasons.
    reasons = result["risk"]["reasons"]

    assert len(reasons) > 0

    categories = {
        reason["category"]
        for reason in reasons
    }

    assert "body" in categories
    assert "url" in categories
    assert "attachment" in categories
    assert "authentication" in categories


def test_spam_email_contains_ml_and_semantic_evidence():
    service = EmailAnalysisService()

    parsed_email = {
        "from": "unknown@example.com",
        "message_id": "<spam@example.com>",
        "reply_to": None,
        "authentication_results": "",
        "received_spf": "",
        "dkim_signature": None,
        "body": """
Congratulations! You won $5000.
Click here immediately to claim your reward.
""",
        "urls": [],
        "attachments": [],
    }

    result = service.analyze(parsed_email)

    # ML prediction must be present.
    spam_result = result["spam"]

    assert "label" in spam_result
    assert "spam_probability" in spam_result
    assert "ham_probability" in spam_result

    assert 0.0 <= spam_result["spam_probability"] <= 1.0
    assert 0.0 <= spam_result["ham_probability"] <= 1.0

    # Semantic analysis must be present.
    semantic_findings = result["body"]["semantic_findings"]

    categories = {
        finding["category"]
        for finding in semantic_findings
    }

    assert "urgency" in categories
    assert "financial_reward" in categories
    assert "call_to_action" in categories

    # The risk engine must incorporate ML scoring.
    assert result["risk"]["spam_score"] >= 0
    assert result["total_score"] >= result["risk"]["spam_score"]


def test_normal_email_has_no_semantic_findings():
    service = EmailAnalysisService()

    parsed_email = {
        "from": "alice@example.com",
        "message_id": "<normal@example.com>",
        "reply_to": None,
        "authentication_results": (
            "spf=pass dkim=pass dmarc=pass"
        ),
        "received_spf": "pass",
        "dkim_signature": "v=1;",
        "body": """
Hello John,

The project meeting is scheduled for tomorrow.

Regards,
Alice.
""",
        "urls": [],
        "attachments": [],
    }

    result = service.analyze(parsed_email)

    assert result["risk_level"] == "Safe"

    assert result["body"].get(
        "semantic_findings",
        []
    ) == []


def test_analysis_result_has_complete_structure():
    service = EmailAnalysisService()

    parsed_email = {
        "from": "alice@example.com",
        "message_id": "<structure@example.com>",
        "reply_to": None,
        "authentication_results": (
            "spf=pass dkim=pass dmarc=pass"
        ),
        "received_spf": "pass",
        "dkim_signature": "v=1;",
        "body": "Hello, this is a normal message.",
        "urls": [],
        "attachments": [],
    }

    result = service.analyze(parsed_email)

    # Top-level result.
    assert "header" in result
    assert "url" in result
    assert "body" in result
    assert "attachment" in result
    assert "authentication" in result
    assert "spam" in result
    assert "risk" in result
    assert "risk_level" in result
    assert "total_score" in result

    # Risk result.
    risk = result["risk"]

    assert "total_score" in risk
    assert "verdict" in risk
    assert "rule_based_score" in risk
    assert "spam_score" in risk
    assert "reasons" in risk
    assert "details" in risk

    # Risk details.
    details = risk["details"]

    assert "header" in details
    assert "url" in details
    assert "body" in details
    assert "attachment" in details
    assert "authentication" in details
    assert "spam" in details
