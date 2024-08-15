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


class RouteQuery(BaseModel):
    """Route a user query to one of the most relevant classification types."""

    classification: Literal["general_inquiry", "add_book","search_by_title", "search_by_author","search_by_genre", "books_in_specific_year","books_with_rating_count","books_with_rating_average","summarize_book","book_thumbnail","title_from_description" ,"recommendation"] = Field(
        ...,
        description="Given a user question, choose to route it to one of the specified classifications."
    )


class Grader(BaseModel):
    """Route a user query to one of the most relevant classification types."""

    score: Literal["yes", "no"] = Field(
        ...,
        description="Indicate whether the generated response satisfies the given criterion. Use 'yes' if it does, and 'no' if it does not."
    )

# for classification
def classification_model(system_prompt, query):
    parser = PydanticOutputParser(pydantic_object=RouteQuery)
    prompt = PromptTemplate(
        template=system_prompt,
        input_variables=["query"]
    )
    prompt = prompt.partial(format_instructions=parser.get_format_instructions())
    llm = OllamaLLM(model="llama3.1", temperature=0)

    # Combine prompt and model, parse the output
    question_router = prompt | llm | parser
    
    response = question_router.invoke({"query": query})

    # Access the classification directly from the Pydantic model
    classification = response.classification

    print(f"Classification: {classification}")
    return classification

def model(system_prompt,query):
   # if request_name == 'add_book': add the json formate :else (StrOutoutParser)
    prompt = PromptTemplate(
        template= system_prompt,
        input_variables=[query]
    )

    llm = OllamaLLM(model="llama3.1" , temperature=0,)

    chain = prompt | llm | StrOutputParser()
    response = chain.invoke({"query": query})

    return response

def query_rewriter(question):
    prompt = PromptTemplate( 
        template= """ 
        You a query re-writer that converts an input query.
        To make a better version that is optimized for vectorstore retrieval. 
        Look at the initial and formulate an improved question.
        
        
        Here is the initial question: {question}. Improved question with no preamble: 
        
        """,
        input_variables=["query"]
    )
    llm = OllamaLLM(model="llama3.1" , temperature=0)
    rag_chain = prompt | llm | StrOutputParser()
    response= rag_chain.invoke({"question": question})
    return response

def classify_input_node(state):
    question = state["question"]

    system_prompt_classification = """"You are an expert in classifying user questions into one of the following categories: general_inquiry, add_book, search_by_title, search_by_author, search_by_genre, books_in_specific_year, books_with_rating_count, books_with_rating_average, summarize_book, book_thumbnail, title_from_description, or recommendation.
        When a user submits a query:
            - Determine the most appropriate classification.
            - Respond only with a JSON object that includes the classification field.

            

        Here is the user's question:
        {query}
    """
    classification_response=classification_model(system_prompt_classification,question)
    print(f"classify_input_node {classification_response}" )
    state['classification']=classification_response
    return classification_response

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
    return {"response": state['response']}

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
    return {"response": state['response']}




def retrieval_grader_model(query, documents):
    parser = PydanticOutputParser(pydantic_object=Grader)
    prompt = PromptTemplate(
        template= """ 
            You are a grader assessing relevance of a retrieved document to a user question.  
            If the document contains keywords related to the user question, grade it as relevant. 
            It does not need to be a stringent test. The goal is to filter out erroneous retrievals. 
            Give a binary score 'yes' or 'no' score to indicate whether the document is relevant to the question. 
            Provide the binary score as a JSON with a single key 'score' and no premable or explanation.
            
            
            Here is the retrieved document:  
            {document} 


            Here is the user question: 
            {question} 

            """,
        input_variables=["query","documents"]
    )
    prompt = prompt.partial(format_instructions=parser.get_format_instructions())
    llm = OllamaLLM(model="llama3.1" , temperature=0)
    retrieval_grader = prompt | llm | parser
    response= retrieval_grader.invoke({"query": query, "documents": documents})
    return response

def relevance_model(system_prompt,documents,query):
   
    prompt = PromptTemplate(
        template= system_prompt,
        input_variables=["query","documents"]
    )
    llm = OllamaLLM(model="llama3.1" , temperature=0)
    rag_chain = prompt | llm | JsonOutputParser()
    response= rag_chain.invoke({"query": query, "documents": documents})
    return response

def retrieve(state):
    query = state["question"]
    documents = get_similarity(query)
    state["documents"] = documents
    return state

def search(state):
    question=state['question']
    documents= state['documents']
    filtered_docs = []
    for d in documents:
        response=retrieval_grader_model(question,documents)
        score= response['score']
        print(score)
        if score=='yes':
            filtered_docs.append(d)
        else:
            continue

    return filtered_docs

def get_similarity(query_text: str):
    client = chromadb.PersistentClient(
    path="/Users/aalkathami001/Desktop/3rd week/Mon/task2/app/books_vector_db",
    settings=Settings(),
    tenant=DEFAULT_TENANT,
    database=DEFAULT_DATABASE,
    )
    collection = client.get_or_create_collection(name="books_collection")

    results = collection.query(
        query_texts=[query_text],
    )

    return results['metadatas']



class GraphState(TypedDict):
    question: Optional[str] = None
    classification: Optional[str] = None
    documents: List[str]
    response: Optional[str] = None

workflow = StateGraph(GraphState)

def retrieve(state):
    query = state["question"]
    documents = get_similarity(query)
    state["documents"] = documents
    return state

workflow.add_node("classify_input_node", classify_input_node)