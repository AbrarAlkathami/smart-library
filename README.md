# smart-library
Welcome to the Smart library project! This repository contains the implementation of a comprehensive book management system with both a chatbot interface and a book library interface.

## Overview
The Smart Bookstore project is designed to provide a versatile platform for managing and interacting with a collection of books. It includes:

- A FastAPI backend.
- Two frontends:
  - Streamlit for a chatbot interface.
  - HTML, CSS, and JavaScript for a book library interface.
## Features
### Chatbot Interface (Streamlit)
  - Add a Book: Allows users to add a new book to the database.
  - Display Relevant Books: Shows a list of books relevant to the user's query.
  - Book Summary: Provides a summary of any book in the database.
  - Book Information: Fetches detailed information about a specific book.
### Book Library Interface (HTML/CSS/JS)
  - View All Books: Displays all books in the database.
  - Search for Books: Allows users to search for books by various criteria.

## Technologies Used
  - Backend: 
    - FastAPI
  - Frontend:
    - Chatbot: Streamlit
    - Book Library: HTML, CSS, JavaScript
  - Databases:
    - SQLAlchemy (PostgreSQL)
    - ChromaDB

##Setup Instructions
To set up the project locally, follow these steps:

### Clone the repository:
`
git clone https://github.com/yourusername/smart-bookstore.git
cd smart-bookstore
`
### Install dependencies:
`
poetry install
`

### Set up the database:
`
Ensure PostgreSQL is installed and running.
Create a new database and update the connection details in your FastAPI settings.
`

### Run the FastAPI server:
`
uvicorn app.main:app --reload
`

### Run the Streamlit app:
`
streamlit run app/frontend.py
`

## Usage
  #### Accessing the Chatbot Interface
  - Ensure the FastAPI server is running.
  - Navigate to the Streamlit app URL provided in your terminal to interact with the chatbot.


  #### Accessing the Book Library Interface
  - Ensure the FastAPI server is running.
  - Open index.html in your browser to view and search for books in the library.
