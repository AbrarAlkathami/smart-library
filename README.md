# smart-library

## Overview
Smart Library is a web application that allows users to browse, search, and interact with a collection of books. The application includes features like user authentication, personalized preferences, and an AI-powered chatbot for assisting users. The application is built using modern web technologies and provides an interactive user interface for managing and exploring a vast library of books.

## Features

  ### Book Library:
  - User Authentication: Users can sign up and log in securely.
  - Book Search & Filter: Search for books by title and filter results based on various criteria like publication year, rating, etc.
  - Personalized Recommendations: Users can set preferences for authors and genres to receive tailored recommendations.
  - AI Chatbot: A chatbot interface is available to assist users with finding books and general inquiries.
  - Book Rating: Users can view the rating average for books.
  - Dynamic Book Display: The application dynamically loads and displays books based on user interactions, including filtering options.
      
  ### AI Chatbot:
  - Display Relevant Books: Shows a list of books relevant to the user's query.
  - Book Summary: Provides a summary of any book in the database.
  - Book Information: Fetches detailed information about a specific book.
  - Books Recommendation: Shows a list of recommended books based on the user query.

## Technologies Used
- Backend:
  - FastAPI
  - Python
- Frontend:
  - React ( TypeScript )
  - CSS Modules
- Databases:
    - SQLAlchemy ( PostgreSQL )
    - ChromaDB
- AI Integration:
    - LangChain
    - LangGraph
    - Ollama 3.1

## Setup Instructions
To set up the project locally, follow these steps:

### Clone the repository:
`
git clone https://github.com/ILABRAR1/smart-library.git
`

`
cd smart-library
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
Create a new database and update the connection details in connectionDB file in app folder for the FastAPI.
`

### Run the FastAPI server:
`
cd app
`

`
uvicorn app:app --reload
`

### Run the react:
In new terminal.

`
cd smart-library
npm start
`

## Usage
  #### Accessing the frontend
  - Ensure the FastAPI server is running.

