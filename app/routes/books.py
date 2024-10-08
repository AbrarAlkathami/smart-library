from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from typing import List
from common.database.database import get_db
from schemas.book import *
from middleware.auth import get_current_user, admin_required
from middleware.logger import log_user_activity
from common.CRUD.book_crud import *
from common.database.chromaDB import*


router = APIRouter()

@router.get("/books", response_model=List[BookResponseSchema], tags=["Books"], operation_id="get_books_list")
def get_books_route(db: Session = Depends(get_db)):
    print(get_books(db))
    return get_books(db)

@router.post("/books", response_model=BookSchema, tags=["Books"], operation_id="create_book_record")
def create_book_route(authors: List[str], book: BookSchema, db: Session = Depends(get_db), current_user: dict = Depends(admin_required)):
    log_user_activity(db, current_user['username'], "Book creation")
    return create_book(db, authors, book)

@router.get("/books/mostTrending", response_model=List[BookResponseSchema], tags=["Books"])
def get_most_trending_books_route(db: Session = Depends(get_db)):
    return get_books_by_most_trending(db)

@router.get("/books/recentlyAdded", response_model=List[BookResponseSchema], tags=["Books"])
def get_most_recently_added_books_route(db: Session = Depends(get_db)):
    return get_books_by_most_recently_added(db)

@router.get("/books/recentPublishedYear", response_model=List[BookResponseSchema], tags=["Books"], operation_id="get_most_recent_published_year_books")
def get_most_recent_published_year_books_route(db: Session = Depends(get_db)):
    return get_books_by_most_recent_published_year(db)

@router.get("/books/mostrecentpublishedyear", response_model=List[BookResponseSchema], tags=["Books"], operation_id="get_most_recent_published_year_books")
def get_most_recent_published_year_books_route(db: Session = Depends(get_db)):
    return get_books_by_most_recent_published_year(db)

@router.get("/books/earliestPublishedYear", response_model=List[BookResponseSchema], tags=["Books"])
def get_earliest_published_year_books_route(db: Session = Depends(get_db)):
    return get_books_by_earliest_published_year(db)

@router.get("/books/topRated", response_model=List[BookResponseSchema], tags=["Books"])
def get_top_rated_books_route(db: Session = Depends(get_db)):
    return get_books_by_top_rated(db)

@router.get("/books/leastRated", response_model=List[BookResponseSchema], tags=["Books"])
def get_least_rated_books_route(db: Session = Depends(get_db)):
    return get_books_by_least_rated(db)

@router.get("/books/recommended", response_model=List[BookSchema], tags=["Recommendations"])
def get_recommended_books_route(db: Session = Depends(get_db), current_user: dict = Depends(get_current_user)):
    try:
        log_user_activity(db, current_user['username'], "Viewed their recommendations")
        return get_recommended_books(db, current_user["username"])
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    

@router.get("/books/{book_id}", response_model=BookResponseSchema, tags=["Books"], operation_id="get_book_by_id")
def get_book_route(book_id: int, db: Session = Depends(get_db), current_user: dict = Depends(get_current_user)):
    book = get_book_by_id(db, book_id)
    if not book:
        raise HTTPException(status_code=200, detail="Book not found")
    log_user_activity(db, current_user['username'], f"Searched for book with id: {book_id}")
    return book

@router.get("/books/{book_title}", response_model=BookResponseSchema, tags=["Books"], operation_id="get_book_by_title")
def get_book_route(book_title: str, db: Session = Depends(get_db)):
    book = get_book_by_title(db, book_title)
    if not book:
        raise HTTPException(status_code=404, detail="Book not found")
    return book

@router.put("/books/{book_id}", response_model=BookSchema, tags=["Books"], operation_id="update_book_record")
def update_book_route(book_id: int, book: BookSchema, db: Session = Depends(get_db), current_user: dict = Depends(admin_required)):
    log_user_activity(db, current_user['username'], "Book update")
    return update_book(db, book_id, book)

@router.delete("/books/{book_id}", tags=["Books"])
def delete_book_route(book_id: int, db: Session = Depends(get_db), current_user: dict = Depends(admin_required)):
    log_user_activity(db, current_user['username'], "Book deletion")
    return delete_book(db, book_id)


@router.get("/books/search/{user_query}", response_model=List[BookResponseSchema], tags=["Books"], operation_id="search_books")
def search_books_route(user_query: str, db: Session = Depends(get_db)):
    books = search_books(db, user_query)
    return books

@router.get("/books/search/similarity{user_query}")
def get_book_similarity(user_query: str, db: Session = Depends(get_db)):
    similarity_text_result = get_similarity(user_query)
    if not similarity_text_result:
        raise HTTPException(status_code=404, detail="No similar books found.")
    # log_user_activity(db, current_user['username'], f"Searched for book with query: {user_query}")
    return {"results": similarity_text_result}
