from fastapi import APIRouter, Depends, Header, HTTPException, status

from app.core.dependencies import get_current_user_id, get_optional_current_user_id
from app.schemas.settings import (
    DevicePairingApproval,
    DevicePairingStart,
    DeviceRegistration,
    CalibrationUpdate,
)
from app.services.device_service import DeviceService, get_device_service
from app.services.settings_service import get_settings_service

router = APIRouter()


@router.post("/pairing-codes")
def start_device_pairing(payload: DevicePairingStart):
    try:
        return get_device_service().start_pairing(payload.model_dump())
    except PermissionError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc)) from exc


@router.post("/pair")
def approve_device_pairing(
    payload: DevicePairingApproval,
    user_id: str = Depends(get_current_user_id),
):
    try:
        return get_device_service().approve_pairing(user_id, payload.pairing_code)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc


@router.get("/pairing-codes/{device_id}")
def get_pairing_status(
    device_id: str,
    device_key: str | None = Header(default=None, alias="X-Device-Key"),
):
    if not device_key:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Device credentials are required")
    try:
        return get_device_service().poll_pairing(device_id, device_key)
    except PermissionError as exc:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(exc)) from exc


@router.post("/register")
def register_device(
    payload: DeviceRegistration,
    user_id: str = Depends(get_current_user_id),
):
    try:
        return get_device_service().register_device(user_id, payload.model_dump())
    except PermissionError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc)) from exc


@router.get("")
def list_devices(user_id: str = Depends(get_current_user_id)):
    return get_device_service().list_for_user(user_id)


@router.get("/{device_id}/settings")
def get_device_settings(
    device_id: str,
    user_id: str | None = Depends(get_optional_current_user_id),
    device_key: str | None = Header(default=None, alias="X-Device-Key"),
):
    device_service: DeviceService = get_device_service()
    if user_id:
        device = device_service.get_for_user(device_id, user_id)
    elif device_key:
        device = device_service.get_for_device_key(device_id, device_key)
    else:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Authentication is required")
    if device is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Device not found")

    return get_settings_service().get_for_device(
        device["user_id"],
        device.get("calibration_data", {}),
    )


@router.put("/{device_id}/settings/calibration")
def update_device_calibration(
    device_id: str,
    payload: CalibrationUpdate,
    user_id: str | None = Depends(get_optional_current_user_id),
    device_key: str | None = Header(default=None, alias="X-Device-Key"),
):
    if user_id:
        device = get_device_service().get_for_user(device_id, user_id)
    elif device_key:
        device = get_device_service().get_for_device_key(device_id, device_key)
    else:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Authentication is required")
    if device is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Device not found")
    get_device_service().update_calibration(
        device_id,
        device["user_id"],
        payload.calibration_data,
    )
    return get_settings_service().get_for_device(
        device["user_id"],
        payload.calibration_data,
    )
