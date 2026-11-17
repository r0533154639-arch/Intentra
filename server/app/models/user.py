from pydantic import BaseModel, Field


class User(BaseModel):
    id: str = Field(alias="_id")
    username: str
    email: str
    password_hash: str
    created_at: str
    updated_at: str

    class Config:
        populate_by_name = True
