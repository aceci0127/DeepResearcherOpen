import streamlit as st
from datetime import datetime
import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from backend.deepresearch import agent_fast_reply  # Updated import

# This MUST be the first Streamlit command
st.set_page_config(
    page_title="My Streamlit Chatbot",  # Default title
    page_icon="🤖",  # Default icon
    layout="wide"  # Optional
)

def main():
    # App configuration from sidebar
    with st.sidebar:
        st.title("Chatbot Settings")
        
        # Customizable options
        page_title_input = st.text_input("Page Title", "My Streamlit Chatbot")
        bot_name = st.text_input("Bot Name", "StarBot")
        
        # Theme color options
        theme_color = st.color_picker("Theme Color", "#FF4B4B")
        
        # Icon selection
        icon_options = {
            "Robot": "🤖", 
            "Star": "⭐", 
            "Speech": "💬",
            "Sparkles": "✨",
            "Brain": "🧠"
        }
        selected_icon = st.selectbox("Select Bot Icon", list(icon_options.keys()))
        bot_icon = icon_options[selected_icon]
        
        # User icon selection
        user_icon_options = {"Person": "👤", "User": "👩‍💻", "Smile": "😊"}
        selected_user_icon = st.selectbox("Select User Icon", list(user_icon_options.keys()))
        user_icon = user_icon_options[selected_user_icon]
        
        # Reset chat option
        if st.button("Reset Chat"):
            st.session_state.messages = []
            st.experimental_rerun()

    # Apply custom styling based on theme color
    st.markdown(
        f"""
        <style>
        .stTextInput > div > div > input {{
            border-color: {theme_color};
        }}
        .stButton > button {{
            background-color: {theme_color};
            color: white;
        }}
        </style>
        """,
        unsafe_allow_html=True
    )

    # Main chat interface
    st.title(f"{bot_icon} {page_title_input}")
    st.markdown(f"Chat with {bot_name} - powered by Streamlit")
    
    # Initialize chat history in session state if it doesn't exist
    if "messages" not in st.session_state:
        st.session_state.messages = []
        
        # Add welcome message
        welcome_message = {
            "role": "assistant",
            "content": f"Hello! I'm {bot_name}. How can I help you today?",
            "timestamp": datetime.now().strftime("%H:%M")
        }
        st.session_state.messages.append(welcome_message)

    # Display chat messages
    for message in st.session_state.messages:
        if message["role"] == "user":
            st.markdown(f"""
            <div style="display: flex; justify-content: flex-end; margin-bottom: 10px;">
                <div style="background-color: #E0E0E0; padding: 10px; border-radius: 10px; max-width: 80%;">
                    <p style="margin: 0;">{user_icon} <b>You:</b> {message['content']}</p>
                    <p style="margin: 0; font-size: 0.8em; color: grey; text-align: right;">{message['timestamp']}</p>
                </div>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown(f"""
            <div style="display: flex; margin-bottom: 10px;">
                <div style="background-color: {theme_color}; color: white; padding: 10px; border-radius: 10px; max-width: 80%;">
                    <p style="margin: 0;">{bot_icon} <b>{bot_name}:</b> {message['content']}</p>
                    <p style="margin: 0; font-size: 0.8em; color: rgba(255,255,255,0.7); text-align: right;">{message['timestamp']}</p>
                </div>
            </div>
            """, unsafe_allow_html=True)

    # Chat input
    with st.container():
        user_input = st.text_input("Type your message here:", key="user_input", placeholder="Ask me anything...")
        
        if st.button("Send"):
            if user_input:
                # Add user message to chat
                user_message = {
                    "role": "user",
                    "content": user_input,
                    "timestamp": datetime.now().strftime("%H:%M")
                }
                st.session_state.messages.append(user_message)
                
                # Generate and add bot response using agent_fast_reply
                bot_reply = agent_fast_reply(user_input)
                bot_message = {
                    "role": "assistant",
                    "content": bot_reply,
                    "timestamp": datetime.now().strftime("%H:%M")
                }
                st.session_state.messages.append(bot_message)
                
                # Clear input and update chat
                st.experimental_rerun()

if __name__ == "__main__":
    main()