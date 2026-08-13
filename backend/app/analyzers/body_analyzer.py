from typing import ClassVar


class BodyAnalyzer:
    # Words and phrases commonly found in phishing emails
    SUSPICIOUS_KEYWORDS: ClassVar[set[str]] = {
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
    GENERIC_GREETINGS: ClassVar[set[str]] = {
        "dear customer",
        "dear user",
        "dear client",
        "dear member",
        "valued customer",
        "dear account holder",
    }

    # Semantic categories used for explainability.
    # These categories do NOT change the risk score.
    SEMANTIC_CATEGORIES: ClassVar[dict[str, set[str]]] = {
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
        body_lower = body.lower()

        issues = []
        score = 0

        # Semantic findings must be a list of dictionaries.
        semantic_findings = []

        # --------------------------------------------------
        # Rule 1: Suspicious keywords
        # --------------------------------------------------
        for keyword in self.SUSPICIOUS_KEYWORDS:
            if keyword in body_lower:
                issues.append(
                    f"Suspicious keyword: '{keyword}'"
                )
                score += 10

        # --------------------------------------------------
        # Rule 2: Generic greetings
        # --------------------------------------------------
        for greeting in self.GENERIC_GREETINGS:
            if greeting in body_lower:
                issues.append("Generic greeting detected")
                score += 15
                break

        # --------------------------------------------------
        # Semantic findings
        # --------------------------------------------------
        # These findings are for explainability only.
        # They do NOT affect the risk score.
        for category, phrases in self.SEMANTIC_CATEGORIES.items():
            matches = sorted(
                phrase
                for phrase in phrases
                if phrase in body_lower
            )

            if matches:
                semantic_findings.append(
                    {
                        "category": category,
                        "matches": matches,
                    }
                )

        return {
            "score": score,
            "issues": issues,
            "semantic_findings": semantic_findings,
        }
