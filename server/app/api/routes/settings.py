from fastapi import APIRouter, Depends

from app.core.dependencies import get_current_user_id
from app.schemas.settings import SettingsPayload, recommended_settings_payload
from app.services.settings_service import get_settings_service

router = APIRouter()


@router.get("/settings")
def get_settings(user_id: str = Depends(get_current_user_id)):
    service = get_settings_service()
    settings = service.get_for_user(user_id)
    if not settings:
        return {
            "user_id": user_id,
            **recommended_settings_payload(),
            "updated_at": None,
            "version": 0,
        }
    return settings


@router.put("/settings")
def update_settings(payload: SettingsPayload, user_id: str = Depends(get_current_user_id)):
    service = get_settings_service()
    return service.upsert_for_user(user_id, payload.model_dump())
