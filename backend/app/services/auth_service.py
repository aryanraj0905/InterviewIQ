from datetime import timedelta

import jwt
from redis.asyncio import Redis
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.security import (
    TokenType,
    create_access_token,
    create_refresh_token,
    decode_token,
    hash_password,
    verify_password,
)
from app.models.user import User
from app.schemas.auth import TokenResponse
from app.schemas.user import UserCreate


class AuthError(Exception):
    """Raised for any registration/authentication failure; routes translate this to HTTP."""


def _refresh_token_key(jti: str) -> str:
    return f"refresh_token:{jti}"


async def register_user(db: AsyncSession, user_in: UserCreate) -> User:
    existing = await db.scalar(select(User).where(User.email == user_in.email))
    if existing is not None:
        raise AuthError("A user with this email already exists")

    user = User(
        email=user_in.email,
        hashed_password=hash_password(user_in.password),
        full_name=user_in.full_name,
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return user


async def authenticate_user(db: AsyncSession, email: str, password: str) -> User:
    user = await db.scalar(select(User).where(User.email == email))
    if user is None or not verify_password(password, user.hashed_password):
        raise AuthError("Incorrect email or password")
    if not user.is_active:
        raise AuthError("User account is disabled")
    return user


async def issue_tokens(redis: Redis, user: User) -> TokenResponse:
    access_token = create_access_token(str(user.id))
    refresh_token = create_refresh_token(str(user.id))

    payload = decode_token(refresh_token)
    ttl = timedelta(days=settings.refresh_token_expire_days)
    await redis.set(_refresh_token_key(payload["jti"]), str(user.id), ex=ttl)

    return TokenResponse(access_token=access_token, refresh_token=refresh_token)


async def refresh_access_token(redis: Redis, refresh_token: str) -> str:
    try:
        payload = decode_token(refresh_token)
    except jwt.PyJWTError as exc:
        raise AuthError("Invalid or expired refresh token") from exc

    if payload.get("type") != TokenType.REFRESH.value:
        raise AuthError("Invalid token type")

    stored_user_id = await redis.get(_refresh_token_key(payload["jti"]))
    if stored_user_id is None or stored_user_id != payload["sub"]:
        raise AuthError("Refresh token has been revoked or expired")

    return create_access_token(payload["sub"])


async def revoke_refresh_token(redis: Redis, refresh_token: str) -> None:
    try:
        payload = decode_token(refresh_token)
    except jwt.PyJWTError:
        return
    await redis.delete(_refresh_token_key(payload["jti"]))
