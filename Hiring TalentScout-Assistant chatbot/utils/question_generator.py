import openai
from dotenv import load_dotenv
import os
from typing import Optional
from tenacity import retry, stop_after_attempt, wait_exponential

load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
def generate_tech_questions(tech: str, experience: str) -> Optional[str]:
    """Generate technical questions with retry logic"""
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[{
                "role": "user",
                "content": f"""
                Generate 3-5 technical questions about {tech} for a candidate with {experience} years of experience.
                Include:
                - 1 coding exercise
                - 1 system design question
                - 1 best practices question
                Format as Markdown.
                """
            }],
            temperature=0.7,
            max_tokens=500
        )
        return response.choices[0].message.content
    except Exception as e:
        print(f"API Error: {e}")
        return None
