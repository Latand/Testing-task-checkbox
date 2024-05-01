from datetime import timedelta
from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, status

from api.models import SignupRequest, Token
from api.dependencies import get_config, get_repository
from config import Config
from database.repo.requests import RequestsRepo
from services.auth import authenticate_user, create_access_token, get_password_hash


router = APIRouter()


@router.post("/signup")
async def signup_for_access_token(
    form_data: SignupRequest,
    repo: Annotated[RequestsRepo, Depends(get_repository)],
    config: Annotated[Config, Depends(get_config)],
) -> Token:
    user = await authenticate_user(repo, form_data.username, form_data.password)

    if not user:
        await repo.users.create_user(
            form_data.full_name,
            form_data.username,
            get_password_hash(form_data.password),
        )
        await repo.session.commit()

    access_token_expires = timedelta(days=config.api.access_token_expire_days)
    access_token = create_access_token(
        config.api.secret_key,
        config.api.algorithm,
        data={"sub": form_data.username},
        expires_delta=access_token_expires,
    )
    return Token(
        access_token=access_token,
        token_type="bearer",
        expires_in=int(access_token_expires.total_seconds()),
    )


@router.get("/token")
async def login_for_access_token(
    username: str,
    password: str,
    repo: Annotated[RequestsRepo, Depends(get_repository)],
    config: Annotated[Config, Depends(get_config)],
) -> Token:
    user = await authenticate_user(repo, username, password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password, or user does not exist",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token_expires = timedelta(days=config.api.access_token_expire_days)
    access_token = create_access_token(
        config.api.secret_key,
        config.api.algorithm,
        data={"sub": user.username},
        expires_delta=access_token_expires,
    )
    return Token(
        access_token=access_token,
        token_type="bearer",
        expires_in=int(access_token_expires.total_seconds()),
    )
