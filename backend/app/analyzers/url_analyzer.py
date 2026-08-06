from urllib.parse import urlparse
import ipaddress


class URLAnalyzer:
    # Common URL shortener domains
    SHORTENERS = {
        "bit.ly",
        "tinyurl.com",
        "t.co",
        "goo.gl",
        "ow.ly",
        "is.gd",
        "buff.ly",
        "rebrand.ly",
    }

    # TLDs that may deserve additional scrutiny
    SUSPICIOUS_TLDS = {
        "zip",
        "xyz",
        "click",
        "top",
        "work",
        "gq",
        "tk",
        "ml",
        "cf",
    }

    def analyze(self, urls):
        issues = []
        score = 0

        for url in urls:
            parsed = urlparse(url)
            hostname = (parsed.hostname or "").lower()

            # Rule 1: HTTP instead of HTTPS
            if parsed.scheme.lower() == "http":
                issues.append(f"Insecure HTTP URL: {url}")
                score += 10

            # Rule 2: IP Address URL
            try:
                ipaddress.ip_address(hostname)
                issues.append(f"IP Address URL detected: {url}")
                score += 20
            except (ValueError, TypeError):
                pass

            # Rule 3: URL Shortener
            if hostname in self.SHORTENERS:
                issues.append(f"URL shortener detected: {url}")
                score += 15

            # Rule 4: Suspicious Top-Level Domain (TLD)
            if "." in hostname:
                tld = hostname.split(".")[-1]

                if tld in self.SUSPICIOUS_TLDS:
                    issues.append(f"Suspicious TLD detected: .{tld}")
                    score += 15
            # Rule 5: Excessive subdomains
            if hostname.count(".") > 3:
                issues.append(
                    f"Too many subdomains: {hostname}"
                )
                score += 20

        return {
            "score": score,
            "issues": issues,
        }
