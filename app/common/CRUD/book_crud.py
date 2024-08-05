from fastapi import HTTPException
from sqlalchemy.orm import Session , joinedload
from sqlalchemy.exc import IntegrityError
from typing import List
from common.database.models import Book, Author, UserPreference , author_association_table
from schemas.book import BookSchema 
from schemas.author import*
from common.CRUD.author_crud import *
from common.CRUD.books_chroma_crud import *
from sqlalchemy import case
from datetime import datetime


def book_to_dict(book):
    return {
        "title": book.title,
        "subtitle": book.subtitle,
        "published_year": book.published_year,
        "average_rating": book.average_rating,
        "num_pages": book.num_pages,
        "ratings_count": book.ratings_count,
        "genre": book.genre,
        "description": book.description,
        "thumbnail": book.thumbnail,
        "authors": [author_to_dict(author) for author in book.authors]
    }

def author_to_dict(author):
    return {
        "name": author.name,
        "biography" :author.biography
    }


def get_books(db: Session)-> List[dict]:
    return db.query(Book).options(joinedload(Book.authors)).all()

def get_book_by_id(db: Session, book_id: int) -> BookSchema:
    return db.query(Book).filter(Book.book_id == book_id).first()

#delete this function( not working + in the search for a book I'm using search_books function), oh it's used with associate_book_with_author
def get_book_by_title(db: Session, title: str) -> BookSchema:
    book = db.query(Book).filter(Book.title.ilike(f"%{title}%")).first()
    if book:
        return BookSchema.from_orm(book)
    return None

def search_books(db: Session, query: str) -> List[dict]:
    books = db.query(Book).filter(Book.title.ilike(f"%{query}%")).options(joinedload(Book.authors)).all()
    return [book_to_dict(book) for book in books]

def create_book(db: Session, authors: List[str], book: BookSchema):
    author_instances = []

    # Handle multiple authors
    for author_name in authors:
        author_instance = create_or_get_author(db, author_name)
        author_instances.append(author_instance)

    # Create the new book with the author instance
    db_book = Book(**book.dict(exclude={"authors"}))  # Exclude authors as we'll handle it separately
    try:
        db.add(db_book)
        db.commit()
        db.refresh(db_book)
        add_book_chromadb(db_book.book_id, authors, book)
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=409, detail="Book already exists")
    return db_book

def update_book(db: Session, book_id: int, book: BookSchema):
    db_book = db.query(Book).filter(Book.book_id == book_id).first()
    if not db_book:
        raise HTTPException(status_code=404, detail="Book not found")
    
    db_book.title = book.title
    db_book.subtitle = book.subtitle
    db_book.published_year = book.published_year
    db_book.average_rating = book.average_rating
    db_book.num_pages = book.num_pages
    db_book.ratings_count = book.ratings_count
    db_book.genre = book.genre
    db_book.description = book.description
    db_book.thumbnail = book.thumbnail

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

def get_recommended_books(db: Session, username: str) -> List[BookSchema]:
    preferences = db.query(UserPreference).filter(UserPreference.username == username).all()
    preferred_authors = []
    preferred_genres = []

    for pref in preferences:
        if pref.preference_type == 'author':
            preferred_authors.append(pref.preference_value)
        elif pref.preference_type == 'genre':
            preferred_genres.append(pref.preference_value)

    print(f"User: {username}")
    print(f"Preferred Authors: {preferred_authors}")
    print(f"Preferred Genres: {preferred_genres}")

    # Query vector DB for authors
    books_by_authors = []
    for author in preferred_authors:
        author_results = get_similarity(author)
        print("Author Result: ", author_results)
        if isinstance(author_results, list) and len(author_results) > 0 and isinstance(author_results[0], list):
            print("isinstance result: ", author_results)
            author_results = author_results[0]
            print("isinstance result: ", author_results)

        print(f"Results for author '{author}': {author_results}")
        books_by_authors.extend(author_results)

    # Query vector DB for genres
    books_by_genres = []
    for genre in preferred_genres:
        genre_results = get_similarity(genre)
        if isinstance(genre_results, list) and len(genre_results) > 0 and isinstance(genre_results[0], list):
            genre_results = genre_results[0]  # Extract the inner list if nested
        
        print(f"Results for genre '{genre}': {genre_results}")
        books_by_genres.extend(genre_results)

    unique_books = {f"{book['authors']}-{book['title']}": book for book in books_by_authors + books_by_genres}
    print(f"Unique Books: {unique_books}")

    books = []
    for book in unique_books.values():
        author_names = book['authors'].split(', ')
        authors = [AuthorSchema(name=name) for name in author_names]
        book['authors'] = authors

        books.append(BookSchema(**book))

    return books

def get_books_by_most_recently_added(db: Session) -> List[Book]:
    return db.query(Book).order_by(Book.book_id.desc()).all()

def get_books_by_most_recent_published_year(db: Session) -> List[Book]:
    books = db.query(Book).order_by(
        case(
            (Book.published_year == None, 1), 
            else_=0
        ),
        Book.published_year.desc()
    ).all()
    return [book_to_dict(book) for book in books]

def get_books_by_earliest_published_year(db: Session) -> List[Book]:
    current_year = datetime.now().year
    books = db.query(Book).order_by(
        case(
            (Book.published_year == 0, current_year), 
            else_=Book.published_year
        ),
        Book.published_year.asc()
    ).all()
    return [book_to_dict(book) for book in books]

def get_books_by_top_rated(db: Session) -> List[Book]:
    books = db.query(Book).order_by(
        case(
            (Book.average_rating == None, 1), 
            else_=0
        ),
        Book.average_rating.desc()
    ).all()
    return [book_to_dict(book) for book in books]

def get_books_by_least_rated(db: Session) -> List[Book]:
    return db.query(Book).order_by(Book.average_rating.asc()).all()

def get_books_by_most_trending(db: Session) -> List[Book]:

    weight_avg_rating = 0.4
    weight_ratings_count = 0.6

    books = db.query(Book).all()

    for book in books:

        normalized_avg_rating = (book.average_rating or 0) / 5.0  
        normalized_ratings_count = (book.ratings_count or 0) / 10000000.0  

       
        book.trending_score = (
            weight_avg_rating * normalized_avg_rating +
            weight_ratings_count * normalized_ratings_count 
        )
    trending_books = sorted(books, key=lambda b: b.trending_score, reverse=True)
    
    return trending_books
def associate_book_with_author(db: Session, book_title: str, author_name: str):
    book = get_book_by_title(db, book_title)
    author = get_author_by_name(db, author_name)

    if not book:
        raise ValueError(f"Book with title '{book_title}' not found.")

    if not author:
        raise ValueError(f"Author with name '{author_name}' not found.")

    association_exists = db.query(author_association_table).filter_by(book_id=book.book_id, author_id=author.author_id).first()
    if association_exists:
        return  

    db.execute(author_association_table.insert().values(book_id=book.book_id, author_id=author.author_id))
    try:
        db.commit()
    except Exception as e:
        db.rollback()
        raise e
    
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
            return {"message": "Failed to like the book"}

def get_liked_books(db: Session, username: str) -> List[Book]:
    liked_book_ids = db.query(UserPreference.preference_value).filter_by(username=username, preference_type='liked_book').all()
    liked_book_ids = [int(id[0]) for id in liked_book_ids]  # Convert list of tuples to list of ints
    liked_books = db.query(Book).filter(Book.book_id.in_(liked_book_ids)).all()
    return liked_books