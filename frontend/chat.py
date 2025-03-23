import streamlit as st
import os
import sys

# Add the parent directory to the Python path so that the 'backend' package is found.
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from backend.deepresearch import agent_fast_reply  # Custom agent function

st.set_page_config(
    page_title="Chatbot",
    page_icon="🤖",
    layout="wide"
)

st.title("💬 Deep Researcher Open Framework")
st.caption("🚀 A Streamlit Deep Researcher Chatbot.")

if "messages" not in st.session_state:
    st.session_state["messages"] = [{"role": "assistant", "content": "What would you like to research today?"}]

# Display chat messages using Streamlit's chat components
for msg in st.session_state.messages:
    st.chat_message(msg["role"]).write(msg["content"])

# Capture user input with the new chat input widget
if prompt := st.chat_input("Type your message here..."):
    # Append the user's message to the chat history and display it
    st.session_state.messages.append({"role": "user", "content": prompt})
    st.chat_message("user").write(prompt)
    
    # Generate the bot response using your custom agent
    bot_response = agent_fast_reply(prompt)
    st.session_state.messages.append({"role": "assistant", "content": bot_response})
    st.chat_message("assistant").write(bot_response)