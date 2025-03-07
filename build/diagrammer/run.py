import os
from pathlib import Path
import time
import re
import sys
script_path = Path(os.path.abspath(__file__))
parent_dir = str(script_path.parent.parent.parent) 
os.chdir(parent_dir)
sys.path.insert(0, parent_dir)

from aims.assistants.utils import call_ai

start_time = time.time()
txt_dir = os.getenv("TXT_DIR")

os.makedirs(os.getenv("TARGET_DIR"), exist_ok=True)
if not os.path.exists(txt_dir):
    raise FileNotFoundError(f"{txt_dir} directory not found")

file_paths = {f: os.path.join(txt_dir, f) for f in os.listdir(txt_dir) if os.path.isfile(os.path.join(txt_dir, f))}

with open("data/dg/complete/Airbnb - Data University.txt", "r", encoding="utf-8", errors="replace") as file:
    user_instructions = file.read()

try:
    # Use the utility function for the API call
    response = call_ai(
        user_text=user_instructions,
        instructions_env_var="DIAGRAM_INSTRUCTIONS",
        default_instructions="Create a diagram based on the text.",
        title="Diagram Assistant",
        temperature=0.2,
        clean_markdown=True
    )
    
    if isinstance(response, dict) and "error" in response:
        print(f"Error: {response['error']}")
    else:
        if not os.path.exists(f"{os.getenv('TARGET_DIR')}"):
            os.mkdir(f"{os.getenv('TARGET_DIR')}")
        
        with open("test_diagram.json", "w") as file:
            file.write(response)
            
except Exception as e:
    print(f"Error: {e}")

end_time = time.time()
print(f"Total runtime: {end_time - start_time:.2f} seconds")
