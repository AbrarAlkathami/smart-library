from fastapi import HTTPException
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from typing import List
from common.database.models import Book, Author, UserPreference , author_association_table
from schemas.book import BookSchema 
from common.CRUD.author_crud import *
from common.CRUD.books_chroma_crud import *

def get_books(db: Session):
    return db.query(Book).all()

def get_book_by_id(db: Session, book_id: int):
    return db.query(Book).filter(Book.book_id == book_id).first()

def get_book_by_title(db: Session, title: str):
    return db.query(Book).filter(Book.title == title).first()

def create_book(db: Session, book: BookSchema):
    # Ensure the author exists in the database
    author_instances = []

    # Handle multiple authors
    # for author_name in book.authors:
        # author_instance = create_or_get_author(db, author_name)
        # author_instances.append(author_instance)

    
    # Create the new book with the author instance
    db_book = Book(**book.dict(exclude={"authors"}))  # Exclude authors as we'll handle it separately
    # db_book.authors = author_instances
    
    try:
        db.add(db_book)
        db.commit()
        db.refresh(db_book)
        add_book_chromadb(db_book.book_id, book)
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=409, detail="Book already exists")

    return db_book

def update_book(db: Session, book_id: int, book: BookSchema):
    db_book = db.query(Book).filter(Book.book_id == book_id).first()
    if not db_book:
        raise HTTPException(status_code=404, detail="Book not found")
    
    db_author = db.query(Author).filter(Author.author_id == book.author_id).first()
    if not db_author:
        raise HTTPException(status_code=404, detail="Author not found")

    db_book.title = book.title
    db_book.author_id = book.author_id
    db_book.genre = book.genre
    db_book.description = book.description

    try:
        db.add(db_book)
        db.commit()
        db.refresh(db_book)
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=409, detail="Book already exists")

    return db_book
def delete_book(db: Session, book_id: int):
    db_book = db.query(Book).filter(Book.book_id == book_id).first()
    if not db_book:
        raise HTTPException(status_code=404, detail="Book not found")
    
    db.delete(db_book)
    db.commit()
    return {"message": "Book deleted successfully"}

def get_recommended_books(db: Session, username: str) -> List[Book]:
    user_preferences = db.query(UserPreference).filter(UserPreference.username == username).all()
    preferred_genres = [pref.preference_value for pref in user_preferences if pref.preference_type == "genre"]

    if not preferred_genres:
        raise ValueError("No preferred genres found for user")

    recommended_books = db.query(Book).filter(Book.genre.in_(preferred_genres)).all()

    if not recommended_books:
        raise ValueError("No books found for preferred genres")

    return recommended_books


def associate_book_with_author(db: Session, book_title: str, author_name: str):
    # Retrieve the Book and Author instances
    book = get_book_by_title(db, book_title)
    author = get_author_by_name(db, author_name)

    if not book:
        raise ValueError(f"Book with title '{book_title}' not found.")

    if not author:
        raise ValueError(f"Author with name '{author_name}' not found.")

    # Check if the association already exists
    association_exists = db.query(author_association_table).filter_by(book_id=book.book_id, author_id=author.author_id).first()
    if association_exists:
        return  # Association already exists, do nothing

    # Create a new association
    db.execute(author_association_table.insert().values(book_id=book.book_id, author_id=author.author_id))
    try:
        db.commit()
    except Exception as e:
        db.rollback()
        raise e