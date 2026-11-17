from fastapi import APIRouter, Depends, HTTPException, status

from app.core.dependencies import get_current_user_id
from app.services.auth_service import get_auth_service

router = APIRouter()


@router.get("/me")
def get_me(user_id: str = Depends(get_current_user_id)):
    service = get_auth_service()
    user = service.get_user(user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return {"id": user["_id"], "username": user["username"], "email": user["email"]}
