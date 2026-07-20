from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.redis import get_redis
from app.db.session import get_db
from app.models.user import User
from app.schemas.auth import AccessTokenResponse, RefreshRequest, TokenResponse
from app.schemas.user import UserCreate, UserRead
from app.services import auth_service
from app.services.auth_service import AuthError

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", response_model=UserRead, status_code=status.HTTP_201_CREATED)
async def register(user_in: UserCreate, db: AsyncSession = Depends(get_db)) -> User:
    try:
        return await auth_service.register_user(db, user_in)
    except AuthError as exc:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, str(exc)) from exc


@router.post("/login", response_model=TokenResponse)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: AsyncSession = Depends(get_db),
    redis: Redis = Depends(get_redis),
) -> TokenResponse:
    try:
        user = await auth_service.authenticate_user(db, form_data.username, form_data.password)
    except AuthError as exc:
        raise HTTPException(
            status.HTTP_401_UNAUTHORIZED, str(exc), headers={"WWW-Authenticate": "Bearer"}
        ) from exc
    return await auth_service.issue_tokens(redis, user)


@router.post("/refresh", response_model=AccessTokenResponse)
async def refresh(
    body: RefreshRequest, redis: Redis = Depends(get_redis)
) -> AccessTokenResponse:
    try:
        access_token = await auth_service.refresh_access_token(redis, body.refresh_token)
    except AuthError as exc:
        raise HTTPException(
            status.HTTP_401_UNAUTHORIZED, str(exc), headers={"WWW-Authenticate": "Bearer"}
        ) from exc
    return AccessTokenResponse(access_token=access_token)


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
async def logout(body: RefreshRequest, redis: Redis = Depends(get_redis)) -> None:
    await auth_service.revoke_refresh_token(redis, body.refresh_token)
