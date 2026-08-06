from app.utils.pdf_generator import PDFGenerator

sample = {
    "risk_level": "Phishing",
    "total_score": 85,

    "header": {
        "score": 20,
        "issues": [
            "Missing Message-ID",
            "Reply-To mismatch"
        ]
    },

    "url": {
        "score": 30,
        "issues": [
            "HTTP URL",
            "URL Shortener"
        ]
    },

    "body": {
        "score": 20,
        "issues": [
            "Verify",
            "Click Here"
        ]
    },

    "attachment": {
        "score": 10,
        "issues": [
            "invoice.exe"
        ]
    },

    "authentication": {
        "score": 5,
        "issues": [
            "SPF Failed"
        ]
    }
}

PDFGenerator().generate(sample, "report.pdf")

print("PDF created successfully!")
