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
        "attachments": []
    }

    result = service.analyze(parsed_email)

    assert result["risk_level"] == "Safe"
    assert result["total_score"] < 30


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
        "urls": [
            "http://bit.ly/login"
        ],
        "attachments": [
            "invoice.zip"
        ]
    }

    result = service.analyze(parsed_email)

    assert result["risk_level"] in [
        "Suspicious",
        "Phishing"
    ]

    assert result["total_score"] >= 30


def test_phishing_email():
    service = EmailAnalysisService()

    parsed_email = {
        "from": "",
        "message_id": None,
        "reply_to": "hacker@gmail.com",
        "authentication_results": "spf=fail dkim=fail dmarc=fail",
        "received_spf": "fail",
        "dkim_signature": None,
        "body": """
URGENT!

Verify your password immediately.

Click here.

Security alert.
""",
        "urls": [
            "http://192.168.1.1/login.zip"
        ],
        "attachments": [
            "invoice.pdf.exe",
            "macro.docm"
        ]
    }

    result = service.analyze(parsed_email)

    assert result["risk_level"] == "Phishing"

    assert result["total_score"] >= 60
