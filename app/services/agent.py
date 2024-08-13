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

class GraphState(TypedDict):
    question: Optional[str] = None
    classification: Optional[str] = None
    documents: List[str]
    response: Optional[str] = None

workflow = StateGraph(GraphState)

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

    print(f"Classification: {classification}")
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

# with retriver and formating 
def relevance_model(system_prompt,query, documents):
    prompt = PromptTemplate(
        template= system_prompt,
        input_variables=["query","documents"]
    )
    llm = OllamaLLM(model="llama3.1" , temperature=0)
    rag_chain = prompt | llm | JsonOutputParser()
    response= rag_chain.invoke({"query": query, "documents": documents})
    return response

def hallucination_grader_model(query,documents,generation):
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

def answer_grader_model(query,documents,generation):
    parser = PydanticOutputParser(pydantic_object=Grader)
    prompt = PromptTemplate( 
        template= """ 
        You are a grader assessing whether an answer is useful to resolve a question.  
        Give a binary score 'yes' or 'no' to indicate whether the answer is useful to resolve a question. \n
        Provide the binary score as a JSON with a single key 'score' and no preamble or explanation.
        
        

        Here is the answer:
        {generation} 

    
        Here is the question: 
        {question}
        
        """,
        input_variables=["generation","query"]
    )
    prompt = prompt.partial(format_instructions=parser.get_format_instructions())
    llm = OllamaLLM(model="llama3.1" , temperature=0)
    rag_chain = prompt | llm | parser
    response= rag_chain.invoke({"generation": generation, "query": query})
    return response

def query_rewriter(generation,question):
    prompt = PromptTemplate( 
        template= """ 
        You a query re-writer that converts an input query.
        To make a better version that is optimized for vectorstore retrieval. 
        Look at the initial and formulate an improved question. \n
        Here is the initial question: \n\n {question}. Improved question with no preamble: \n
        
        """,
        input_variables=["generation","query"]
    )
    llm = OllamaLLM(model="llama3.1" , temperature=0)
    rag_chain = prompt | llm | StrOutputParser()
    response= rag_chain.invoke({"question": question})
    return response

# with retriver , formating and checking
def quality_and_completeness_model(system_prompt,query,documents):
    prompt = PromptTemplate(
        template= system_prompt,
        input_variables=["query","documents"]
    )
    llm = OllamaLLM(model="llama3.1" , temperature=0)
    rag_chain = prompt | llm | JsonOutputParser()
    response = rag_chain.invoke({"query": query, "documents": documents})
    return response

def get_similarity(query_text : str):
    client = chromadb.PersistentClient(
    path="/Users/aalkathami001/Desktop/3rd week/Mon/task2/app/books_vector_db",
    settings=Settings(),
    tenant=DEFAULT_TENANT,
    database=DEFAULT_DATABASE,
    )
    collection = client.get_or_create_collection(name="books_collection")

    results = collection.query(
        query_texts=[query_text]
    )
    return results['metadatas']




######################################################################################################
        ################################## GRAPH NODES ##################################



def classify(query): 
    
    system_prompt_classification = """"You are an expert in classifying user questions into one of the following categories: general_inquiry, add_book, search_by_title, search_by_author, search_by_genre, books_in_specific_year, books_with_rating_count, books_with_rating_average, summarize_book, book_thumbnail, title_from_description, or recommendation.
        When a user submits a query:
            - Determine the most appropriate classification.
            - Respond only with a JSON object that includes the classification field.

            

        Here is the user's question:
        {query}
    """
    classification_response=classification_model(system_prompt_classification,query)
    
    print(classification_response)
    return classification_response


def classify_input_node(state):
    question = state["question"]
    classification = classify(question)
    print(f"classify_input_node {classification}" )
    state['classification']=classification
    return {"classification": classification}


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
    return {"response": "Book added successfully! \n "+state['response']}


# RAG model ----- grade_relevance_model ----- using columns to retrive the data 

def handle_search_by_title_node(state):
    system_prompt_search_by_title="""
    You are an expert in searching for books by title based on user query. 
    When user send the query:
        - Check the douments.
        - Check the title for each document.
        - If you found related title to the user query return it.
        - If you did not found any related title based on the user query return, sorry we do not have this book.
    
    Here is the user query:  
    {query} 

    Here is the retrieved document:  
    {document} 

    """
    question = state["question"]
    
    return 

def handle_search_by_author_node(state):
    system_prompt_search_by_author=""""""
    question = state["question"]
    return 

def handle_search_by_genre_node(state):
    system_prompt_search_by_genre=""""""
    question = state["question"]
    return 

def handle_books_in_specific_year_node(state):
    system_prompt_for_books_in_specific_year=""""""
    question = state["question"]
    return 

def handle_books_with_rating_count_node(state):
    system_prompt_for_books_with_rating_count=""""""
    question = state["question"]
    return 

def handle_books_with_rating_average_node(state):
    system_prompt_for_books_with_rating_average=""""""
    question = state["question"]
    
    return 

def handle_title_from_description_node(state):
    system_prompt_for_title_from_description =""""""
    question = state["question"]
    return 


# quality_and_completeness ----- grade_relevance_model ----- using columns to retrive the data 

def handle_summarize_book_node(state):
    summarize_booK_system_prompt=""""""
    question = state["question"]
    response = "" 
    return {"response": response}

def handle_thumbnail_description_node(state):
    thumbnail_description_system_prompt=""""""
    question = state["question"]
    response = "" 
    return {"response": response}

def handle_recommendation_node(state):
    recommendation_system_prompt=""""""
    question = state["question"]
    response = "" 
    return {"response": response}

############################################################################################################
            ########################################################################

def retrieve(state):
    question = state["question"]
    documents = get_similarity(question)
    state["documents"] = documents
    return {"documents" : documents, "question" : question }


def retrieval_grader(state):
    question = state["question"]
    documents = state["documents"]

    retrieval_grader_prompt=""" 
    You are a grader assessing relevance of a retrieved document to a user question.  
    If the document contains keywords related to the user question, grade it as relevant. 
    It does not need to be a stringent test. The goal is to filter out erroneous retrievals. 
    Give a binary score 'yes' or 'no' score to indicate whether the document is relevant to the question. 
    Provide the binary score as a JSON with a single key 'score' and no premable or explanation.
    
    
    Here is the retrieved document:  
    {document} 


    Here is the user question: 
    {question} 

    """
    
    filtered_docs = []
    for d in documents:
        response=relevance_model(retrieval_grader_prompt,question,documents)
        grade = response["score"]
        print(grade)
        if grade == "yes":
            print("---GRADE: DOCUMENT RELEVANT---")
            filtered_docs.append(d)
        else:
            print("---GRADE: DOCUMENT NOT RELEVANT---")
            continue
    return {"documents": filtered_docs, "question": question}

def grade_generation_v_documents_and_question(state):
    """
    Determines whether the generation is grounded in the document and answers question.

    Args:
        state (dict): The current graph state

    Returns:
        str: Decision for next node to call
    """

    print("---CHECK HALLUCINATIONS---")
    question = state["question"]
    documents = state["documents"]
    generation = state["generation"]

    # score = hallucination_grader.invoke(
    #     {"documents": documents, "generation": generation}
    # )
    score=""
    grade =  "" #score["score"]

    # Check hallucination
    if grade == "yes":
        print("---DECISION: GENERATION IS GROUNDED IN DOCUMENTS---")
        # Check question-answering
        print("---GRADE GENERATION vs QUESTION---")
        # score = answer_grader.invoke({"question": question, "generation": generation})
        grade = score["score"]
        if grade == "yes":
            print("---DECISION: GENERATION ADDRESSES QUESTION---")
            return "useful"
        else:
            print("---DECISION: GENERATION DOES NOT ADDRESS QUESTION---")
            return "not useful"
    else:
        pprint("---DECISION: GENERATION IS NOT GROUNDED IN DOCUMENTS, RE-TRY---")
        return "not supported"   

############################################################################################################
            ########################################################################
# Add nodes to the workflow
workflow.add_node("classify_input_node", classify_input_node)

workflow.add_node("handle_general_inquiry_node", handle_general_inquiry_node)
workflow.add_node("handle_add_book_node", handle_add_book_node)

workflow.add_node("handle_search_by_title_node", handle_search_by_title_node)
workflow.add_node("handle_search_by_author_node", handle_search_by_author_node)
workflow.add_node("handle_search_by_genre_node", handle_search_by_genre_node)
workflow.add_node("handle_books_in_specific_year_node", handle_books_in_specific_year_node)
workflow.add_node("handle_books_with_rating_count_node", handle_books_with_rating_count_node)
workflow.add_node("handle_books_with_rating_average_node", handle_books_with_rating_average_node)
workflow.add_node("handle_title_from_description_node", handle_title_from_description_node)

workflow.add_node("handle_summarize_book", handle_summarize_book_node)
workflow.add_node("handle_thumbnail_description", handle_thumbnail_description_node)
workflow.add_node("handle_recommendation_node", handle_recommendation_node)

"books_with_rating_average","summarize_book","book_thumbnail","title_from_description","recommendation"

def decide_next_node(state):

    classification = state['classification']

    if classification == "general_inquiry":
        return "handle_general_inquiry_node"
    elif classification == "add_book":
        return "handle_add_book_node"
    
    elif classification == "search_by_title":
        return "handle_search_by_title_node"
    elif classification == "search_by_author":
        return "handle_search_by_author_node"
    elif classification == "search_by_genre":
        return "handle_search_by_genre_node"
    elif classification == "books_in_specific_year":
        return "handle_books_in_specific_year_node"
    elif classification == "books_with_rating_count":
        return "handle_books_with_rating_count_node"
    elif classification == "books_with_rating_average":
        return "handle_books_with_rating_average_node"
    elif classification == "title_from_description":
        return "handle_title_from_description_node"
    
    elif classification == "summarize_book":
        return "handle_summarize_book"
    elif classification == "book_thumbnail":
        return "handle_thumbnail_description"
    elif classification == "recommendation":
        return "handle_recommendation_node"
    
    
workflow.add_conditional_edges(
    "classify_input_node",
    decide_next_node,
    {
        "handle_general_inquiry_node": "handle_general_inquiry_node",
        "handle_add_book_node": "handle_add_book_node",

        "handle_search_by_title_node": "handle_search_by_title_node",
        "handle_search_by_author_node": "handle_search_by_author_node",
        "handle_search_by_genre_node": "handle_search_by_genre_node",

        "handle_books_in_specific_year_node": "handle_books_in_specific_year_node",
        "handle_books_with_rating_count_node": "handle_books_with_rating_count_node",
        "handle_books_with_rating_average_node": "handle_books_with_rating_average_node",
        "handle_title_from_description_node": "handle_title_from_description_node",
        "handle_summarize_book": "handle_summarize_book",
        "handle_thumbnail_description": "handle_thumbnail_description",
        "handle_recommendation_node": "handle_recommendation_node",
    }
)



# Set up edges to ensure all nodes can lead to END
workflow.set_entry_point("classify_input_node")
workflow.add_edge('handle_general_inquiry_node', END)
workflow.add_edge('handle_add_book_node', END)
# workflow.add_edge('handle_summarize_book', END)

# Set the entry point and compile
app = workflow.compile()

inputs = {"question": "Hi, how are you"}
for output in app.stream(inputs):
    print("this is the output for your query")
    print(output)
    for key, value in output.items():
        # Node
        print("\n\n\n")
        pprint(f"Node '{key}':")
        # Optional: print full state at each node
        # pprint.pprint(value["keys"], indent=2, width=80, depth=None)
        
    pprint("\n---\n")
# Final generation

pprint(value["response"])

# class Agent:
#     def __init__(self, system=""):
#         self.system=system
#         self.messages=[]
#         if self.system:
#             self.messages.append(("system", system))
    
#     def __call__(self,message):
#        self.messages.append(("user", message)) 
#        result = self.execute()
#        self.messages.append(("assisstant", result))
#        return result
    
#     def execute(self):
#         llm = OllamaLLM(model="llama3.1")

#         prompt = ChatPromptTemplate.from_messages([self.messages])

#         # context = get_similarity(query)
#         # print("Retrieved context:", context)

#         rag_chain = (
#             RunnablePassthrough()  
#             | (lambda x: { "query": self.message , "system_prompt": self.system})  
#             | prompt
#             | llm
#             | StrOutputParser()
#         )

#         response = rag_chain.invoke({"query": self.message })
#         print("We got the response:", response)


# prompt = """
# You run in a loop of Thought, Action, PAUSE, Observation.
# At the end of the loop you output an Answer
# Use Thought to describe your thoughts about the query you have been asked.
# Use Action to run one of the actions available to you - then return PAUSE.
# Observation will be the result of running those actions.

# Your available actions are:

# calculate:
# e.g. calculate: 4 * 7 / 3
# Runs a calculation and returns the number - uses Python so be sure to use floating point syntax if necessary

# average_dog_weight:
# e.g. average_dog_weight: Collie
# returns average weight of a dog when given the breed

# Example session:

# query: How much does a Bulldog weigh?
# Thought: I should look the dogs weight using average_dog_weight
# Action: average_dog_weight: Bulldog
# PAUSE

# You will be called again with this:

# Observation: A Bulldog weights 51 lbs

# You then output:

# Answer: A bulldog weights 51 lbs
# """.strip()
# agent= Agent(prompt)
# print(agent("welcom"))