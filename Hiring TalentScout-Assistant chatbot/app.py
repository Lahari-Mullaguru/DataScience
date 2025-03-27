import streamlit as st
import re  # For input validation

def validate_email(email):
    """Basic email validation"""
    return re.match(r"[^@]+@[^@]+\.[^@]+", email)

def validate_phone(phone):
    """Basic phone number validation (digits only, min 10 chars)"""
    return phone.isdigit() and len(phone) >= 10

def main():
    # Page configuration (same as before)
    st.set_page_config(
        page_title="TalentScout Hiring Assistant",
        page_icon="💼",
        layout="centered"
    )
    
    # Custom CSS (same as before)
    st.markdown("""
    <style>
        .stChatInput {position: fixed; bottom: 2rem;}
        .stChatMessage {width: 80%;}
        .assistant-message {background-color: #f0f2f6; padding: 1rem; border-radius: 0.5rem;}
    </style>
    """, unsafe_allow_html=True)
    
    # Initialize session state (expanded)
    if "messages" not in st.session_state:
        st.session_state.messages = []
        st.session_state.candidate_info = {
            "name": None,
            "email": None,
            "phone": None,
            "experience": None,
            "position": None,
            "location": None,
            "tech_stack": []
        }
        st.session_state.conversation_stage = "greeting"
    
    # Display header
    st.title("💼 TalentScout Hiring Assistant")
    st.caption("AI-powered initial screening for tech candidates")
    
    # Display chat messages
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
    
    # Initial greeting (only on first load)
    if len(st.session_state.messages) == 0:
        initial_greeting = (
            "Hello! I'm TalentBot, your AI hiring assistant. "
            "I'll help with your initial screening process.\n\n"
            "May I have your **full name** please?"
        )
        st.session_state.messages.append({"role": "assistant", "content": initial_greeting})
        with st.chat_message("assistant"):
            st.markdown(initial_greeting)
    
    # Handle user input
    if user_input := st.chat_input("Type your response here..."):
        # Add user message to chat
        st.session_state.messages.append({"role": "user", "content": user_input})
        with st.chat_message("user"):
            st.markdown(user_input)
        
        # Determine response based on conversation stage
        response = ""
        
        # --- GREETING: Collecting name ---
        if st.session_state.conversation_stage == "greeting":
            st.session_state.candidate_info["name"] = user_input
            response = f"Thanks, {user_input}! What's your **email address**?"
            st.session_state.conversation_stage = "collecting_email"
        
        # --- COLLECTING EMAIL ---
        elif st.session_state.conversation_stage == "collecting_email":
            if validate_email(user_input):
                st.session_state.candidate_info["email"] = user_input
                response = "Got it! What's your **phone number**?"
                st.session_state.conversation_stage = "collecting_phone"
            else:
                response = "❌ Please enter a valid email (e.g., name@example.com)."
        
        # --- COLLECTING PHONE ---
        elif st.session_state.conversation_stage == "collecting_phone":
            if validate_phone(user_input):
                st.session_state.candidate_info["phone"] = user_input
                response = "Great! How many **years of experience** do you have?"
                st.session_state.conversation_stage = "collecting_experience"
            else:
                response = "❌ Please enter a valid phone number (digits only, at least 10 characters)."
        
        # --- COLLECTING EXPERIENCE ---
        elif st.session_state.conversation_stage == "collecting_experience":
            if user_input.isdigit():
                st.session_state.candidate_info["experience"] = user_input
                response = "Got it! What **position(s)** are you applying for?"
                st.session_state.conversation_stage = "collecting_position"
            else:
                response = "❌ Please enter a valid number (e.g., 3)."
        
        # --- COLLECTING POSITION ---
        elif st.session_state.conversation_stage == "collecting_position":
            st.session_state.candidate_info["position"] = user_input
            response = "Thanks! What's your **current location**?"
            st.session_state.conversation_stage = "collecting_location"
        
        # --- COLLECTING LOCATION ---
        elif st.session_state.conversation_stage == "collecting_location":
            st.session_state.candidate_info["location"] = user_input
            response = (
                "Great! Now, please list your **tech stack** (e.g., Python, JavaScript, React).\n\n"
                "You can separate technologies with commas."
            )
            st.session_state.conversation_stage = "collecting_tech_stack"
        
        # --- (Next step: Tech stack collection) ---
        
        # Add assistant response to chat
        st.session_state.messages.append({"role": "assistant", "content": response})
        with st.chat_message("assistant"):
            st.markdown(response)

if __name__ == "__main__":
    main()
