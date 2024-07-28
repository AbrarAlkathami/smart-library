from langchain_ollama.llms import OllamaLLM
from langchain_core.chat_history import BaseChatMessageHistory
from langchain_core.chat_history import InMemoryChatMessageHistory
from langchain_core.prompts import ChatPromptTemplate
from common.CRUD.books_chroma_crud import get_similarity
from langchain.chains.retrieval import create_retrieval_chain
from langchain.chains.combine_documents import create_stuff_documents_chain
from typing import TypedDict, Annotated, List, Union
from langchain_core.agents import AgentAction, AgentFinish
import operator
from langchain_core.runnables import RunnablePassthrough
from langchain_core.tools import tool
from common.CRUD.book_crud import *
from common.CRUD.author_crud import *
from langchain_core.output_parsers import StrOutputParser
from sqlalchemy.orm import Session
import json
from langchain_community.chat_message_histories import SQLChatMessageHistory
from langchain_core.messages import HumanMessage,AIMessage
from langchain_core.runnables.history import RunnableWithMessageHistory


def format_docs(docs):
    formatted_data = "\n\n".join(
        f"Title: {doc.get('title', 'No Title')}, "
        f"Authors: {doc.get('authors', 'No Authors')}, "
        f"Average Rating: {doc.get('average_rating', 'No Rating')}, "
        f"Description: {doc.get('description', 'No Description')}, "
        f"Genre: {doc.get('genre', 'No Genre')}, "
        f"Num Pages: {doc.get('num_pages', 'No Page Number')}, "
        f"Published Year: {doc.get('published_year', 'No Publication Year')}, "
        f"Ratings Count: {doc.get('ratings_count', 'No Ratings Count')}"
        for doc in docs if isinstance(doc, dict)
    )
    return formatted_data

def get_session_history(session_id):
    return SQLChatMessageHistory(session_id, "sqlite:///memory.db")

store = {}

def get_session_history(session_id: str) -> BaseChatMessageHistory:
    if session_id not in store:
        store[session_id] = InMemoryChatMessageHistory()
    return store[session_id]

def generate_response_with_context(system_prompt: str,session_id: str, query: str):
    history = get_session_history(session_id)

    print("This is the generate a response with context function")
    
    llm = OllamaLLM(model="llama3.1", n_gpu_layers=1, n_batch=512, n_ctx=2048, f16_kv=True, verbose=True)

    prompt = ChatPromptTemplate.from_messages([
        ("system", system_prompt),
        ("human", query),
    ])
    print(f"Created ChatPromptTemplate")

    context = get_similarity(query)
    print("Retrieved context:", context)

    rag_chain = (
        RunnablePassthrough()  
        | (lambda x: {"context": context, "query": query , "system_prompt": system_prompt})  
        | prompt
        | llm
        | StrOutputParser()
    )

    print("This is the RAG chain:", rag_chain)

    response = rag_chain.invoke({"query": query})
    print("We got the response:", response)
    history.add_messages([
        HumanMessage(content=query),
        AIMessage(content=response)
    ])
    return response

def generate_response(system_prompt: str, session_id: str, query: str):
    history = get_session_history(session_id)
    llm = OllamaLLM(model="llama3.1", n_gpu_layers=1, n_batch=512, n_ctx=2048, f16_kv=True, verbose=True)

    prompt = ChatPromptTemplate.from_messages([
        ("system", system_prompt),
        ("human", query),
    ])
    
    chain = prompt | llm
    print("get the chain")
    response = chain.invoke({"\'title\'": query})
    history.add_messages([
        HumanMessage(content=query),
        AIMessage(content=response)
    ])
    return response

def generate_response_intent(db: Session, session_id: str, query: str):
    intent_prompt = f"You are specialized in classifying book data queries. When a user submits a query, classify it as: '{query}'. Determine if the user is asking to add a book, display relevant books, request a summary, or ask for book information. Respond with 'add_book', 'display_books', 'list_all_books', 'summary', 'information', if it does not one of the choices return 'unkown'. Avoid providing any additional information."
    
    intent_response = generate_response(intent_prompt, session_id, query)
    print(intent_response)
    if 'add_book' in intent_response:
        add_book_prompt = (
            f"Format the book information in JSON Include the authors. If there is any empty value, make sure it stores as null. jsut return the json without any explanation"
            f"Example: 'title': 'book title', 'subtitle': 'subtitle', 'published_year': 'published year', 'average_rating': 'average rating', 'num_pages': 'number of pages', 'ratings_count': 'ratings count', 'genre': 'genre', 'description': 'description', 'authors': ['author1', 'author2']."
            f"Query: '{query}'"
        )

        book_info = generate_response(add_book_prompt, session_id, query)
        
        try:

            book_info = json.loads(book_info)
            print("this book has been loaded as json")
        except json.JSONDecodeError:
            raise HTTPException(status_code=400, detail="Failed to parse book information JSON")
        print("start add it to books DB")
        result = create_book(db, book_info.get('authors', []), book_info)
        return result
    
    elif 'display_books' in intent_response or 'list_all_books' in intent_response:
        display_books_prompt = (
            "Display books based on the user's query. Provide the list of books in a table format with the relevant details. "
            "Do not provide anything outside of the query context."
            "context: {context}"
            "the return value must be as table with books information"
        )
        
        response = generate_response_with_context(display_books_prompt, session_id, query)
        return response
    
    elif 'summary' in intent_response:
        summary_books_prompt = (
            "Summarize the book description effectively. Follow these steps: "
            "1- Verify if the requested book information matches the provided context. "
            "2- Identify the description for the mentioned book in the user's query. "
            "3- If the book information is unavailable, respond with 'I don't have this book's information.' "
            "4- If the book description is available, deliver a concise summary that encapsulates the main plot. "
            "Ensure the summary is brief, ideally no more than two sentences. Avoid providing any additional information."
        )
        
        response = generate_response_with_context(summary_books_prompt, session_id, query)
        return response

    elif 'information' in intent_response:
        print("info")
        information_book_prompt = (
            "Answer questions specifically related to the provided context. Ensure responses are precise, relevant, and informative. "
            "Do not provide any information not found in the database."
        )
        
        response = generate_response_with_context(information_book_prompt, session_id, query)
        return response

    else:
        print("else")
        system_prompt = (
            "you can not give the user this service. your job is just to add a book to DB, display relevant books, response with a summary for any book, or ask for book information. Avoid providing any additional information."
        )
        response = generate_response_with_context(system_prompt, session_id, query)
        return response
