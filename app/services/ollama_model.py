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


store = {}

def get_session_history(session_id: str) -> BaseChatMessageHistory:
    if session_id not in store:
        store[session_id] = InMemoryChatMessageHistory()
    return store[session_id]


def format_docs(docs):
    # Concatenate all relevant data from each metadata entry
    formatted_data = "\n\n".join(
        f"Title: {doc.get('title', 'No Title')}, "
        f"Authors: {doc.get('authors', 'No Authors')}, "
        f"Average Rating: {doc.get('average_rating', 'No Rating')}, "
        f"Description: {doc.get('description', 'No Description')}, "
        f"Genre: {doc.get('genre', 'No Genre')}, "
        f"Num Pages: {doc.get('num_pages', 'No Page Number')}, "
        f"Published Year: {doc.get('published_year', 'No Publication Year')}, "
        f"Ratings Count: {doc.get('ratings_count', 'No Ratings Count')}"
        for doc in docs
    )
    return formatted_data

def generate_response_with_context(system_prompt: str, query: str):
    print("this is the gerate a response with context")
    llm = OllamaLLM(model="llama3.1", n_gpu_layers=1, n_batch=512, n_ctx=2048, f16_kv=True, verbose=True)

    # Update the placeholder to match the invoke call
    prompt = ChatPromptTemplate.from_messages([
        ("system", system_prompt),
        ("human", "{query}"),  # This should be used in the placeholder
    ])

    context = get_similarity(query)  # Assuming this returns a list of dictionaries
    formatted_context = format_docs(context)  # Format the metadata for the RAG chain

    rag_chain = (
        {"context": formatted_context, "question": RunnablePassthrough()}
        | prompt
        | llm
        | StrOutputParser()
    )
    print("This is the RAG chain:", rag_chain)
    response = rag_chain.invoke({"query": query})
    print("We got the response:", response)
    return response
    
    # print("this is the gereate a response with context and we got the context: " , context)
    # question_answer_chain = create_stuff_documents_chain(llm, prompt)
    # print("we create the stuff documents chain : " ,question_answer_chain)

    # print("\n\n\nType of context: ", type(context))
    # print("Type of question_answer_chain: ", type(question_answer_chain))
    # chain = create_retrieval_chain(context, question_answer_chain)
    # print("we create retrival chain : " ,chain)

    # # The key used here needs to be 'query' as defined in the template
    
    # response = chain.invoke({"query": query})
    # print("we got the response : " ,response)
    # print(response)
    # return response
     

def generate_response(system_prompt: str, query: str):
    llm = OllamaLLM(model="llama3.1", n_gpu_layers=1, n_batch=512, n_ctx=2048, f16_kv=True, verbose=True)

    # Update the placeholder from {query} to {input}
    prompt = ChatPromptTemplate.from_messages([
        ("system", system_prompt),
        ("human", query),  # This now matches the key in the invoke call below
    ])
    
    chain = prompt | llm
    print("get the chain")
    response = chain.invoke({"input": query})  # This key matches the template placeholder
    print("get the chain invoke response")
    print(response)
    return response

def generate_response_intent(db: Session ,session_id: str, query: str):

    intent_prompt = f"You are a helpful AI bot, specialized in classifying book data queries. When a user submits a query, classify it as: '{query}'. Determine if the user is asking to add a book, filter data, display relevant books, request a summary, or view book information. Respond with 'add_book', 'filter', 'display_books', 'summary', 'information', or 'unknown' and provide details if applicable. If the requested data is not found, simply respond, 'I am sorry I do not have that information.' Avoid providing any additional information."
    # intent_response = llm.generate_one(intent_prompt).strip().lower()
    intent_response= generate_response(intent_prompt, query)
    print(intent_response)
    if 'add_book' in intent_response:
        print("in add book if section")
        add_book_prompt = (
            f"Format the book information in JSON Include the authors. If there is any empty value, make sure it stores as null. jsut return the json without any explanation"
            f"Example: 'title': 'book title', 'subtitle': 'subtitle', 'published_year': 'published year', 'average_rating': 'average rating', 'num_pages': 'number of pages', 'ratings_count': 'ratings count', 'genre': 'genre', 'description': 'description', 'authors': ['author1', 'author2']."
            f"Query: '{query}'"
        )
        print("trying to get the response")
        book_info = generate_response(add_book_prompt, query)
        print("we get the response")
        try:
            print("trying to load json response")
            book_info = json.loads(book_info)
            print("finish response loads")
        except json.JSONDecodeError:
            raise HTTPException(status_code=400, detail="Failed to parse book information JSON")
        print("start storing the create book in DB ")
        result = create_book(db, book_info.get('authors', []), book_info)
        return result
    # elif 'filter' in intent_response:
    #     filters = parse_filters_from_query(query)
    #     filtered_books = get_books_by_filter(db, filters)
    #     return display_books_as_table(filtered_books)
    elif 'display_books' in intent_response:
        display_books_prompt = (
            f"When asked to display book information, you will present the details in a structured table format. Ensure the table includes columns for the following attributes: Title, Authors, Published Year, Genre, Average Rating, Number of Pages, and Ratings Count. If any data is missing for a book, leave the corresponding cell empty. Before displaying the information, make sure that the books you are about to show are exactly the ones requested by the user. Cross-verify the titles and authors or description to ensure 100% accuracy."
            f"Query: '{query}'"
        )
        # Assuming you have a way to get relevant books
        response = generate_response_with_context(display_books_prompt , query)  # Define this function
        return response
    elif 'summary' in intent_response or 'chat' in intent_response:
        summary_books_prompt = (
            f"When asked to summarize a book description, first ensure that the book is within the provided context. If the book information is not available, respond with (I don't have this book's information.) If the book is found, provide a concise and clear summary that captures the essence of the book's plot, main themes, and key points. Ensure the summary is brief, no longer than a few sentences, and avoids unnecessary details or spoilers."
            f"Query: '{query}'"
        )
        response = generate_response_with_context(summary_books_prompt , query)  # Define this function
        return response
    # elif 'information' in intent_response:
    #     book_id = extract_book_id_from_query(query)  # Define this function to extract book ID
    #     return display_book_information(db, book_id)
    else:
        print("ELSE SECTION")
        system_prompt = (
            "Check if the question is related 100% to the {context} if not related say (I don't have this information)"
        )
        response=generate_response_with_context(system_prompt,query)
        return response
        
# "You are a helpful AI bot, specialized in useing the given context to answer the question. If the answer was not related to the context say ( I don't have this information). "
#             "Use three sentences maximum and keep the answer concise. "
#             "Context: {context}"
    # # Continue with generating the response
    # system_prompt = (
    #     "You are an assistant for Smart Library. "
    #     "Use the given context to answer the question. If you don't know the answer, say you don't know. "
    #     "Use three sentences maximum and keep the answer concise. "
    #     "Context: {context}"
    # )
    
    # prompt_template = ChatPromptTemplate.from_messages(
    #     [("system", system_prompt), ("human", "{input}")]
    # )
    
    # question_answer_chain = create_stuff_documents_chain(llm, prompt_template)
    # chain = create_retrieval_chain(context, question_answer_chain)
    
    # response = chain.invoke({"input": query})
    # return response




#     prompt = ChatPromptTemplate.from_messages([
#     ("system", "You are a helpful AI bot named Lucky that retrieves book data from the database. If the requested data is not available in the database, simply respond with 'I am sorry I do not have that information.' Do not provide any other information."),
#     ("human", "Hello, how are you doing?"),
#     ("ai", "I'm doing well, thanks! How can I assist you with book data today?"),
#     ("human", "{user_input}")
# ])