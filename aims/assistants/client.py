"""
Shared OpenAI client module to avoid multiple client instantiations.
"""
from openai import OpenAI
import os
from dotenv import load_dotenv

load_dotenv()

_client = None

def get_client():
    """
    Returns a singleton OpenAI client instance.
    
    Returns:
        OpenAI: The shared OpenAI client instance
    """
    global _client
    
    if _client is None:
        # Initialize the client only once
        _client = OpenAI(
            base_url=os.getenv("BASE_URL"),
            api_key=os.getenv("OR_API_KEY") or os.getenv("OPENAI_API_KEY")
        )
    
    return _client
