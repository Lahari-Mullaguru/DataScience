import openai
from dotenv import load_dotenv
import os
from typing import Optional

load_dotenv()

def generate_tech_questions(tech: str, experience: str) -> Optional[str]:
    """Generate technical questions with error handling"""
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[{
                "role": "user",
                "content": f"""
                Generate 3-5 technical questions about {tech} for a candidate with {experience} years of experience.
                Focus on:
                - 20% theory (e.g., 'Explain X concept')
                - 50% practical (e.g., 'How would you solve Y?')
                - 30% scenario-based (e.g., 'What would you do if Z happened?')
                Format as a numbered Markdown list.
                """
            }],
            temperature=0.7,
            max_tokens=500
        )
        return response.choices[0].message.content
    except Exception as e:
        print(f"API Error: {e}")  # Log errors for debugging
        return None
