from pydantic import BaseModel
from typing import Optional

class BookSchema(BaseModel):
    title: str
    genre: Optional[str] = None
    description: Optional[str] = None
