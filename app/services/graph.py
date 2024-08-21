from services.model import classification_model, answer_grader_model, retrieval_grader_model, hallucination_grader_model, rag_model, model, query_rewriter_model, query_keywords, docs_to_tables
from utils.prompts import *
from langchain_ollama.llms import OllamaLLM
from langchain_core.prompts import ChatPromptTemplate,PromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser,PydanticOutputParser,JsonOutputParser, MarkdownListOutputParser
from typing import TypedDict, Dict, Optional , List, Any,Literal
from langgraph.graph import StateGraph , END , START
from chromadb.config import DEFAULT_TENANT, DEFAULT_DATABASE, Settings
import chromadb
from langchain_core.pydantic_v1 import BaseModel, Field
from pprint import pprint
from langgraph.checkpoint.memory import MemorySaver
from common.CRUD.books_chroma_crud import get_similarity

class GraphState(TypedDict):
    question: Optional[str] = None
    classification: Optional[str] = None
    next_node: Optional[str]=None
    documents: Optional[List[str]]=None
    response: Optional[str] = None


def classify_input_node(state):
    question = state["question"]

    system_prompt_classification = """"You are an expert in Understanding and classifying user questions into one of the following categories: search_by_title, search_by_author, search_by_genre, books_in_specific_year, books_with_rating_count, books_with_rating_average, summarize_book, book_thumbnail, title_from_description, recommendation, general_inquiry, or add_book,.
        When a user submits a query:
            - Determine the most appropriate classification.
            - Respond only with a JSON object that includes the classification field.

        Here is the user's question:
        {query}
    """
    classification_response = classification_model(system_prompt_classification, question)
    
    # Update the state with the classification
    state['classification'] = classification_response
    print(classification_response)
    return state

def handle_general_inquiry_node(state):
    question = state["question"]

    general_inquiry_prompt= """You are an expert in handling general inquiries from users. 
    A general inquiry is a casual or open-ended conversation that does not directly request specific information like adding a book, searching by title, or summarizing a book.
    Your task is to respond appropriately to these general conversations, ensuring the user feels engaged and understood. 
    These inquiries may include greetings, small talk, or general questions that don't require specialized knowledge.

    Please respond to the user's query within 2 sentences in a way that encourages a positive and friendly interaction, without providing additional information unrelated to the inquiry.

    Here is the user's query:
    {query}"""

    response= model(general_inquiry_prompt, question)
    state['response']=response
    return state

def handle_add_book_node(state):
    question = state["question"]

    add_book_prompt= """
    You are an expert in processing user requests to add books. 
    The user may or may not provide full details about the book they want to add.
    
    When a user submits a query:
    - If the user provides details about the book, format the information in JSON, including the title, subtitle, published_year, average_rating, num_pages, ratings_count, genre, description, thumbnail, and authors.
    - If the user does not provide details, simply indicate that more information is needed and ask the user to provide the missing details.
    - If there are any fields that are missing or not provided, store them as null.
    - Respond with either the formatted JSON or a request for more information.
    - Do not use bullet points or list formatting in your response. 
    - Respond with either the formatted JSON or a clear request for more information in a single paragraph.


    Example of the JSON format if details are provided:
        {{
            "title": "book title", 
            "subtitle": "subtitle", 
            "published_year": "published year", 
            "average_rating": "average rating", 
            "num_pages": "number of pages", 
            "ratings_count": "ratings count", 
            "genre": "genre", 
            "description": "description", 
            "thumbnail": "thumbnail",
            "authors": ["author1", "author2"]
        }}

    Example of a request for more information if details are missing:
    "It seems that you want to add a book, but I need more details such as the title, authors, etc. Please provide the missing information."


    Here is the user's query:
    {query}
    """

    response=model(add_book_prompt,question)
    state['response']=response
    return state

def retrieve(state):
    question = state["question"]
    new_question=query_keywords(question)
    print(new_question)
    documents = get_similarity(query_text=new_question)
    # to read each metadata easily
    flattened_documents = []
    for sublist in documents:
        for doc in sublist:
            flattened_documents.append(doc)

    state["documents"] = flattened_documents
    return state

def retrieval_grader(state):
    question = state["question"]
    documents = state["documents"]
    relevant_documents = []
    for doc in documents:
        response = retrieval_grader_model(question, doc)
        if response.score == "yes":
            relevant_documents.append(doc)
    
    state["documents"] = relevant_documents
    return state

def query_rewriter(state):
    question = state["question"]
    new_question = query_rewriter_model(question)
    state["question"] = new_question
    return state

def structure_response(state):
    documents = state["documents"]
    formatted_response = docs_to_tables(documents)
    state["response"] = formatted_response
    return state

def generate_response(state):
    query = state["question"]
    documents = state["documents"]
    classification= state['classification']

    if classification== "title_from_description":
        system_prompt=""" 
            You are an expert in identifying books based on user descriptions. 
            Given a user's query that describes a book and a set of documents.
            Your task is to determine whether any of the documents match the description provided in the query. 
            - If a document matches the description, return it.
            - Do not edit any information in the documents. 
            - If multiple documents match, list all relevant documents in the table format. 
            - If no documents match, return "No relevant books found."

            

            Here is the user query:  
            {query} 

            Here is the retrieved documents:  
            {documents}

            """
    elif classification== "summarize_book":
        system_prompt=""" 
            You are an expert in summarizing books. 
            The user will provide a query related to a specific book.
            Your task is to identify the relevant document from the provided documents.
            Summrize the document information in 3 sentenses mention the main information in the book.
            Do not add additional information.
            Do not use bullet points or list formatting in your response. 


            

            Here is the user query:  
            {query} 

            Here is the retrieved documents:  
            {documents}
            """
    elif classification== "book_thumbnail":
        system_prompt=""" """ # additional feature i have to use llava:13b model this refrence can be useful https://anakin.ai/blog/ollama-vision-llava-models/
        
    response = rag_model(system_prompt, query,documents)
    state['response']= response
    return state

def recommendation_node(state):
    query=state['question']

    system_prompt=""" 
    You are an expert in recommending books. 
    The user has provided a query that expresses a specific interest or preference. 
    Your task is to analyze the user query and recommend keywords to the user interest or preference that provied best align with the user's query.
    Return list format of the recommended keywords.
    Do not add additional information.

    
    Here is the user query:  
    {query} 

    """
    recommended_keywords = model(system_prompt, query)
    documents= get_similarity(recommended_keywords)
    flattened_documents = [item for sublist in documents for item in sublist]

    state['documents'] = flattened_documents
    response = docs_to_tables(flattened_documents)
    state['response'] = response
    return state

def check_hallucination(state):

    documents = state["documents"]
    response = state["response"]

    response = hallucination_grader_model(documents, response)
    if response.score == "yes":
        state["next_node"] ="return_answer"
    else:
        state["next_node"] ="generate_response"
    return state
    

def return_answer(state):
    return {"response": state['response']}
    
def decide_next_classification_node(state):
    classification = state['classification']

    if classification == "general_inquiry":
        state["next_node"] = "handle_general_inquiry_node"
    elif classification == "add_book":
        state["next_node"] = "handle_add_book_node"
    elif classification== "recommendation":
        state["next_node"] ='recommendation_node'
    elif classification in ["search_by_title", "search_by_author", "search_by_genre", 
                            "books_with_rating_count", "books_with_rating_average"]:
        state["next_node"] = "retrieve"
    elif classification in ["title_from_description", "summarize_book", "book_thumbnail"]:
        state["next_node"] = "retrieve"

    return state["next_node"]
    
def decide_next_node(state):

    classification = state['classification']

    if classification in ["search_by_title", "search_by_author", "search_by_genre", 
                          "books_with_rating_count", "books_with_rating_average"]:
        if state["documents"]:
            state["next_node"]= "structure_response"
        else:
            state["next_node"]= "rewrite_query"

    elif classification in ["title_from_description", "summarize_book", "book_thumbnail"]:
        if state["documents"] != None:
            state["next_node"]= "generate_response"
        else:
            state["next_node"]= "rewrite_query"

    return state["next_node"]

def langgraph(query):


    workflow = StateGraph(GraphState)
    workflow.add_node("classify_input_node", classify_input_node)
    workflow.add_node("handle_general_inquiry_node", handle_general_inquiry_node)
    workflow.add_node("handle_add_book_node", handle_add_book_node)
    workflow.add_node("retrieve", retrieve)
    workflow.add_node("check_relevance", retrieval_grader)
    workflow.add_node("rewrite_query", query_rewriter)
    workflow.add_node("structure_response", structure_response)
    workflow.add_node("generate_response", generate_response)
    workflow.add_node("check_hallucination", check_hallucination)
    workflow.add_node('recommendation_node', recommendation_node)
    # workflow.add_node("check_answer", check_answer)
    workflow.add_node("return_answer", return_answer)

    workflow.set_entry_point("classify_input_node") 
    workflow.add_conditional_edges(
        "classify_input_node",
        decide_next_classification_node,
        {
            "handle_general_inquiry_node": "handle_general_inquiry_node",
            "handle_add_book_node": "handle_add_book_node",
            "recommendation_node":"recommendation_node",
            "retrieve": "retrieve",
        }
    )

    workflow.add_edge("retrieve", "check_relevance")
    workflow.add_conditional_edges(
        "check_relevance",
        decide_next_node,
        {
            "structure_response": "structure_response",
            "rewrite_query": "rewrite_query",
            "generate_response": "generate_response",
        }
    )
    workflow.add_edge("structure_response", "return_answer")
    workflow.add_edge("rewrite_query", "retrieve")
    workflow.add_edge("generate_response", "check_hallucination")
    workflow.add_conditional_edges(
        "check_hallucination",
        lambda state: state["next_node"],
        {
            "generate_response": "generate_response",
            "return_answer": "return_answer",
        }
    )

    workflow.add_edge("return_answer", END)
    workflow.add_edge('handle_general_inquiry_node', END)
    workflow.add_edge('handle_add_book_node', END)
    workflow.add_edge('recommendation_node', END)
    # Set the entry point and compile the workflow


    # Execution
    inputs = {"question":query}
    memory = MemorySaver()
    app = workflow.compile()

    for output in app.stream(inputs):
        for key, value in output.items():
            response = value.get('response')
            if response:
                yield response

