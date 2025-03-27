import streamlit as st
import re
import openai
from dotenv import load_dotenv
import os

# Load OpenAI API key
load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

def validate_email(email):
    """Basic email validation"""
    return re.match(r"[^@]+@[^@]+\.[^@]+", email)

def validate_phone(phone):
    """Basic phone validation (digits only, min 10 chars)"""
    return phone.isdigit() and len(phone) >= 10

def generate_tech_questions(tech, experience):
    """Generate technical questions using OpenAI"""
    prompt = f"""
    Generate 3-5 technical interview questions about {tech} suitable for a candidate with {experience} years of experience.
    Questions should cover:
    - Core concepts
    - Practical scenarios
    - Best practices
    Format as a numbered list.
    """
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"⚠️ Could not generate questions. Error: {str(e)}"

def main():
    # Page config (same as before)
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
            "tech_stack": [],
            "tech_questions": {}
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
        
        # --- COLLECTING TECH STACK ---
        elif st.session_state.conversation_stage == "collecting_tech_stack":
            tech_list = [tech.strip() for tech in re.split(r"[,/]", user_input) if tech.strip()]
            if tech_list:
                st.session_state.candidate_info["tech_stack"] = tech_list
                response = (
                    f"✅ Saved your tech stack: {', '.join(tech_list)}\n\n"
                    "I'll now generate some technical questions for you..."
                )
                st.session_state.messages.append({"role": "assistant", "content": response})
                with st.chat_message("assistant"):
                    st.markdown(response)
                
                # Generate questions for each technology
                for tech in tech_list:
                    questions = generate_tech_questions(tech, st.session_state.candidate_info["experience"])
                    st.session_state.candidate_info["tech_questions"][tech] = questions
                    
                    q_response = (
                        f"📌 **{tech} Questions:**\n\n"
                        f"{questions}\n\n"
                        "Take your time to answer!"
                    )
                    st.session_state.messages.append({"role": "assistant", "content": q_response})
                    with st.chat_message("assistant"):
                        st.markdown(q_response)
                
                # End conversation
                closing_message = (
                    "🎉 **Screening Complete!**\n\n"
                    "Thank you for your time! A recruiter will review your responses "
                    "and contact you soon.\n\n"
                    "Have a great day! 👋"
                )
                st.session_state.messages.append({"role": "assistant", "content": closing_message})
                with st.chat_message("assistant"):
                    st.markdown(closing_message)
                
                st.session_state.conversation_stage = "completed"
                return  # Prevent further input
            
            else:
                response = "❌ Please enter at least one technology (e.g., Python, JavaScript)."
        
        # --- CONVERSATION COMPLETED ---
        elif st.session_state.conversation_stage == "completed":
            response = "This conversation has ended. Refresh the page to start a new screening."
        
        # Add assistant response to chat
        st.session_state.messages.append({"role": "assistant", "content": response})
        with st.chat_message("assistant"):
            st.markdown(response)

if __name__ == "__main__":
    main()
