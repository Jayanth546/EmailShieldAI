class RiskEngine:
    SAFE_THRESHOLD = 30
    PHISHING_THRESHOLD = 70

    # Maximum contribution from the ML spam model
    MAX_SPAM_SCORE = 40

    def analyze(
        self,
        header_result,
        url_result,
        body_result,
        attachment_result,
        authentication_result,
        spam_result=None,
    ):
        """
        Calculate the final email risk score.

        The final score combines:
        - Header analysis
        - URL analysis
        - Body analysis
        - Attachment analysis
        - Authentication analysis
        - ML spam probability
        """

        # --------------------------------
        # 1. Rule-based security score
        # --------------------------------
        rule_based_score = (
            header_result["score"]
            + url_result["score"]
            + body_result["score"]
            + attachment_result["score"]
            + authentication_result["score"]
        )

        # --------------------------------
        # 2. ML spam score
        # --------------------------------
        spam_score = 0

        if spam_result:
            spam_probability = float(
                spam_result.get("spam_probability", 0.0)
            )

            # Convert probability into a score.
            #
            # Example:
            # 0.00 -> 0
            # 0.50 -> 20
            # 0.75 -> 30
            # 1.00 -> 40
            #
            spam_score = round(
                spam_probability * self.MAX_SPAM_SCORE
            )

        # --------------------------------
        # 3. Final score
        # --------------------------------
        total_score = min(
            rule_based_score + spam_score,
            100,
        )

        # --------------------------------
        # 4. Determine verdict
        # --------------------------------
        if total_score >= self.PHISHING_THRESHOLD:
            verdict = "PHISHING"

        elif total_score >= self.SAFE_THRESHOLD:
            verdict = "SUSPICIOUS"

        else:
            verdict = "SAFE"

        # --------------------------------
        # 5. Return detailed result
        # --------------------------------
        return {
            "total_score": total_score,
            "verdict": verdict,

            "rule_based_score": rule_based_score,
            "spam_score": spam_score,

            "details": {
                "header": header_result,
                "url": url_result,
                "body": body_result,
                "attachment": attachment_result,
                "authentication": authentication_result,
                "spam": spam_result,
            },
        }
