import streamlit as st
from utils.data_handler import *
from utils.question_generator import generate_tech_questions
from prompts import *

# --- Session State Initialization ---
def init_session_state():
    if "messages" not in st.session_state:
        st.session_state.messages = []
        st.session_state.candidate_info = {
            "name": None, "email": None, "phone": None,
            "experience": None, "position": None,
            "location": None, "tech_stack": []
        }
        st.session_state.conversation_flow = [
            ("greeting", "name", INITIAL_GREETING),
            ("collecting_email", "email", INFO_COLLECTION_PROMPTS["email"]),
            ("collecting_phone", "phone", INFO_COLLECTION_PROMPTS["phone"]),
            ("collecting_experience", "experience", INFO_COLLECTION_PROMPTS["experience"]),
            ("collecting_position", "position", INFO_COLLECTION_PROMPTS["position"]),
            ("collecting_location", "location", INFO_COLLECTION_PROMPTS["location"]),
            ("collecting_tech_stack", "tech_stack", INFO_COLLECTION_PROMPTS["tech_stack"])
        ]
        st.session_state.current_stage = 0

# --- UI Setup ---
def setup_ui():
    st.set_page_config(
        page_title="TalentScout Hiring Assistant",
        page_icon="💼",
        layout="centered"
    )
    st.title("💼 TalentScout Hiring Assistant")
    st.caption("AI-Powered Candidate Screening")

    # Custom CSS
    st.markdown("""
    <style>
        .stChatInput {position: fixed; bottom: 2rem;}
        .stChatMessage {width: 80%;}
        .assistant-message {background-color: #f0f2f6; padding: 1rem; border-radius: 0.5rem;}
    </style>
    """, unsafe_allow_html=True)

# --- Core Logic ---
def handle_user_input(user_input: str):
    stage_data = st.session_state.conversation_flow[st.session_state.current_stage]
    stage_name, field, prompt = stage_data
    candidate = st.session_state.candidate_info

    # Validate inputs
    if stage_name == "collecting_email" and not validate_email(user_input):
        return "❌ Invalid email. Please try again (e.g., name@example.com)."
    elif stage_name == "collecting_phone" and not validate_phone(user_input):
        return "❌ Phone must be 10+ digits (no symbols)."
    elif stage_name == "collecting_experience" and not validate_experience(user_input):
        return "❌ Please enter a valid number (0-50)."

    # Store valid data
    candidate[field] = user_input

    # Move to next stage
    if st.session_state.current_stage < len(st.session_state.conversation_flow) - 1:
        st.session_state.current_stage += 1
        next_stage = st.session_state.conversation_flow[st.session_state.current_stage]
        return next_stage[2]  # Next prompt
    else:
        return generate_tech_questions_flow()

def generate_tech_questions_flow():
    tech_stack = st.session_state.candidate_info["tech_stack"]
    questions = []
    for tech in parse_tech_stack(tech_stack):
        q = generate_tech_questions(tech, st.session_state.candidate_info["experience"])
        if q:
            questions.append(f"**{tech} Questions:**\n\n{q}")
    
    return "\n\n".join(questions) + "\n\n" + CLOSING_MESSAGE

# --- Main Function ---
def main():
    setup_ui()
    init_session_state()

    # Display chat history
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # Initial greeting
    if len(st.session_state.messages) == 0:
        st.session_state.messages.append({"role": "assistant", "content": INITIAL_GREETING})
        with st.chat_message("assistant"):
            st.markdown(INITIAL_GREETING)

    # User input handling
    if user_input := st.chat_input("Your response..."):
        st.session_state.messages.append({"role": "user", "content": user_input})
        with st.chat_message("user"):
            st.markdown(user_input)

        response = handle_user_input(user_input)
        st.session_state.messages.append({"role": "assistant", "content": response})
        with st.chat_message("assistant"):
            st.markdown(response)

if __name__ == "__main__":
    main()
