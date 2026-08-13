import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jwt import InvalidTokenError

from app.auth.security import ALGORITHM, JWT_SECRET_KEY
from app.database.db_service import DatabaseService

oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl="/auth/login"
)

db = DatabaseService()


def get_current_user(
    token: str = Depends(oauth2_scheme),
):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={
            "WWW-Authenticate": "Bearer"
        },
    )

    try:
        payload = jwt.decode(
            token,
            JWT_SECRET_KEY,
            algorithms=[ALGORITHM],
        )

        user_id = payload.get("sub")

        if user_id is None:
            raise credentials_exception

        try:
            user_id = int(user_id)
        except (TypeError, ValueError):
            raise credentials_exception

    except InvalidTokenError:
        raise credentials_exception

    user = db.get_user_by_id(user_id)

    if user is None:
        raise credentials_exception

    return user

