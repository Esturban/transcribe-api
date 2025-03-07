import os
from pathlib import Path
import sys
import time

script_path = Path(os.path.abspath(__file__))
parent_dir = str(script_path.parent.parent.parent)  # Move up THREE directories
os.chdir(parent_dir)
sys.path.insert(0, parent_dir)

from aims.assistants import run_content


start_time = time.time()

txt_dir = os.getenv("TXT_DIR")
target_dir = os.getenv("TARGET_DIR")
os.makedirs(target_dir, exist_ok=True)
if not os.path.exists(txt_dir):
    raise FileNotFoundError(f"{txt_dir} directory not found")

file_paths = {f: os.path.join(txt_dir, f) for f in os.listdir(txt_dir) if os.path.isfile(os.path.join(txt_dir, f))}

for f, full_path in file_paths.items():
    target_file_path = f"{target_dir}{f}"
    
    if not os.path.exists(target_file_path):
        print(f"Processing {f}...")
        
        try:
            with open(full_path, "r", encoding="utf-8", errors="replace") as file:
                user_instructions = file.read()
            result = run_content(user_instructions)
            
            if isinstance(result, dict) and "error" in result:
                print(f"Error processing {f}: {result['error']}")
                continue
                
            with open(target_file_path, "w") as file:
                file.write(result)
                
        except Exception as e:
            print(f"Error: {e}")
            continue
    else:
        print(f"Skipping {f} (already exists)")

end_time = time.time()
print(f"Total runtime: {end_time - start_time:.2f} seconds")
