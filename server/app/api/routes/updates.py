from fastapi import APIRouter, HTTPException, status

from app.services.update_service import get_update_service

router = APIRouter()


@router.get("/check")
def check_for_update(current_version: str | None = None, platform: str = "windows"):
    try:
        return get_update_service().check(current_version, platform)
    except LookupError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(exc)) from exc


@router.get("/latest")
def latest_update(platform: str = "windows"):
    try:
        return get_update_service().latest(platform)
    except LookupError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
