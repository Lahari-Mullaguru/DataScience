# Conversation flow prompts
INITIAL_GREETING = """
Hello! I'm TalentBot, your AI hiring assistant. 
I'll help with your initial screening process.

May I have your full name please?
"""

TECH_STACK_PROMPT = """
Great! Now, please list your tech stack (e.g., Python, JavaScript, React).

You can separate technologies with commas.
"""

CLOSING_MESSAGE = """
Screening Complete!

Thank you for your time! A recruiter will review your responses 
and contact you soon.

Have a great day!
"""

# Question generation prompt
TECH_QUESTION_PROMPT = """
Generate 3-5 technical interview questions about {tech} 
suitable for a candidate with {experience} years of experience.

Focus on:
- Core concepts (20%)
- Practical applications (40%)
- Problem-solving scenarios (40%)

Format as a numbered list.
"""
