from langchain_ollama.llms import OllamaLLM
from langchain_core.prompts import ChatPromptTemplate , PromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser , JsonOutputParser
from common.CRUD.books_chroma_crud import *
from langchain.output_parsers import PydanticOutputParser
from langchain_core.pydantic_v1 import BaseModel, Field, validator
from services.agent import*

def model_classification(system_prompt,parser,query):

    prompt = ChatPromptTemplate.from_messages(
        template= system_prompt,
        input_variables=[parser,query]
    ).partial(format_instructions=parser.get_format_instructions())

    llm = OllamaLLM(model="llama3.1" , temperature=0)

    rag_chain = prompt | llm | StrOutputParser()
    classification_response = rag_chain.invoke({"query": query})

    print(classification_response)
    return classification_response


def model(system_prompt,query):

    document = get_similarity(query)
    print("Retrieved context:", document)
    # if you want the output as string 
    prompt = PromptTemplate(
        template= system_prompt,
        input_variables=[query,document]
    )

    print("system_prompt", system_prompt)
    print("query", query)
    llm = OllamaLLM(model="llama3.1" , temperature=0,)

    rag_chain = prompt | llm | StrOutputParser()

    # if you want the output as json 
    prompt = PromptTemplate(
        template= system_prompt,
        input_variables=[query,document]
    )

    print("system_prompt", system_prompt)
    print("query", query)
    llm = OllamaLLM(model="llama3.1" , format="json", temperature=0)

    rag_chain = prompt | llm | JsonOutputParser()

    # prompt = ChatPromptTemplate.from_messages([
    #     ("system", system_prompt),
    #     ("human", query),
    # ])
    # context = get_similarity(query)
    # print("Retrieved context:", context)


    print("This is the RAG chain:", rag_chain)

    response = rag_chain.invoke({"query": query})
    print("We got the response:", response)

    return response


def RAG_model(system_prompt,query):
    llm = OllamaLLM(model="llama3.1")

    prompt = ChatPromptTemplate.from_messages([
        ("system", system_prompt),
        ("human", query),
    ])
    print(f"Created ChatPromptTemplate")

    # context = get_similarity(query)
    # print("Retrieved context:", context)

    rag_chain = (
        RunnablePassthrough()  
        | (lambda x: { "query": query , "system_prompt": system_prompt})  
        | prompt
        | llm
        | StrOutputParser()
    )

    print("This is the RAG chain:", rag_chain)

    response = rag_chain.invoke({"query": query})
    print("We got the response:", response)

    return response


# print(model("You are a helpful assisstant In Technologies." , "Hi, What does agent means"))
