from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_ollama.llms import OllamaLLM
from langchain_community.chat_message_histories import ChatMessageHistory
from langchain_core.chat_history import BaseChatMessageHistory
from langchain_core.runnables.history import RunnableWithMessageHistory 
from langchain_core.chat_history import InMemoryChatMessageHistory
# from chromaDB import similarity_text
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain.chains.retrieval import create_retrieval_chain
from langchain_core.chat_history import BaseChatMessageHistory
from langchain_core.documents import Document
from langchain_core.messages import BaseMessage, AIMessage, HumanMessage
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.runnables import (
    RunnableLambda,
    ConfigurableFieldSpec,
    RunnablePassthrough,
)
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_core.prompts import ChatPromptTemplate
from langchain_ollama.llms import OllamaLLM
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain_core.documents import Document
# from common.database.chromaDB import similarity_text

# store = {}

# def get_session_history(session_id: str) -> BaseChatMessageHistory:
#         if session_id not in store:
#             store[session_id] = InMemoryChatMessageHistory()
#         return store[session_id]


# # def retrieve_qa(query: str):
# model = OllamaLLM(model="mistral")

# prompt = ChatPromptTemplate.from_messages(
# [
#     (
#         "system",
#         "You're an assistant who speaks in {language}. Respond in 20 words or fewer",
#     ),
#     MessagesPlaceholder(variable_name="history"),
#     ("human", "{input}"),
# ]
# )

# runnable = prompt | model

# runnable_with_history = RunnableWithMessageHistory(
#     runnable,
#     get_session_history,
#     input_messages_key="input",
#     history_messages_key="history",
# )
# for i in range(100):
#     query=input("Enter your question?")
#     response=runnable_with_history.invoke(
#     {"language": "Arabic", "input": {query}},
#     config={"configurable": {"session_id": "2"}},
#     )
#     print(response)

############################################################################

    # return response.content

    # # Retrieve context using similarity_text function)

    # # Define the system prompt
    # system_prompt = (
    #     "You are an assistant for question-answering tasks. "
    #     "Use the following pieces of retrieved context to answer "
    #     "the question. If you don't know the answer, say that you "
    #     "don't know. Use three sentences maximum and keep the "
    #     "answer concise."
    #     "\n\n"
    #     "{retriever}"
    # )
    # template_messages = [
    # SystemMessage(content="You are a helpful assistant."),
    # MessagesPlaceholder(variable_name="chat_history"),
    # HumanMessagePromptTemplate.from_template("{text}"),
    # ]
    # prompt_template = ChatPromptTemplate.from_messages(template_messages)

    # response = rag_chain.invoke({"input": "What is Task Decomposition?"})
    # print(response)
    # return response



# # Define the chat prompt template
# prompt = ChatPromptTemplate.from_messages(
#     [
#         ("system", "You are an assistant for question-answering tasks who speaks in all languages." 
#                     "Use the following pieces of retrieved context to answer" "Use the following pieces of retrieved context to answer "
#                     "the question. If you don't know the answer, say that you "
#                     "don't know. Use three sentences maximum and keep the "
#                     "answer concise."
#                     "\n\n"
#                     "{context}""Respond in 20 words or fewer"
#         ),
#         MessagesPlaceholder(variable_name="history"),
#         ("human", "{question}"),
#         ("system", "{context}"), 
#     ]
# )

# # Define the chain with prompt and model
# chain = prompt | model

# from langchain_community.chat_message_histories import ChatMessageHistory
# from langchain_core.chat_history import BaseChatMessageHistory
# from langchain_core.runnables.history import RunnableWithMessageHistory



# def retrive_function():
# history_aware_retriever = create_history_aware_retriever(
#     llm, retriever, contextualize_q_prompt
# )
# system_prompt = (
#     "You are an assistant for question-answering tasks. "
#     "Use the following pieces of retrieved context to answer "
#     "the question. If you don't know the answer, say that you "
#     "don't know. Use three sentences maximum and keep the "
#     "answer concise."
#     "\n\n"
#     "{context}"
# )
# qa_prompt = ChatPromptTemplate.from_messages(
#     [
#         ("system", system_prompt),
#         MessagesPlaceholder("chat_history"),
#         ("human", "{input}"),
#     ]
# )
# question_answer_chain = create_stuff_documents_chain(llm, qa_prompt)

# rag_chain = create_retrieval_chain(history_aware_retriever, question_answer_chain)
# store = {}


# def get_session_history(session_id: str) -> BaseChatMessageHistory:
#     if session_id not in store:
#         store[session_id] = ChatMessageHistory()
#     return store[session_id]


# conversational_rag_chain = RunnableWithMessageHistory(
#     rag_chain,
#     get_session_history,
#     input_messages_key="input",
#     history_messages_key="chat_history",
#     output_messages_key="answer",
# )



# def retrieve_docs(question: str):
#     retrieved_docs = similarity_text(question)
#     context = "\n".join(retrieved_docs)  # Combine retrieved docs into a single context string
#     return context


# # Initialize the Ollama model
# model = OllamaLLM(model="mistral")

# # Define the chat prompt template
# prompt = ChatPromptTemplate.from_messages(
#     [
#         ("system", "You are a helpful assistant who speaks in {language}. Respond in 20 words or fewer"),
#         MessagesPlaceholder(variable_name="history"),
#         ("human", "{question}"),
#         ("system", "{context}"),  # Add the retrieved context to the prompt
#     ]
# )

# # Define the chain with prompt and model
# chain = prompt | model

# # Initialize an in-memory store for session histories
# store = {}

# # Define a function to get or create session history
# def get_session_history(session_id: str) -> BaseChatMessageHistory:
#     if session_id not in store:
#         store[session_id] = ChatMessageHistory()
#     return store[session_id]

# # Define the conversational RAG chain with message history handling
# conversational_rag_chain = RunnableWithMessageHistory(
#     chain,
#     get_session_history,
#     input_messages_key="input",
#     history_messages_key="chat_history",
#     output_messages_key="answer",
# )

# # Function to perform RAG with history
# def retrieve_and_generate_with_history(session_id: str, question: str):
#     context = retrieve_docs(question)
#     input_data = {
#         "question": question,
#         "context": context,
#         "language": "English",  # You can customize this as needed
#         "chat_history": get_session_history(session_id).get_messages(),
#     }
#     response = conversational_rag_chain.invoke(input_data)
#     return response

# # Example usage
# session_id = "session1"
# question = "List all the books for Harry Potter"
# answer = retrieve_and_generate_with_history(session_id, question)
# print(answer)
