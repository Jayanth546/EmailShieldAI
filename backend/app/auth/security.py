from datetime import datetime, timedelta, timezone
import os

from dotenv import load_dotenv
from pwdlib import PasswordHash
import jwt


load_dotenv()


# ============================================================
# JWT CONFIGURATION
# ============================================================

JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY")

ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256").upper()

ACCESS_TOKEN_EXPIRE_MINUTES = int(
    os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30")
)

# Only allow the algorithm that the application is designed
# and tested to use.
ALLOWED_ALGORITHMS = {"HS256"}

if ALGORITHM not in ALLOWED_ALGORITHMS:
    raise RuntimeError(
        f"Unsupported JWT algorithm: {ALGORITHM}. "
        f"Allowed algorithms: {sorted(ALLOWED_ALGORITHMS)}"
    )

if not JWT_SECRET_KEY:
    raise RuntimeError(
        "JWT_SECRET_KEY is not configured. "
        "Set it in the environment or .env file."
    )

# Reject obviously weak development secrets.
if len(JWT_SECRET_KEY) < 32:
    raise RuntimeError(
        "JWT_SECRET_KEY is too short. "
        "Use a cryptographically random secret of at least 32 characters."
    )

if ACCESS_TOKEN_EXPIRE_MINUTES <= 0:
    raise RuntimeError(
        "ACCESS_TOKEN_EXPIRE_MINUTES must be greater than 0."
    )


# ============================================================
# PASSWORD HASHING
# ============================================================

password_hash = PasswordHash.recommended()


def hash_password(password: str) -> str:
    """Hash a plain-text password."""
    return password_hash.hash(password)


def verify_password(
    plain_password: str,
    hashed_password: str,
) -> bool:
    """Verify a plain-text password against its hash."""
    return password_hash.verify(
        plain_password,
        hashed_password,
    )


# ============================================================
# JWT ACCESS TOKEN
# ============================================================

def create_access_token(
    data: dict,
    expires_delta: timedelta | None = None,
) -> str:
    """Create a signed JWT access token."""

    to_encode = data.copy()

    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(
            minutes=ACCESS_TOKEN_EXPIRE_MINUTES
        )

    to_encode.update(
        {
            "exp": expire,
        }
    )

    encoded_jwt = jwt.encode(
        to_encode,
        JWT_SECRET_KEY,
        algorithm=ALGORITHM,
    )

    return encoded_jwt
