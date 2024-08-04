from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class UserSchema(BaseModel):
    username: str
    password: str
    role: Optional[str] = "user"

class TokenSchema(BaseModel):
    access_token: str
    token_type: str

class UserActivitySchema(BaseModel):
    username: str
    activity: str
    timestamp: datetime

class UserPreferenceSchema(BaseModel):
    preference_type: str
    preference_value: str

    class Config:
        from_attributes = True