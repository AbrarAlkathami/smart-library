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