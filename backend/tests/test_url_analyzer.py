from app.analyzers.url_analyzer import URLAnalyzer


def test_https_url():
    analyzer = URLAnalyzer()

    result = analyzer.analyze([
        "https://openai.com"
    ])

    assert result["score"] == 0
    assert result["issues"] == []


def test_http_url():
    analyzer = URLAnalyzer()

    result = analyzer.analyze([
        "http://example.com"
    ])

    assert result["score"] == 10
    assert len(result["issues"]) == 1
    assert "Insecure HTTP URL" in result["issues"][0]


def test_ip_address_url():
    analyzer = URLAnalyzer()

    result = analyzer.analyze([
        "http://192.168.1.100/login"
    ])

    # HTTP (+10) + IP Address (+20)
    assert result["score"] == 30
    assert any("IP Address URL detected" in issue for issue in result["issues"])


def test_url_shortener():
    analyzer = URLAnalyzer()

    result = analyzer.analyze([
        "https://bit.ly/abcd123"
    ])

    assert result["score"] == 15
    assert any(
        "URL shortener detected" in issue
        for issue in result["issues"]
    )
def test_suspicious_tld():
    analyzer = URLAnalyzer()

    result = analyzer.analyze([
        "https://paypal-login.xyz/login"
    ])

    assert result["score"] == 15
    assert any(
        "Suspicious TLD detected" in issue
        for issue in result["issues"]
    )
def test_excessive_subdomains():
    analyzer = URLAnalyzer()

    result = analyzer.analyze([
        "https://login.paypal.verify.secure.evil.com/login"
    ])

    assert result["score"] == 20
    assert any(
        "Too many subdomains" in issue
        for issue in result["issues"]
    )
