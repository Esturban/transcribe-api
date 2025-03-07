import os
import tempfile
from .client import get_client
from .utils import call_ai

def run_content(content_text):
    """Process content using OpenAI API and return the result"""
    return call_ai(
        user_text=content_text,
        instructions_env_var="CONTENT_INSTRUCTIONS",
        default_instructions="You are a helpful content assistant.",
        title="Content Assistant",
        temperature=float(os.getenv("CONTENT_TEMP", 0.7))
    )
