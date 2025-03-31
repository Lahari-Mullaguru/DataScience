INITIAL_GREETING = """
Hello! I'm TalentBot, your AI hiring assistant.  
I'll guide you through our initial screening process.

May I have your **full name** please?
"""

INFO_COLLECTION_PROMPTS = {
    "email": "Thanks! What's your **email address**?",
    "phone": "Got it! What's your **phone number**?",
    "experience": "Great! How many **years of experience** do you have?",
    "position": "What **position(s)** are you applying for?",
    "location": "What's your **current location**?",
    "tech_stack": \"\"\"\nPlease list your **tech stack** (e.g., Python, JavaScript, React).  
Separate technologies with commas.\n\"\"\"
}

TECH_QUESTION_PROMPT = """
Generate 3-5 technical questions about {tech} for a candidate with {experience} years of experience.
Format as a Markdown list with:
- Clear numbering
- **Bold** for key concepts
- 1 practical coding question
- 1 architecture/design question
"""

CLOSING_MESSAGE = """
🎉 **Screening Complete!**

Thank you! A recruiter will review your responses and contact you shortly.

Have a great day! 👋
"""

FALLBACK_RESPONSE = """
I didn't quite understand that. Could you rephrase?
(To exit, type 'quit')
"""
