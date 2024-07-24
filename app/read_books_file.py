import pandas as pd
from sqlalchemy.orm import Session
from common.CRUD.book_crud import *
from common.CRUD.author_crud import *
from common.database.database import session_local, get_db
from schemas.author import AuthorSchema
from schemas.book import BookSchema

def process_csv(file_path: str, db: Session):
    df = pd.read_csv(file_path, usecols=['title' , 'subtitle', 'authors', 'categories', 'published_year', 'description', 'average_rating', 'num_pages', 'ratings_count'])

    for index, row in df.iterrows():
        title = row['title']
        subtitle= row['subtitle']
        author_names = row['authors'].split(';')  
        genre = row['categories']
        published_year=row['published_year']
        description = row['description']
        average_rating = row['average_rating']
        num_pages = row['num_pages']
        ratings_count = row['ratings_count']

        # Create or retrieve the book
        book_data = BookSchema(title=title, subtitle=subtitle, genre=genre, published_year=published_year, description=description, average_rating=average_rating, num_pages=num_pages, ratings_count=ratings_count)
        db_book = create_book(db, book_data)
        
        # Create authors and associate them with the book
        for author_name in author_names:
            # Check if author exists
            db_author = get_author_by_name(db, author_name)
            if not db_author:
                author_data = AuthorSchema(name=author_name, biography=None)
                db_author = create_author(db, author_data)

            # Associate the author with the book
            associate_book_with_author(db, title, author_name)
            
# Ensure to manage sessions properly
db_session = session_local()
process_csv('cleaned_books.csv', db_session)
db_session.close()