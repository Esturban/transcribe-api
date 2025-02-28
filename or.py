from openai import OpenAI
import os
import time
from dotenv import load_dotenv
load_dotenv()

client = OpenAI(
  base_url=os.getenv("BASE_URL"),
  api_key = os.getenv("OR_API_KEY") 
)
with open(os.getenv("SYSTEM_INSTRUCTIONS"), "r") as file:
    system_instructions = file.read()
start_time = time.time()

txt_dir = os.getenv("TXT_DIR")
if not os.path.exists(txt_dir):
    raise FileNotFoundError(f"{txt_dir} directory not found")

file_paths = {f: os.path.join(txt_dir, f) for f in os.listdir(txt_dir) if os.path.isfile(os.path.join(txt_dir, f))}

for f, full_path in file_paths.items():
    
    with open(full_path, "r") as file:
        user_instructions = file.read()

    if not os.path.exists(f"{os.getenv("TARGET_DIR")}{f}"):
        print(f"Processing {f}...")
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
            temperature=0.2,
            )
        except Exception as e:
            print(f"Error: {e}")
            continue
        #print(completion)
        if not os.path.exists(f"{os.getenv("TARGET_DIR")}"): os.mkdir(f"{os.getenv("TARGET_DIR")}")
            
        with open(f"{os.getenv('TARGET_DIR')}{f}", "w") as file:
            file.write(completion.choices[0].message.content)
            file.close()

end_time = time.time()
print(f"Total runtime: {end_time - start_time:.2f} seconds")
    