from fastapi import FastAPI

app = FastAPI(
    title="EmailShield AI",
    description="AI-Powered Email Spam & Phishing Detection System",
    version="1.0.0"
)


@app.get("/")
def home():
    return {
        "project": "EmailShield AI",
        "version": "1.0.0",
        "status": "Running"
    }


@app.get("/health")
def health():
    return {
        "status": "Healthy"
    }


@app.get("/about")
def about():
    return {
        "developer": "Cyber Hacker",
        "project": "EmailShield AI",
        "framework": "FastAPI"
    }