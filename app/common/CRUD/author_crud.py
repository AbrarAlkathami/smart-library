from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from fastapi import HTTPException
from typing import List
from ..database.models import Author , Book
from schemas.author import AuthorSchema

def get_authors(db: Session) -> List[Author]:
    return db.query(Author).all()

def get_author_by_id(db: Session, author_id: int) -> Author:
    return db.query(Author).filter(Author.author_id == author_id).first()

# def get_author_id_by_name(db: Session, author_name: str) -> Author:
#     author = db.query(Author).filter(Author.name == author_name).first()
#     if author:
#         print(author)
#         return author.author_id
#     return None

def get_author_by_name(db: Session, author_name: str) -> Author:
    return db.query(Author).filter(Author.name == author_name).first()

def create_or_get_author(db: Session, author_name: str) -> Author:
    author_instance = db.query(Author).filter(Author.name == author_name).first()
    
    if not author_instance:
        author_instance = create_author(db, AuthorSchema(name=author_name))
    
    return author_instance


def create_author(db: Session, author: AuthorSchema) -> Author:
    
    db_author = Author(**author.dict())
    
    try:
        db.add(db_author)
        db.commit()
        db.refresh(db_author)
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=409, detail="Author already exists")

    return db_author



def update_author(db: Session, author_id: int, author: AuthorSchema) -> Author:
    db_author = db.query(Author).filter(Author.author_id == author_id).first()
    if not db_author:
        raise ValueError("Author not found")

    db_author.name = author.name
    db_author.biography = author.biography

    try:
        db.commit()
        db.refresh(db_author)
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=409, detail="Author already exists")

    return db_author


def delete_author(db: Session, author_id: int) -> None:
    db_author = db.query(Author).filter(Author.author_id == author_id).first()
    if not db_author:
        raise ValueError("Author not found")
    
    db.delete(db_author)
    db.commit()

