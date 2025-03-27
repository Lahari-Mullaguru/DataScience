import streamlit as st
from utils.data_handler import (
    validate_email,
    validate_phone,
    parse_tech_stack
)
from utils.question_generator import generate_tech_questions
from prompts import (
    INITIAL_GREETING,
    TECH_STACK_PROMPT,
    CLOSING_MESSAGE
)

# Initialize session state
def init_session_state():
    if "messages" not in st.session_state:
        st.session_state.messages = []
        st.session_state.candidate_info = {
            "name": None,
            "email": None,
            "phone": None,
            "experience": None,
            "position": None,
            "location": None,
            "tech_stack": [],
            "tech_questions": {}
        }
        st.session_state.conversation_stage = "greeting"

# UI Configuration
def setup_ui():
    st.set_page_config(
        page_title="TalentScout Hiring Assistant",
        page_icon="💼",
        layout="centered"
    )
    st.title("💼 TalentScout Hiring Assistant")
    st.caption("AI-powered initial screening for tech candidates")
    
    # Custom CSS
    st.markdown("""
    <style>
        .stChatInput {position: fixed; bottom: 2rem;}
        .stChatMessage {width: 80%;}
        .assistant-message {background-color: #f0f2f6; padding: 1rem; border-radius: 0.5rem;}
    </style>
    """, unsafe_allow_html=True)

# [Rest of the conversation handling code...]
# (Would continue with the modularized version of the conversation flow)
