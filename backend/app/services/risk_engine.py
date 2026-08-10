class RiskEngine:
    SAFE_THRESHOLD = 30
    PHISHING_THRESHOLD = 70

    # Maximum contribution from the ML spam model
    MAX_SPAM_SCORE = 40

    def _build_reasons(
        self,
        header_result,
        url_result,
        body_result,
        attachment_result,
        authentication_result,
        spam_result,
    ):
        """
        Build human-readable explanations for the calculated
        security risk.

        These reasons describe evidence from the security analyzers.
        They do not claim that the ML model itself identified
        individual words or phrases.
        """

        reasons = []

        # --------------------------------
        # Header evidence
        # --------------------------------
        header_score = header_result.get("score", 0)

        if header_score > 0:
            reasons.append({
                "category": "header",
                "message": "Suspicious email header indicators detected.",
                "score": header_score,
            })

        # --------------------------------
        # URL evidence
        # --------------------------------
        url_score = url_result.get("score", 0)

        if url_score > 0:
            reasons.append({
                "category": "url",
                "message": "Suspicious URL indicators detected.",
                "score": url_score,
            })

        # --------------------------------
        # Body evidence
        # --------------------------------
        body_score = body_result.get("score", 0)

        if body_score > 0:
            reasons.append({
                "category": "body",
                "message": "Suspicious language or content detected in the email body.",
                "score": body_score,
            })

        # --------------------------------
        # Attachment evidence
        # --------------------------------
        attachment_score = attachment_result.get("score", 0)

        if attachment_score > 0:
            reasons.append({
                "category": "attachment",
                "message": "Suspicious attachment indicators detected.",
                "score": attachment_score,
            })

        # --------------------------------
        # Authentication evidence
        # --------------------------------
        authentication_score = authentication_result.get("score", 0)

        if authentication_score > 0:
            reasons.append({
                "category": "authentication",
                "message": "Email authentication checks produced security warnings.",
                "score": authentication_score,
            })

        # --------------------------------
        # ML evidence
        # --------------------------------
        if spam_result:
            spam_probability = float(
                spam_result.get("spam_probability", 0.0)
            )

            if spam_probability >= 0.70:
                reasons.append({
                    "category": "machine_learning",
                    "message": (
                        f"Machine-learning spam probability is "
                        f"{spam_probability:.0%}."
                    ),
                    "score": round(
                        spam_probability * self.MAX_SPAM_SCORE
                    ),
                })

            elif spam_probability >= 0.50:
                reasons.append({
                    "category": "machine_learning",
                    "message": (
                        f"Machine-learning model indicates elevated "
                        f"spam probability of {spam_probability:.0%}."
                    ),
                    "score": round(
                        spam_probability * self.MAX_SPAM_SCORE
                    ),
                })

        # --------------------------------
        # No evidence
        # --------------------------------
        if not reasons:
            reasons.append({
                "category": "general",
                "message": "No significant security risk indicators detected.",
                "score": 0,
            })

        return reasons

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
        # 5. Build explanations
        # --------------------------------
        reasons = self._build_reasons(
            header_result,
            url_result,
            body_result,
            attachment_result,
            authentication_result,
            spam_result,
        )

        # --------------------------------
        # 6. Return detailed result
        # --------------------------------
        return {
            "total_score": total_score,
            "verdict": verdict,

            "rule_based_score": rule_based_score,
            "spam_score": spam_score,

            "reasons": reasons,

            "details": {
                "header": header_result,
                "url": url_result,
                "body": body_result,
                "attachment": attachment_result,
                "authentication": authentication_result,
                "spam": spam_result,
            },
        }
