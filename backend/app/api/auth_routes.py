import json

from fastapi import APIRouter, HTTPException, Request
from pydantic import ValidationError

from app.auth.security import (
    create_access_token,
    hash_password,
    verify_password,
)
from app.database.db_service import DatabaseService
from app.middleware.security import LoginBruteForceMiddleware
from app.schemas.user_schema import Token, UserLogin, UserRegister

router = APIRouter(
    prefix="/auth",
    tags=["Authentication"],
)

db = DatabaseService()


@router.post("/register")
def register_user(user: UserRegister):
    # Check username
    existing_username = db.get_user_by_username(user.username)

    if existing_username:
        raise HTTPException(
            status_code=400,
            detail="Username already registered",
        )

    # Check email
    existing_email = db.get_user_by_email(user.email)

    if existing_email:
        raise HTTPException(
            status_code=400,
            detail="Email already registered",
        )

    # Hash password
    hashed_password = hash_password(user.password)

    # Save user
    new_user = db.create_user(
        username=user.username,
        email=user.email,
        hashed_password=hashed_password,
    )

    return {
        "message": "User registered successfully",
        "user": {
            "id": new_user.id,
            "username": new_user.username,
            "email": new_user.email,
        },
    }


@router.post("/login", response_model=Token)
async def login_user(request: Request):
    """
    Login endpoint.

    Supports both:
    - JSON: {"username": "...", "password": "..."}
    - Form: username=...&password=...

    This keeps backward compatibility with the existing API
    while allowing OAuth2-style form login tests.
    """

    content_type = request.headers.get("content-type", "").lower()

    if "application/x-www-form-urlencoded" in content_type:
        form = await request.form()

        username = form.get("username")
        password = form.get("password")

    elif "application/json" in content_type:
        try:
            payload = await request.json()
        except json.JSONDecodeError as exc:
            raise HTTPException(
                status_code=422,
                detail="Invalid JSON request body",
            ) from exc

        try:
            login_data = UserLogin.model_validate(payload)
        except ValidationError as exc:
            raise HTTPException(
                status_code=422,
                detail="Invalid login request",
            ) from exc

        username = login_data.username
        password = login_data.password

    else:
        raise HTTPException(
            status_code=415,
            detail="Unsupported content type",
        )

    if not isinstance(username, str) or not isinstance(password, str):
        raise HTTPException(
            status_code=422,
            detail="Username and password are required",
        )

    # --------------------------------------------------------
    # Brute-force protection
    # --------------------------------------------------------

    if LoginBruteForceMiddleware.is_blocked(username):
        raise HTTPException(
            status_code=429,
            detail=(
                "Too many failed login attempts. "
                "Please try again later."
            ),
            headers={"Retry-After": "60"},
        )

    # --------------------------------------------------------
    # Find user
    # --------------------------------------------------------

    existing_user = db.get_user_by_username(username)

    if existing_user is None:
        LoginBruteForceMiddleware.record_failure(username)

        raise HTTPException(
            status_code=401,
            detail="Invalid username or password",
        )

    # --------------------------------------------------------
    # Verify password
    # --------------------------------------------------------

    password_valid = verify_password(
        password,
        existing_user.hashed_password,
    )

    if not password_valid:
        LoginBruteForceMiddleware.record_failure(username)

        raise HTTPException(
            status_code=401,
            detail="Invalid username or password",
        )

    # --------------------------------------------------------
    # Successful login
    # --------------------------------------------------------

    LoginBruteForceMiddleware.clear_failures(username)

    access_token = create_access_token(
        data={
            "sub": str(existing_user.id),
            "username": existing_user.username,
        }
    )

    return {
        "access_token": access_token,
        "token_type": "bearer",
    }
