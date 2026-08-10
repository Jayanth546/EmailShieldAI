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

    # Semantic categories used for explainability.
    # These categories DO NOT change the risk score.
    SEMANTIC_CATEGORIES = {
        "urgency": {
            "urgent",
            "immediately",
            "act now",
            "act immediately",
            "as soon as possible",
            "final warning",
            "limited time",
        },
        "credential_request": {
            "password",
            "login",
            "credentials",
            "login information",
            "account information",
            "verify your identity",
            "confirm your identity",
        },
        "account_threat": {
            "account will be suspended",
            "account has been suspended",
            "account will be locked",
            "account has been locked",
            "account will be closed",
            "account will be permanently closed",
            "account access will be disabled",
            "account has been compromised",
        },
        "financial_reward": {
            "you won",
            "won $",
            "cash reward",
            "cash prize",
            "free money",
            "cash bonus",
            "special cash prize",
            "guaranteed reward",
            "special reward",
            "shopping voucher",
        },
        "call_to_action": {
            "click here",
            "click now",
            "verify now",
            "confirm now",
            "claim it now",
            "claim your",
            "sign up now",
            "update your",
            "confirm your",
        },
    }

    def analyze(self, body):
        issues = []
        findings = []
        semantic_findings = []
        score = 0

        # Convert body to lowercase for case-insensitive matching
        body_lower = body.lower()

        # --------------------------------
        # Rule 1: Suspicious keywords
        # --------------------------------
        for keyword in self.SUSPICIOUS_KEYWORDS:
            if keyword in body_lower:
                message = (
                    f"Suspicious keyword found: '{keyword}'"
                )

                issues.append(message)

                findings.append({
                    "category": "suspicious_keyword",
                    "keyword": keyword,
                    "message": message,
                    "score": 10,
                })

                score += 10

        # --------------------------------
        # Rule 2: Generic greetings
        # --------------------------------
        for greeting in self.GENERIC_GREETINGS:
            if greeting in body_lower:
                message = (
                    f"Generic greeting detected: '{greeting}'"
                )

                issues.append(message)

                findings.append({
                    "category": "generic_greeting",
                    "keyword": greeting,
                    "message": message,
                    "score": 15,
                })

                score += 15

        # --------------------------------
        # Rule 3: Semantic categories
        # --------------------------------
        #
        # These findings are explanatory only.
        # They DO NOT modify the existing score.
        #
        for category, phrases in self.SEMANTIC_CATEGORIES.items():
            matched_phrases = []

            for phrase in phrases:
                if phrase in body_lower:
                    matched_phrases.append(phrase)

            if matched_phrases:
                semantic_findings.append({
                    "category": category,
                    "matches": sorted(matched_phrases),
                })

        return {
            "score": score,
            "issues": issues,
            "findings": findings,
            "semantic_findings": semantic_findings,
        }

