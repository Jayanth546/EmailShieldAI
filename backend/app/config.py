import os
from pathlib import Path

REPORTS_DIR = Path(
    os.getenv("REPORTS_DIR", "reports")
).resolve()
