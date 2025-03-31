import streamlit as st
import google.generativeai as genai
from prompts import (
    greeting_prompt,
    candidate_info_prompt,
    tech_question_prompt,
    fallback_prompt,
    goodbye_prompt,
)
from utils import (
    validate_email,
    validate_phone,
    anonymize_data,
    generate_session_id,
    is_exit_command,
)
import os
from dotenv import load_dotenv

load_dotenv()
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
model = genai.GenerativeModel("gemini-pro")

st.set_page_config(page_title="TalentScout AI Hiring Assistant", layout="centered")

if "history" not in st.session_state:
    st.session_state.history = []
    st.session_state.session_id = generate_session_id()

st.title("TalentScout - AI Hiring Assistant")

with st.expander("Data Privacy Notice"):
    st.write(
        "All information entered is simulated and anonymized for testing purposes only. "
        "This app complies with GDPR data privacy practices by not storing any personal data persistently."
    )

st.markdown("Welcome to TalentScout! Please fill out the details below to begin.")

with st.form("candidate_form"):
    full_name = st.text_input("Full Name")
    email = st.text_input("Email Address")
    phone = st.text_input("Phone Number")
    experience = st.slider("Years of Experience", 0, 30, 1)
    desired_role = st.text_input("Desired Position")
    location = st.text_input("Current Location")
    tech_stack = st.text_area("Tech Stack (comma-separated):", placeholder="e.g., Python, Django, React")

    submitted = st.form_submit_button("Submit")

if submitted:
    if not validate_email(email):
        st.error("Please enter a valid email.")
    elif not validate_phone(phone):
        st.error("Please enter a valid phone number.")
    else:
        candidate_info = {
            "name": full_name,
            "email": email,
            "phone": phone,
            "experience": experience,
            "role": desired_role,
            "location": location,
            "tech_stack": tech_stack,
        }

        anonymized_info = anonymize_data(candidate_info)

        st.session_state.history.append(f"🧑 Candidate: {full_name}")
        st.success("Candidate information recorded successfully.")

        with st.spinner("Generating technical questions..."):
            prompt = tech_question_prompt(tech_stack)
            response = model.generate_content(prompt)
            st.markdown("### 🧪 Technical Questions")
            st.write(response.text)
            st.session_state.history.append(f"🧪 Questions: {response.text}")

st.markdown("---")
st.markdown("### 💬 Chat")

user_input = st.text_input("Ask a follow-up question or type 'exit' to end the session:")

if user_input:
    if is_exit_command(user_input):
        st.write(goodbye_prompt())
    else:
        try:
            response = model.generate_content(user_input)
            st.write(f"{response.text}")
            st.session_state.history.append(f"{user_input}")
            st.session_state.history.append(f"{response.text}")
        except Exception:
            st.write(fallback_prompt())
