from fastapi import APIRouter, HTTPException

from app.auth.security import (
    hash_password,
    verify_password,
    create_access_token,
)
from app.database.db_service import DatabaseService
from app.schemas.user_schema import UserRegister, UserLogin, Token


router = APIRouter(
    prefix="/auth",
    tags=["Authentication"],
)

db = DatabaseService()


@router.post("/register")
def register_user(user: UserRegister):

    # Check username
    existing_username = db.get_user_by_username(
        user.username
    )

    if existing_username:
        raise HTTPException(
            status_code=400,
            detail="Username already registered",
        )

    # Check email
    existing_email = db.get_user_by_email(
        user.email
    )

    if existing_email:
        raise HTTPException(
            status_code=400,
            detail="Email already registered",
        )

    # Hash password
    hashed_password = hash_password(
        user.password
    )

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
def login_user(user: UserLogin):

    # Find user
    existing_user = db.get_user_by_username(
        user.username
    )

    if existing_user is None:
        raise HTTPException(
            status_code=401,
            detail="Invalid username or password",
        )

    # Verify password
    password_valid = verify_password(
        user.password,
        existing_user.hashed_password,
    )

    if not password_valid:
        raise HTTPException(
            status_code=401,
            detail="Invalid username or password",
        )

    # Create JWT access token
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
