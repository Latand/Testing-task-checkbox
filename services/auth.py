from datetime import datetime, timedelta, timezone
from typing import Annotated

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from passlib.context import CryptContext

from api.dependencies import get_config, get_repository
from config import Config
from database.models.users import User
from database.repo.requests import RequestsRepo

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


def verify_password(plain_password: str, hashed_password: str):
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str):
    return pwd_context.hash(password)


async def get_current_user(
    repo: Annotated[RequestsRepo, Depends(get_repository)],
    config: Annotated[Config, Depends(get_config)],
    token: Annotated[str, Depends(oauth2_scheme)],
) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = jwt.decode(
            token, config.api.secret_key, algorithms=[config.api.algorithm]
        )
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception

    except JWTError:
        raise credentials_exception

    user = await repo.users.get_user(username)
    if user is None:
        raise credentials_exception
    return user


async def authenticate_user(repo: RequestsRepo, username: str, password: str):
    user: User = await repo.users.get_user(username)
    if not user:
        return False
    if not verify_password(password, user.password_hash):
        return False

    return user


def create_access_token(
    secret_key: str, algorithm: str, data: dict, expires_delta: timedelta
):
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + expires_delta

    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, secret_key, algorithm=algorithm)
    return encoded_jwt
