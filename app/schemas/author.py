from pydantic import BaseModel
from typing import Optional
from schemas.book import*

class AuthorSchema(BaseModel):
    name: str
    biography: Optional[str] = None
