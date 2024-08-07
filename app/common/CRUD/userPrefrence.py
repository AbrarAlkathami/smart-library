
from sqlalchemy.orm import Session 
from schemas.user import UserPreferenceSchema
from fastapi import HTTPException
from sqlalchemy.exc import IntegrityError
from common.database.models import Book, UserPreference 
from typing import List



def create_user_preference(db: Session, preference: UserPreferenceSchema, username: str):
    db_preference = UserPreference(
        username=username,
        preference_type=preference.preference_type,
        preference_value=preference.preference_value
    )
    db.add(db_preference)
    db.commit()
    db.refresh(db_preference)
    return db_preference

def get_user_preferences(db: Session, username: str):
    return db.query(UserPreference).filter(UserPreference.username == username).all()



def toggle_like_book(db: Session, username: str, book_id: int):
    liked_book = db.query(UserPreference).filter_by(username=username, preference_type='liked_book', preference_value=str(book_id)).first()
    if liked_book:
        db.delete(liked_book)
        db.commit()
        return {"message": "Book unliked successfully"}
    else:
        try:
            new_like = UserPreference(username=username, preference_type='liked_book', preference_value=str(book_id))
            db.add(new_like)
            db.commit()
            return {"message": "Book liked successfully"}
        except IntegrityError:
            db.rollback()
            raise HTTPException(status_code=400, detail="Could not like the book")

def get_liked_books(db: Session, username: str) -> List[Book]:
    liked_book_ids = db.query(UserPreference.preference_value).filter_by(username=username, preference_type='liked_book').all()
    liked_book_ids = [int(id[0]) for id in liked_book_ids] 
    liked_books = db.query(Book).filter(Book.book_id.in_(liked_book_ids)).all()
    return liked_books