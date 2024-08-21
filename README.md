
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

## Usage
  #### Accessing the frontend
  - Ensure the FastAPI server is running.


## UI Prototype

<img width="1512" alt="Screenshot 1446-02-16 at 5 31 15 PM" src="https://github.com/user-attachments/assets/9cb211cb-7a4d-4b82-9b6b-ae3fa562f7ec"># smart-library
<img width="1512" alt="Screenshot 1446-02-16 at 5 26 30 PM" src="https://github.com/user-attachments/assets/f2e608c4-4805-4571-8d12-53fb7b3fecfa">
<img width="1512" alt="Screenshot 1446-02-16 at 5 26 49 PM" src="https://github.com/user-attachments/assets/cef33e6a-7947-4ede-9e3f-233a8fbd082e">

<img width="1512" alt="Screenshot 1446-02-16 at 5 25 16 PM" src="https://github.com/user-attachments/assets/c739ac2f-2fa0-460a-b1e3-4d05c87defe5">
<img width="1512" alt="Screenshot 1446-02-16 at 5 25 28 PM" src="https://github.com/user-attachments/assets/da09a379-37f6-41a7-a295-13d21e7990e5">


### LogIn SignUp form
<img width="1512" alt="Screenshot 1446-02-16 at 5 27 01 PM" src="https://github.com/user-attachments/assets/39b92c17-a21e-4e40-8944-83d70ee77bb6">
<img width="1512" alt="Screenshot 1446-02-16 at 5 27 51 PM" src="https://github.com/user-attachments/assets/db9357f2-0d41-44c0-8333-dce412120de5">
<img width="1512" alt="Screenshot 1446-02-16 at 5 27 38 PM" src="https://github.com/user-attachments/assets/258323f1-da28-47d8-ac29-71bfd139c832">


### User Prefrences 

<img width="1512" alt="Screenshot 1446-02-16 at 5 28 03 PM" src="https://github.com/user-attachments/assets/8a7fc2fd-0d85-4c47-9727-438b8c8db54c">
<img width="1512" alt="Screenshot 1446-02-16 at 5 29 38 PM" src="https://github.com/user-attachments/assets/c10fa8f0-4e99-47da-8bce-fdbb56bd15c3">

