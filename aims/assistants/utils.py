"""
Utility functions for assistant modules.
"""
import os
import re
from .client import get_client

def call_ai(
    user_text, 
    instructions_env_var, 
    default_instructions="You are a helpful assistant.",
    title="Assistant", 
    temperature=0.7,
    model=None,
    clean_markdown=False
):
    """
    Make an OpenAI API call with standardized configuration.
    
    Args:
        user_text (str): The user's text to process
        instructions_env_var (str): Environment variable name for system instructions
        default_instructions (str): Default instructions if env var not found
        title (str): Title for X-Title header
        temperature (float): Temperature for the model
        model (str): Model to use, defaults to OR_MODEL from env
        clean_markdown (bool): Whether to clean markdown code blocks from response
        
    Returns:
        str or dict: The processed text or error message
    """
    client = get_client()
    
    # Load system instructions
    try:
        with open(os.getenv(instructions_env_var), "r") as file:
            system_instructions = file.read()
    except (FileNotFoundError, TypeError):
        system_instructions = default_instructions
    
    try:
        completion = client.chat.completions.create(
            extra_headers={
                "HTTP-Referer": os.getenv("REFERER", "https://api.example.com"), 
                "X-Title": os.getenv("TITLE", title),
            },
            extra_body={},
            model=model or os.getenv("OR_MODEL", "gpt-3.5-turbo"),
            messages=[
                {"role": "system", "content": system_instructions},
                {"role": "user", "content": user_text}
            ],
            temperature=float(temperature)
        )
        
        content = completion.choices[0].message.content
        
        # Clean markdown code blocks if requested
        if clean_markdown:
            content = re.sub(r'```[\w]*\n|```', '', content)
            
        return content
        
    except Exception as e:
        return {"error": str(e)}
