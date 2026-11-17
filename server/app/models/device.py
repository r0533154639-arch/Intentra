from pydantic import BaseModel, Field


class Device(BaseModel):
    id: str = Field(alias="_id")
    user_id: str
    os_user_identifier: str
    installation_id: str
    device_name: str
    desktop_version: str = "1.0.0"
    calibration_data: dict = Field(default_factory=dict)
    last_seen: str
    created_at: str

    class Config:
        populate_by_name = True
