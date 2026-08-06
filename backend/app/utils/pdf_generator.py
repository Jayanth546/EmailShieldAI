from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
)
from reportlab.lib.styles import getSampleStyleSheet


class PDFGenerator:

    def generate(self, result, filename):

        doc = SimpleDocTemplate(filename)
        styles = getSampleStyleSheet()

        story = []

        # Title
        story.append(
            Paragraph(
                "<b>EmailShield AI Report</b>",
                styles["Title"]
            )
        )

        story.append(Spacer(1, 20))

        # Overall Risk
        story.append(
            Paragraph(
                f"<b>Risk Level:</b> {result['risk_level']}",
                styles["Heading2"]
            )
        )

        story.append(
            Paragraph(
                f"<b>Total Score:</b> {result['total_score']}",
                styles["Heading2"]
            )
        )

        story.append(Spacer(1, 20))

        # Function to add analyzer sections
        def add_section(title, analyzer):

            story.append(
                Paragraph(
                    f"<b>{title}</b>",
                    styles["Heading2"]
                )
            )

            story.append(
                Paragraph(
                    f"Score: {analyzer['score']}",
                    styles["BodyText"]
                )
            )

            if analyzer["issues"]:
                for issue in analyzer["issues"]:
                    story.append(
                        Paragraph(
                            f"• {issue}",
                            styles["BodyText"]
                        )
                    )
            else:
                story.append(
                    Paragraph(
                        "No issues detected.",
                        styles["BodyText"]
                    )
                )

            story.append(Spacer(1, 12))

        # Analyzer Results
        add_section("Header Analysis", result["header"])
        add_section("URL Analysis", result["url"])
        add_section("Body Analysis", result["body"])
        add_section("Attachment Analysis", result["attachment"])
        add_section("Authentication Analysis", result["authentication"])

        # Recommendation
        story.append(Spacer(1, 20))

        story.append(
            Paragraph(
                "<b>Recommendation</b>",
                styles["Heading2"]
            )
        )

        if result["risk_level"] == "Safe":
            recommendation = (
                "This email appears to be safe. "
                "No suspicious indicators were detected."
            )

        elif result["risk_level"] == "Suspicious":
            recommendation = (
                "Exercise caution before interacting with this email. "
                "Verify the sender before clicking links or opening attachments."
            )

        else:
            recommendation = (
                "This email is highly likely to be a phishing attempt. "
                "Do not click any links, do not open attachments, and report the email immediately."
            )

        story.append(
            Paragraph(
                recommendation,
                styles["BodyText"]
            )
        )

        story.append(Spacer(1, 20))

        # Generate PDF
        doc.build(story)
