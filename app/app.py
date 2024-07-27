from fastapi import FastAPI, HTTPException, Depends
from routes import users, books, authors
from common.database.database import *
from services.ollama_model import *
from sqlalchemy.orm import Session
from pydantic import BaseModel

app = FastAPI()

app.include_router(users.router)
app.include_router(books.router)
app.include_router(authors.router)

class ChatRequest(BaseModel):
    query: str
    session_id: str

@app.get("/")
def read_root():
    return {"message": "Welcome to the Simple User API"}

@app.get("/health_check")
def health_check():
    return {"message": "API is running"}

@app.post("/chat")
def chat_with_model(request: ChatRequest , db: Session = Depends(get_db)):
    try:
        response = generate_response_intent(db, request.session_id, request.query)
        return {"response": response}
    except Exception as e:
        print(f"Error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


Base.metadata.create_all(engine)
