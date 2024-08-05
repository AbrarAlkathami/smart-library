# smart-library
This repository contains the implementation of a comprehensive book management system with both a chatbot and a book library.

## Overview
The Smart library project is designed to provide a versatile platform for managing and interacting with a collection of books. It includes: backend, frontend , database, llms.
 
## Features
### Chatbot:
  - Add a Book: Allows users to add a new book to the database.
  - Display Relevant Books: Shows a list of books relevant to the user's query.
  - Book Summary: Provides a summary of any book in the database.
  - Book Information: Fetches detailed information about a specific book.
### Book Library:
  - View All Books: Displays all books in the database.
  - Search for Books: Allows users to search for books by various criteria.

## Technologies Used
- Backend:
  - FastAPI
- Frontend:
  - React ( TypeScript )
- Databases:
    - SQLAlchemy (PostgreSQL)
    - ChromaDB

## Setup Instructions
To set up the project locally, follow these steps:

### Clone the repository:
`
git clone https://github.com/ILABRAR1/smart-library.git
`

`
cd smart-bookstore
`
### Install dependencies:
`
poetry install
`

`
npm install
`

### Set up the database:
`
Ensure PostgreSQL is installed and running. 
Create a new database and update the connection details in your FastAPI settings.
`

### Run the FastAPI server:
`
cd app
`

`
uvicorn app.main:app --reload
`

### Run the react:
`
cd smart-library
npm start
`

## Usage
  #### Accessing the frontend
  - Ensure the FastAPI server is running.

