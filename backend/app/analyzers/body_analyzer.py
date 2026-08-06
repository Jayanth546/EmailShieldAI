class BodyAnalyzer:
    # Words and phrases commonly found in phishing emails
    SUSPICIOUS_KEYWORDS = {
        "urgent",
        "verify",
        "password",
        "login",
        "account",
        "click here",
        "confirm",
        "security alert",
        "limited time",
        "prize",
    }

    # Generic greetings often used in phishing emails
    GENERIC_GREETINGS = {
        "dear customer",
        "dear user",
        "dear client",
        "dear member",
        "valued customer",
        "dear account holder",
    }

    def analyze(self, body):
        issues = []
        score = 0

        # Convert body to lowercase for case-insensitive matching
        body_lower = body.lower()

        # Rule 1: Suspicious keywords
        for keyword in self.SUSPICIOUS_KEYWORDS:
            if keyword in body_lower:
                issues.append(f"Suspicious keyword found: '{keyword}'")
                score += 10

        # Rule 2: Generic greetings
        for greeting in self.GENERIC_GREETINGS:
            if greeting in body_lower:
                issues.append(
                    f"Generic greeting detected: '{greeting}'"
                )
                score += 15

        return {
            "score": score,
            "issues": issues,
        }
