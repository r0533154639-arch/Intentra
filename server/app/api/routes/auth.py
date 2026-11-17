from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError

from app.core.security import revoke_access_token
from app.schemas.auth import LoginRequest, RegisterRequest, TokenResponse, UserResponse
from app.services.auth_service import get_auth_service

router = APIRouter()
bearer = HTTPBearer()


@router.post("/register", response_model=UserResponse)
def register(request: RegisterRequest):
    service = get_auth_service()
    try:
        user = service.register(request.username, request.email, request.password)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
    return {"id": user["_id"], "username": user["username"], "email": user["email"]}


@router.post("/login", response_model=TokenResponse)
def login(request: LoginRequest):
    service = get_auth_service()
    try:
        data = service.login(request.username, request.password)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(exc)) from exc
    return {"access_token": data["token"], "token_type": "bearer"}


@router.post("/logout")
def logout(credentials: HTTPAuthorizationCredentials = Depends(bearer)):
    try:
        revoked = revoke_access_token(credentials.credentials)
    except JWTError as exc:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid or expired token") from exc
    if not revoked:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Session is not active")
    return {"ok": True, "message": "Logged out"}
