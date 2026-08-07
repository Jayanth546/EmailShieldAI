from fastapi import APIRouter, HTTPException

from app.auth.security import hash_password
from app.database.db_service import DatabaseService
from app.schemas.user_schema import UserRegister


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
