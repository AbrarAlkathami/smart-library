from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_ollama.llms import OllamaLLM
from langchain_core.chat_history import BaseChatMessageHistory
from langchain_core.runnables.history import RunnableWithMessageHistory 
from langchain_core.chat_history import InMemoryChatMessageHistory
from langchain_core.chat_history import BaseChatMessageHistory
from langchain_core.messages import BaseMessage, AIMessage, HumanMessage
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
import sys
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_core.prompts import ChatPromptTemplate
from langchain_ollama.llms import OllamaLLM
from common.CRUD.books_chroma_crud import get_similarity
from langchain_core.agents import AgentAction, AgentFinish
import operator
from typing import TypedDict, Annotated, List, Union



class AgentState(TypedDict):
    input: str
    agent_out: Union[AgentAction, AgentFinish, None]
    intermediate_steps: Annotated[list[tuple[AgentAction, str]], operator.add]


store = {}

def get_session_history(session_id: str) -> BaseChatMessageHistory:
    if session_id not in store:
        store[session_id] = InMemoryChatMessageHistory()
    return store[session_id]

def generate_response(session_id: str, user_input: str):
    prompt = ChatPromptTemplate.from_messages([
        ("system", "You are a helpful AI bot, just answer a question that are relevent to this data {vector_info}, if the question does not mention in the data say that you don't know about this information"),
        ("human", "{user_input}"),
    ])

    model = OllamaLLM(model="llama3.1")

    chain = prompt | model
    history = get_session_history(session_id)

    # Retrieve vector info if needed
    vector_info = ""
    prompt_with_vector_info = f"User asked: {user_input}\n\nVector Database Results:\n{vector_info}\n\nAI Answer:"
    response = chain.invoke({"user_input": prompt_with_vector_info})

    # Add messages to history
    history.add_messages([
        HumanMessage(content=user_input),
        AIMessage(content=response)
    ])

    return response
     
     
 