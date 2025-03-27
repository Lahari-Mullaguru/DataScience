import streamlit as st

def main():
    # Configure page
    st.set_page_config(
        page_title="TalentScout Hiring Assistant",
        page_icon="💼",
        layout="centered"
    )
    
    # Custom CSS for better appearance
    st.markdown("""
    <style>
        .stChatInput {position: fixed; bottom: 2rem;}
        .stChatMessage {width: 80%;}
        .assistant-message {background-color: #f0f2f6; padding: 1rem; border-radius: 0.5rem;}
    </style>
    """, unsafe_allow_html=True)
    
    # Initialize session state
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
    
    # Initial greeting if no messages yet
    if len(st.session_state.messages) == 0:
        initial_greeting = (
            "Hello! I'm TalentBot, your AI hiring assistant. "
            "I'll help with your initial screening process.\n\n"
            "May I have your full name please?"
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
        
        # Simple response for now (will enhance in next steps)
        if st.session_state.conversation_stage == "greeting":
            response = f"Thank you, {user_input}. Could you please share your email address?"
            st.session_state.candidate_info["name"] = user_input
            st.session_state.conversation_stage = "collecting_email"
        
        # Add assistant response to chat
        st.session_state.messages.append({"role": "assistant", "content": response})
        with st.chat_message("assistant"):
            st.markdown(response)

if __name__ == "__main__":
    main()
