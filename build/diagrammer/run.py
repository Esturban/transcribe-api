import os
from pathlib import Path

script_path = Path(os.path.abspath(__file__))
parent_dir = str(script_path.parent.parent.parent)  # Move up THREE directories
os.chdir(parent_dir)

from openai import OpenAI
from dotenv import load_dotenv
import time
import re
load_dotenv()

client = OpenAI(
  base_url=os.getenv("BASE_URL"),
  api_key = os.getenv("OR_API_KEY") 
)
with open(os.getenv("DIAGRAM_INSTRUCTIONS") , "r") as file:
    system_instructions = file.read()
start_time = time.time()

txt_dir = os.getenv("TXT_DIR")

os.makedirs(os.getenv("TARGET_DIR"), exist_ok=True)
if not os.path.exists(txt_dir):
    raise FileNotFoundError(f"{txt_dir} directory not found")

file_paths = {f: os.path.join(txt_dir, f) for f in os.listdir(txt_dir) if os.path.isfile(os.path.join(txt_dir, f))}
#print(file_paths)
with open("data/dg/complete/Airbnb - Data University.txt", "r",encoding="utf-8",errors="replace") as file:
    user_instructions = file.read()
    
    
    
try:
    completion = client.chat.completions.create(
            extra_headers={
                "HTTP-Referer": os.getenv("REFERER"), 
                "X-Title": os.getenv("TITLE"),
            },
            extra_body={},
            model=os.getenv("OR_MODEL"),
            messages=[{"role": "system", "content": system_instructions},
                {"role": "user", "content": user_instructions}
            ],
            temperature=0.2
            )
except Exception as e:
    print(f"Error: {e}")
    
        #print(completion)
if not os.path.exists(f"{os.getenv("TARGET_DIR")}"): os.mkdir(f"{os.getenv("TARGET_DIR")}")

cleaned_content = re.sub(r'```[\w]*\n|```', '', completion.choices[0].message.content)
with open("test_diagram.json", "w") as file:
        file.write(cleaned_content)
        file.close()

end_time = time.time()
print(f"Total runtime: {end_time - start_time:.2f} seconds")
    