from pydantic import BaseModel
from typing import Optional , List

class BookSchema(BaseModel):
    title: str
    subtitle : Optional[str] = None 
    authors: Optional[List[str]] = None
    published_year: Optional[int] = None
    average_rating: Optional[float] = None
    num_pages: Optional[int] = None
    ratings_count: Optional[int] = None
    genre: Optional[str] = None
    description: Optional[str] = None

