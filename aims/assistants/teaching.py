import os
from .utils import call_ai

def run_teaching(teaching_text):
    """Process teaching content using OpenAI API and return the result"""
    return call_ai(
        user_text=teaching_text,
        instructions_env_var="TEACHING_INSTRUCTIONS",
        default_instructions="You are a helpful teaching assistant. Explain concepts clearly and provide examples.",
        title="Teaching Assistant",
        temperature=float(os.getenv("TEACHING_TEMP", 0.5))
    )
