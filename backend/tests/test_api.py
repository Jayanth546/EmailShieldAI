import uuid

from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def unique_user():
    suffix = uuid.uuid4().hex[:8]

    return {
        "username": f"apitest_{suffix}",
        "email": f"apitest_{suffix}@example.com",
        "password": "Password123!",
    }


def register_and_login():
    user = unique_user()

    register_response = client.post(
        "/auth/register",
        json=user,
    )

    assert register_response.status_code == 200

    login_response = client.post(
        "/auth/login",
        json={
            "username": user["username"],
            "password": user["password"],
        },
    )

    assert login_response.status_code == 200

    token_data = login_response.json()

    assert "access_token" in token_data
    assert token_data["token_type"] == "bearer"

    return user, token_data["access_token"]


def phishing_email():
    return {
        "from": "security-alert@paypa1-example.com",
        "message_id": f"<phishing-{uuid.uuid4().hex}@example.com>",
        "reply_to": "attacker@example.com",
        "authentication_results": "dkim=fail; spf=fail",
        "received_spf": "fail",
        "dkim_signature": "invalid",
        "body": (
            "URGENT! Your account has been suspended. "
            "Verify your account immediately by clicking this link "
            "and provide your password and credit card information."
        ),
        "urls": [
            "http://paypa1-example.com/verify-account"
        ],
        "attachments": [
            "invoice.exe"
        ],
    }


# ============================================================
# BASIC API TESTS
# ============================================================

def test_health():
    response = client.get("/health")

    assert response.status_code == 200


# ============================================================
# REGISTRATION TESTS
# ============================================================

def test_register_user():
    user = unique_user()

    response = client.post(
        "/auth/register",
        json=user,
    )

    assert response.status_code == 200

    data = response.json()

    assert data["message"] == "User registered successfully"
    assert data["user"]["username"] == user["username"]
    assert data["user"]["email"] == user["email"]
    assert "id" in data["user"]


def test_duplicate_username_rejected():
    user = unique_user()

    first = client.post(
        "/auth/register",
        json=user,
    )

    assert first.status_code == 200

    second = client.post(
        "/auth/register",
        json=user,
    )

    assert second.status_code == 400
    assert second.json()["detail"] == "Username already registered"


def test_duplicate_email_rejected():
    user = unique_user()

    first = client.post(
        "/auth/register",
        json=user,
    )

    assert first.status_code == 200

    second_user = unique_user()
    second_user["email"] = user["email"]

    second = client.post(
        "/auth/register",
        json=second_user,
    )

    assert second.status_code == 400
    assert second.json()["detail"] == "Email already registered"


# ============================================================
# LOGIN SECURITY TESTS
# ============================================================

def test_login_success():
    user, token = register_and_login()

    assert token
    assert isinstance(token, str)


def test_login_invalid_password():
    user = unique_user()

    register_response = client.post(
        "/auth/register",
        json=user,
    )

    assert register_response.status_code == 200

    response = client.post(
        "/auth/login",
        json={
            "username": user["username"],
            "password": "WrongPassword123!",
        },
    )

    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid username or password"


def test_login_unknown_user():
    response = client.post(
        "/auth/login",
        json={
            "username": f"does_not_exist_{uuid.uuid4().hex}",
            "password": "Password123!",
        },
    )

    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid username or password"


# ============================================================
# AUTHENTICATION SECURITY TESTS
# ============================================================

def test_analyze_requires_authentication():
    response = client.post(
        "/analyze",
        json=phishing_email(),
    )

    assert response.status_code == 401


def test_analyze_invalid_token():
    response = client.post(
        "/analyze",
        headers={
            "Authorization": "Bearer invalid-token"
        },
        json=phishing_email(),
    )

    assert response.status_code == 401
    assert response.json()["detail"] == "Could not validate credentials"


def test_analyze_malformed_jwt():
    response = client.post(
        "/analyze",
        headers={
            "Authorization": "Bearer abc.def.ghi"
        },
        json=phishing_email(),
    )

    assert response.status_code == 401
    assert response.json()["detail"] == "Could not validate credentials"


def test_reports_requires_authentication():
    response = client.get("/reports")

    assert response.status_code == 401


def test_report_requires_authentication():
    response = client.get("/reports/1")

    assert response.status_code == 401


# ============================================================
# EMAIL ANALYSIS TESTS
# ============================================================

def test_analyze_phishing_email():
    user, token = register_and_login()

    response = client.post(
        "/analyze",
        headers={
            "Authorization": f"Bearer {token}"
        },
        json=phishing_email(),
    )

    assert response.status_code == 200

    data = response.json()

    assert data["risk_level"] == "Phishing"
    assert data["total_score"] == 100

    assert data["spam"]["label"] == "spam"
    assert data["spam"]["spam_probability"] > 0.5

    assert "report_id" in data
    assert data["report_id"] > 0


# ============================================================
# REPORT TESTS
# ============================================================

def test_get_reports():
    user, token = register_and_login()

    analysis_response = client.post(
        "/analyze",
        headers={
            "Authorization": f"Bearer {token}"
        },
        json=phishing_email(),
    )

    assert analysis_response.status_code == 200

    response = client.get(
        "/reports",
        headers={
            "Authorization": f"Bearer {token}"
        },
    )

    assert response.status_code == 200

    reports = response.json()

    assert isinstance(reports, list)
    assert len(reports) >= 1

    report = reports[-1]

    assert "id" in report
    assert "sender" in report
    assert "message_id" in report
    assert "risk_level" in report
    assert "total_score" in report
    assert "report_path" in report


def test_get_report():
    user, token = register_and_login()

    analysis_response = client.post(
        "/analyze",
        headers={
            "Authorization": f"Bearer {token}"
        },
        json=phishing_email(),
    )

    assert analysis_response.status_code == 200

    report_id = analysis_response.json()["report_id"]

    response = client.get(
        f"/reports/{report_id}",
        headers={
            "Authorization": f"Bearer {token}"
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["id"] == report_id
    assert data["risk_level"] == "Phishing"
    assert data["total_score"] == 100
    assert "body" in data
    assert "report_path" in data


def test_get_nonexistent_report():
    user, token = register_and_login()

    response = client.get(
        "/reports/999999999",
        headers={
            "Authorization": f"Bearer {token}"
        },
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Report not found"


def test_invalid_report_id():
    user, token = register_and_login()

    response = client.get(
        "/reports/REPORT_ID",
        headers={
            "Authorization": f"Bearer {token}"
        },
    )

    assert response.status_code == 422


# ============================================================
# AUTHORIZATION / IDOR SECURITY TEST
# ============================================================

def test_user_cannot_access_another_users_report():
    # User A creates a report
    user_a, token_a = register_and_login()

    analysis_response = client.post(
        "/analyze",
        headers={
            "Authorization": f"Bearer {token_a}"
        },
        json=phishing_email(),
    )

    assert analysis_response.status_code == 200

    report_id = analysis_response.json()["report_id"]

    # User B creates a separate account
    user_b, token_b = register_and_login()

    # User B attempts to access User A's report
    response = client.get(
        f"/reports/{report_id}",
        headers={
            "Authorization": f"Bearer {token_b}"
        },
    )

    assert response.status_code == 403

    assert response.json()["detail"] == (
        "You do not have permission to access this report"
    )


# ============================================================
# PDF AUTHORIZATION SECURITY TESTS
# ============================================================

def test_pdf_requires_authentication():
    response = client.get("/reports/1/pdf")

    assert response.status_code == 401


def test_user_cannot_download_another_users_pdf():
    # User A creates report
    user_a, token_a = register_and_login()

    analysis_response = client.post(
        "/analyze",
        headers={
            "Authorization": f"Bearer {token_a}"
        },
        json=phishing_email(),
    )

    assert analysis_response.status_code == 200

    report_id = analysis_response.json()["report_id"]

    # User B logs in
    user_b, token_b = register_and_login()

    # User B attempts to download User A's PDF
    response = client.get(
        f"/reports/{report_id}/pdf",
        headers={
            "Authorization": f"Bearer {token_b}"
        },
    )

    assert response.status_code == 403


# ============================================================
# AUTHORIZATION HEADER SECURITY TESTS
# ============================================================

def test_invalid_authorization_scheme():
    response = client.get(
        "/reports",
        headers={
            "Authorization": "Basic invalid-token"
        },
    )

    assert response.status_code == 401


def test_empty_bearer_token():
    response = client.get(
        "/reports",
        headers={
            "Authorization": "Bearer "
        },
    )

    assert response.status_code == 401

def test_analyze_rejects_unknown_fields():
    user, token = register_and_login()

    email = phishing_email()
    email["unexpected_field"] = "malicious"

    response = client.post(
        "/analyze",
        headers={
            "Authorization": f"Bearer {token}"
        },
        json=email,
    )

    assert response.status_code == 422


def test_analyze_rejects_oversized_body():
    user, token = register_and_login()

    email = phishing_email()
    email["body"] = "A" * 100001

    response = client.post(
        "/analyze",
        headers={
            "Authorization": f"Bearer {token}"
        },
        json=email,
    )

    assert response.status_code == 422


def test_analyze_rejects_oversized_url():
    user, token = register_and_login()

    email = phishing_email()
    email["urls"] = ["http://example.com/" + ("A" * 2048)]

    response = client.post(
        "/analyze",
        headers={
            "Authorization": f"Bearer {token}"
        },
        json=email,
    )

    assert response.status_code == 422


def test_analyze_rejects_newline_in_email_header():
    user, token = register_and_login()

    email = phishing_email()
    email["from"] = "attacker@example.com\r\nX-Injected: true"

    response = client.post(
        "/analyze",
        headers={
            "Authorization": f"Bearer {token}"
        },
        json=email,
    )

    assert response.status_code == 422


def test_analyze_rejects_invalid_attachment_filename():
    user, token = register_and_login()

    email = phishing_email()
    email["attachments"] = ["invoice\x00.exe"]

    response = client.post(
        "/analyze",
        headers={
            "Authorization": f"Bearer {token}"
        },
        json=email,
    )

    assert response.status_code == 422

def test_analyze_rejects_unknown_fields():
    user, token = register_and_login()

    email = phishing_email()
    email["unexpected_field"] = "malicious"

    response = client.post(
        "/analyze",
        headers={
            "Authorization": f"Bearer {token}"
        },
        json=email,
    )

    assert response.status_code == 422


def test_analyze_rejects_oversized_body():
    user, token = register_and_login()

    email = phishing_email()
    email["body"] = "A" * 100_001

    response = client.post(
        "/analyze",
        headers={
            "Authorization": f"Bearer {token}"
        },
        json=email,
    )

    assert response.status_code == 422


def test_analyze_rejects_too_many_urls():
    user, token = register_and_login()

    email = phishing_email()
    email["urls"] = [
        f"https://example.com/{i}"
        for i in range(101)
    ]

    response = client.post(
        "/analyze",
        headers={
            "Authorization": f"Bearer {token}"
        },
        json=email,
    )

    assert response.status_code == 422


def test_analyze_rejects_too_many_attachments():
    user, token = register_and_login()

    email = phishing_email()
    email["attachments"] = [
        f"file_{i}.txt"
        for i in range(51)
    ]

    response = client.post(
        "/analyze",
        headers={
            "Authorization": f"Bearer {token}"
        },
        json=email,
    )

    assert response.status_code == 422


def test_analyze_accepts_valid_email_after_hardening():
    user, token = register_and_login()

    response = client.post(
        "/analyze",
        headers={
            "Authorization": f"Bearer {token}"
        },
        json=phishing_email(),
    )

    assert response.status_code == 200
