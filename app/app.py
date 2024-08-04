from fastapi import FastAPI, HTTPException, Depends, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from routes import users, books, authors ,preferences
from common.database.database import *
from services.ollama_model import *
from sqlalchemy.orm import Session
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"],  
    allow_headers=["*"], 
)

app.include_router(users.router)
app.include_router(books.router)
app.include_router(authors.router)
app.include_router(preferences.router)

# Serve static files
app.mount("/static", StaticFiles(directory="frontend"), name="static")
# Set up Jinja2 templates
templates = Jinja2Templates(directory="frontend")

class ChatRequest(BaseModel):
    query: str
    session_id: str

@app.get("/", response_class=HTMLResponse)
async def read_books(request: Request):
    return templates.TemplateResponse("books.html", {"request": request})

@app.get("/health_check")
def health_check():
    return {"message": "API is running"}

@app.post("/chat")
def chat_with_model(request: ChatRequest, db: Session = Depends(get_db)):
    try:
        response = generate_response_intent(db, request.session_id, request.query)
        return {"response": response}
    except Exception as e:
        print(f"Error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

Base.metadata.create_all(engine)
