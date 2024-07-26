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
from langchain_core.tools import tool


store = {}

def get_session_history(session_id: str) -> BaseChatMessageHistory:
    if session_id not in store:
        store[session_id] = InMemoryChatMessageHistory()
    return store[session_id]

def generate_response(session_id: str, query: str):

    llm = OllamaLLM(model="llama3.1" ,n_gpu_layers=1,
    n_batch=512,
    n_ctx=2048,
    f16_kv=True,  
    verbose=True,)
    check_prompt = ("determine what does the query was about?, if the the user ask to filter categories for books return (filter categories)"

    )

    system_prompt = (
                "You are an asistant for smart library"
                "Use the given context to answer the question. "
                "If you don't know the answer, say you don't know. "
                "Use three sentence maximum and keep the answer concise. "
                "Context: {context}"
            )
    prompt = ChatPromptTemplate.from_messages(
                [
                    ("system", system_prompt),
                    ("human", "{input}"),
                ]
            )
    context = get_similarity(query)
    question_answer_chain = create_stuff_documents_chain(llm, prompt)
    chain = create_retrieval_chain(context, question_answer_chain)

    response= chain.invoke({"input": query})

    return response
     
     
