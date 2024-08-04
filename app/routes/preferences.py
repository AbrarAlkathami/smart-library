from fastapi import APIRouter, HTTPException, Depends
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from typing import List
from common.database.database import get_db
from common.database.models import UserActivity
from schemas.user import UserSchema, TokenSchema, UserActivitySchema
from middleware.auth import create_access_token, get_current_user, admin_required
from common.CRUD.userPrefrence import *
from middleware.logger import log_user_activity
from sqlalchemy.orm import Session 
from schemas.user import UserPreferenceSchema


router = APIRouter()

@router.post("/preferences", response_model=UserPreferenceSchema)
def create_preference(preference: UserPreferenceSchema,db: Session = Depends(get_db),current_user: dict = Depends(get_current_user)):
    return create_user_preference(db, preference, current_user['username'])


@router.get("/preferences", response_model=List[UserPreferenceSchema])
def read_preferences(
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    preferences = get_user_preferences(db, current_user['username'])
    if not preferences:
        raise HTTPException(status_code=404, detail="Preferences not found")
    return preferences