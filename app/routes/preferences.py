from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from typing import List
from common.database.database import get_db
from middleware.auth import *
from common.CRUD.userPrefrence import *
from common.CRUD.book_crud import *
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

@router.post("/toggle-like-book/{book_id}")
def toggle_like_book_route(book_id: int, username: str, db: Session = Depends(get_db)):
    result = toggle_like_book(db, username, book_id)
    return result

@router.get("/liked-books", response_model=List[BookSchema])
def get_liked_books_route(username: str, db: Session = Depends(get_db)):
    books = get_liked_books(db, username)
    return [book_to_dict(book) for book in books]