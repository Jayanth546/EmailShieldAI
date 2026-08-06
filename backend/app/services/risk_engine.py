class RiskEngine:
    SAFE_THRESHOLD = 30
    PHISHING_THRESHOLD = 70

    def analyze(
        self,
        header_result,
        url_result,
        body_result,
        attachment_result,
        authentication_result,
    ):
        total_score = (
            header_result["score"]
            + url_result["score"]
            + body_result["score"]
            + attachment_result["score"]
            + authentication_result["score"]
        )

        if total_score >= self.PHISHING_THRESHOLD:
            verdict = "PHISHING"
        elif total_score >= self.SAFE_THRESHOLD:
            verdict = "SUSPICIOUS"
        else:
            verdict = "SAFE"

        return {
            "total_score": total_score,
            "verdict": verdict,
            "details": {
                "header": header_result,
                "url": url_result,
                "body": body_result,
                "attachment": attachment_result,
                "authentication": authentication_result,
            },
        }
