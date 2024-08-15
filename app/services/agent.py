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

                ######################################################################################################
                        ################################## LLMs ##################################

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

    return classification

# without retriver and formate the result for the add book to the DB
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

def rag_model(system_prompt,query,documents):
    prompt = PromptTemplate(
        template= system_prompt,
        input_variables=["query","documents"]
    )
    llm = OllamaLLM(model="llama3.1" , temperature=0)
    rag_chain = prompt | llm | StrOutputParser()
    response= rag_chain.invoke({"query": query, "documents": documents})
    return response

def retrieval_grader_model(query, documents):
    parser = PydanticOutputParser(pydantic_object=Grader)
    prompt = PromptTemplate(
        template= """ 
            You are a grader assessing relevance of a retrieved documents to a user query.  
            If the documents contains keywords related to the user query, grade it as relevant. 
            It does not need to be a stringent test. The goal is to filter out erroneous retrievals. 
            Give a binary score 'yes' or 'no' score to indicate whether the documents is relevant to the query. 
            Provide the binary score as a JSON with a single key 'score' and no premable or explanation.
            
            
            Here is the retrieved documents:  
            {documents} 


            Here is the user query: 
            {query} 

            """,
        input_variables=["query","documents"]
    )
    prompt = prompt.partial(format_instructions=parser.get_format_instructions())
    llm = OllamaLLM(model="llama3.1" , temperature=0)
    retrieval_grader = prompt | llm | parser
    response= retrieval_grader.invoke({"query": query, "documents": documents})
    return response

def docs_to_tables(documents):
    columns = [
            'title', 'subtitle', 'authors', 'published_year', 'average_rating',
            'num_pages', 'ratings_count', 'genre', 'description', 'thumbnail'
        ]

    # Create the header
    header = "| " + " | ".join(columns) + " |"
    separator = "| " + " | ".join(['-' * len(col) for col in columns]) + " |"

    # Create each row of the table
    rows = []
    for document in documents:
        row = "| " + " | ".join([str(document.get(col, '')).strip() for col in columns]) + " |"
        rows.append(row)

    # Combine everything into the final table
    table = [header, separator] + rows
    return "\n".join(table)




def hallucination_grader_model(documents,generation):
    parser = PydanticOutputParser(pydantic_object=Grader)
    prompt = PromptTemplate(
        template= """
        You are a grader tasked with evaluating whether the given answer is based on and supported by the provided facts.
        Determine if the answer accurately reflects the facts. 
        If it does, respond with 'yes'. If it does not, respond with 'no'.
        Provide your response as a JSON object with a single key 'score' and no additional text.

        Below are the facts:
        {documents} 

        Below is the answer:
        {generation}

        """,
        input_variables=["documents","generation"]
    )
    prompt = prompt.partial(format_instructions=parser.get_format_instructions())
    llm = OllamaLLM(model="llama3.1" , temperature=0)
    rag_chain = prompt | llm | parser
    response= rag_chain.invoke({"documents": documents, "generation": generation})
    return response

def answer_grader_model(query,generation):
    parser = PydanticOutputParser(pydantic_object=Grader)
    prompt = PromptTemplate( 
        template= """ 
        You are a grader assessing whether an answer is useful to resolve a user query.  
        Give a binary score 'yes' or 'no' to indicate whether the answer is useful to resolve a user query. \n
        Provide the binary score as a JSON with a single key 'score' and no preamble or explanation.
        

        Here is the answer:
        {generation} 

    
        Here is the user query: 
        {query}
        
        """,
        input_variables=["generation","query"]
    )
    prompt = prompt.partial(format_instructions=parser.get_format_instructions())
    llm = OllamaLLM(model="llama3.1" , temperature=0)
    rag_chain = prompt | llm | parser
    response= rag_chain.invoke({"generation": generation, "query": query})
    return response

def query_keywords(query):
    prompt = PromptTemplate( 
        template= """ 
        You are expert in identifying books information keywords in the query.
        To optimiz the result of the vectorstore retrieval. 
        Return list format of the keywords you found.
        Do not add additional information.
        
        Here is the user query: {query}. 
        
        """,
        input_variables=["query"]
    )
    llm = OllamaLLM(model="llama3.1" , temperature=0)
    rag_chain = prompt | llm | StrOutputParser()
    response= rag_chain.invoke({"query": query})
    return response

def query_rewriter_model(query):
    prompt = PromptTemplate( 
        template= """ 
        You are query re-writer that rewrite an user query by taking the keywords in the user query.
        To make a better version that is optimized for vectorstore retrieval. 
        Look at the initial and formulate an improved query.
        
        
        Here is the user query: {query}. 
        
        """,
        input_variables=["query"]
    )
    llm = OllamaLLM(model="llama3.1" , temperature=0)
    rag_chain = prompt | llm | StrOutputParser()
    response= rag_chain.invoke({"query": query})
    return response

def get_similarity(query_text: str):
    client = chromadb.PersistentClient(
    path="/Users/aalkathami001/Desktop/3rd week/Mon/task2/app/books_vector_db",
    settings=Settings(),
    tenant=DEFAULT_TENANT,
    database=DEFAULT_DATABASE,
    )
    collection = client.get_or_create_collection(name="books_collection")

    results = collection.query(
        query_texts=query_text,
    )

    return results['metadatas']



                ######################################################################################################
                        ################################## GRAPH ##################################

class GraphState(TypedDict):
    question: Optional[str] = None
    classification: Optional[str] = None
    next_node: Optional[str]=None
    documents: Optional[List[str]]=None
    response: Optional[str] = None

workflow = StateGraph(GraphState)

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
            Your task is to identify the most relevant document from the provided list.
            Then create a concise and informative summary of the book.
            The summary should include key points, without altering any information from the original document.

            

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
inputs = {"question": "list all books that the average rating more than 4"}
memory = MemorySaver()
app = workflow.compile()

for output in app.stream(inputs):
    for key, value in output.items():
        print('Node:', key)
        response = value.get('response')
        if response:
            print('\n\n\n')
            print(response)
    

