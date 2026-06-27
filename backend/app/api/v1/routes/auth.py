from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from backend.app.db.session import get_db
from backend.app.schemas.auth import CurrentUser, LoginRequest, TokenResponse
from backend.app.security.dependencies import get_current_active_user
from backend.app.services.auth_service import AuthService

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/login", response_model=TokenResponse)
def login(payload: LoginRequest, db: Session = Depends(get_db)):
    service = AuthService(db)
    try:
        user, token = service.login(payload)
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(exc),
        ) from exc
    except PermissionError as exc:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(exc),
        ) from exc

    return TokenResponse(
        access_token=token,
        role=user.role,
        user_id=user.id,
        tenant_id=user.tenant_id,
    )


@router.get("/me", response_model=CurrentUser)
def me(current_user=Depends(get_current_active_user)):
    return CurrentUser(
        id=current_user.id,
        tenant_id=current_user.tenant_id,
        email=current_user.email,
        role=current_user.role,
    )