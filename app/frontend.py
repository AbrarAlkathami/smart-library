import streamlit as st
import requests

st.title("Chat with ABRAR's AI")

session_id = "1"

def get_response(query):
    response = requests.post(
       "http://127.0.0.1:8002/chat",  # Ensure this is the correct port
        json={"query": query, "session_id": session_id},
        timeout=10000
    )
    if response.status_code == 200:
        return response.json().get("response", "")
    else:
        return f"Error: {response.status_code}"

# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display chat messages from history on app rerun
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# React to user input
if prompt := st.chat_input("Hi, how can I assist you today?"):
    # Display user message in chat message container
    st.chat_message("user").markdown(prompt)
    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": prompt})

    response = get_response(prompt)
    # Display assistant response in chat message container
    with st.chat_message("assistant"):
        st.markdown(response)
    # Add assistant response to chat history
    st.session_state.messages.append({"role": "assistant", "content": response})