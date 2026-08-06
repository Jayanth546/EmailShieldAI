class AuthenticationAnalyzer:
    def analyze(self, email):
        issues = []
        score = 0

        # -------------------------
        # SPF
        # -------------------------
        spf = email.get("received_spf")

        if not spf:
            issues.append("SPF header missing")
            score += 15

        elif "fail" in spf.lower():
            issues.append("SPF validation failed")
            score += 30

        # -------------------------
        # DKIM
        # -------------------------
        dkim = email.get("dkim_signature")

        if not dkim:
            issues.append("DKIM signature missing")
            score += 15

        # -------------------------
        # Authentication Results
        # -------------------------
        auth = email.get("authentication_results")

        if auth:
            auth = auth.lower()

            if "spf=fail" in auth:
                issues.append("SPF failed")
                score += 30

            if "dkim=fail" in auth:
                issues.append("DKIM failed")
                score += 30

            if "dmarc=fail" in auth:
                issues.append("DMARC failed")
                score += 40

        return {
            "score": score,
            "issues": issues,
        }
