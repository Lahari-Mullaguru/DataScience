import openai
from dotenv import load_dotenv
import os
from ..prompts import TECH_QUESTION_PROMPT

load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

def generate_tech_questions(tech: str, experience: str) -> str:
    """Generate technical questions using LLM"""
    prompt = TECH_QUESTION_PROMPT.format(tech=tech, experience=experience)
    
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"⚠️ Could not generate questions. Error: {str(e)}"
