class HeaderAnalyzer:
    def analyze(self, email_data):
        issues = []

        if not email_data.get("from"):
            issues.append("Missing From header")

        if not email_data.get("message_id"):
            issues.append("Missing Message-ID")

        if email_data.get("reply_to") and email_data.get("reply_to") != email_data.get("from"):
            issues.append("Reply-To differs from From")

        return {
            "score": len(issues) * 10,
            "issues": issues,
        }