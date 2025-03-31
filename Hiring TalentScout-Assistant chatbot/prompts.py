def greeting_prompt():
    return "Hello! I'm TalentScout, your virtual hiring assistant. I'll help gather your details and assess your technical strengths. Let's begin!"

def candidate_info_prompt(name, experience, role, location):
    return (
        f"Candidate Name: {name}\n"
        f"Experience: {experience} years\n"
        f"Desired Role: {role}\n"
        f"Current Location: {location}\n\n"
        f"Please confirm that this information is correct."
    )

def tech_question_prompt(tech_stack):
    return (
        f"You are a technical interviewer. Generate 3 to 5 challenging and relevant interview questions "
        f"for the following technologies: {tech_stack}. Make sure the questions test both theoretical knowledge "
        f"and practical experience."
    )

def fallback_prompt():
    return "I'm sorry, I didn't understand that. Could you please rephrase or clarify?"

def goodbye_prompt():
    return "Thank you for your time! We'll review your responses and reach out with next steps. Have a great day!"
