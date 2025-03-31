# app.py
import streamlit as st
import google.generativeai as genai
from dotenv import load_dotenv
import os
from prompts import INITIAL_GREETING, INFO_COLLECTION_PROMPTS, TECH_QUESTION_PROMPT, CLOSING_MESSAGE, FALLBACK_RESPONSE
from utils import validate_email, validate_phone, is_exit_command

# Load environment variables
load_dotenv()
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

# Configure the Google Generative AI model
genai.configure(api_key=GOOGLE_API_KEY)
model = genai.GenerativeModel(model_name="models/google-genai==1.7.0")

# Initialize session state
if "step" not in st.session_state:
    st.session_state.step = "greeting"
    st.session_state.candidate_data = {}
    st.session_state.messages = []

st.title("TalentBot – AI Hiring Assistant")

# Display chat history
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Bot replies in chat
def bot_reply(text):
    st.session_state.messages.append({"role": "assistant", "content": text})
    with st.chat_message("assistant"):
        st.markdown(text)

# Initial greeting
if st.session_state.step == "greeting":
    bot_reply(INITIAL_GREETING)
    st.session_state.step = "full_name"

# Input from user
user_input = st.chat_input("Type your response...")

if user_input:
    st.session_state.messages.append({"role": "user", "content": user_input})

    if is_exit_command(user_input):
        bot_reply(CLOSING_MESSAGE)
        st.session_state.step = "done"

    elif st.session_state.step == "full_name":
        st.session_state.candidate_data["full_name"] = user_input
        bot_reply(INFO_COLLECTION_PROMPTS["email"])
        st.session_state.step = "email"

    elif st.session_state.step == "email":
        if validate_email(user_input):
            st.session_state.candidate_data["email"] = user_input
            bot_reply(INFO_COLLECTION_PROMPTS["phone"])
            st.session_state.step = "phone"
        else:
            bot_reply("That doesn't look like a valid email. Try again:")

    elif st.session_state.step == "phone":
        if validate_phone(user_input):
            st.session_state.candidate_data["phone"] = user_input
            bot_reply(INFO_COLLECTION_PROMPTS["experience"])
            st.session_state.step = "experience"
        else:
            bot_reply("That doesn't look like a valid phone number. Try again:")

    elif st.session_state.step == "experience":
        st.session_state.candidate_data["experience"] = user_input
        bot_reply(INFO_COLLECTION_PROMPTS["position"])
        st.session_state.step = "position"

    elif st.session_state.step == "position":
        st.session_state.candidate_data["position"] = user_input
        bot_reply(INFO_COLLECTION_PROMPTS["location"])
        st.session_state.step = "location"

    elif st.session_state.step == "location":
        st.session_state.candidate_data["location"] = user_input
        bot_reply(INFO_COLLECTION_PROMPTS["tech_stack"])
        st.session_state.step = "tech_stack"

    elif st.session_state.step == "tech_stack":
        st.session_state.candidate_data["tech_stack"] = user_input
        tech = user_input
        experience = st.session_state.candidate_data.get("experience", "2")

        prompt = TECH_QUESTION_PROMPT.format(tech=tech, experience=experience)

        with st.chat_message("assistant"):
            with st.spinner("Generating technical questions..."):
                response = model.generate_content(prompt)
                st.markdown(response.text)

        st.session_state.step = "done"
        bot_reply(CLOSING_MESSAGE)

    elif st.session_state.step == "done":
        bot_reply("Session ended. Refresh the page to start again.")

    else:
        bot_reply(FALLBACK_RESPONSE)
