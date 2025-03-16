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
txt_dir = os.getenv("TEACHING_TXT")  # Changed from TXT_DIR to TEACHING_TXT
teaching_dir = os.getenv("TEACHING_DIR")  # Get the output directory

# Ensure target directory exists (keeping this for backward compatibility)
os.makedirs(os.getenv("TARGET_DIR"), exist_ok=True)
# Ensure teaching directory exists
os.makedirs(teaching_dir, exist_ok=True)

if not os.path.exists(txt_dir):
    raise FileNotFoundError(f"{txt_dir} directory not found")

file_paths = {f: os.path.join(txt_dir, f) for f in os.listdir(txt_dir) if os.path.isfile(os.path.join(txt_dir, f)) and f.endswith('.txt')}

processed_count = 0
skipped_count = 0

for filename, filepath in file_paths.items():
    # Create output filename (keep same name but in teaching_dir)
    output_filepath = os.path.join(teaching_dir, filename)
    
    # Check if output file already exists
    if os.path.exists(output_filepath):
        print(f"Skipping {filename} - output already exists")
        skipped_count += 1
        continue
    
    print(f"Processing {filename}...")
    
    try:
        # Read the input file
        with open(filepath, "r", encoding="utf-8", errors="replace") as file:
            user_instructions = file.read()

        # Use the utility function for the API call
        response = call_ai(
            user_text=user_instructions,
            instructions_env_var="TEACHING_INSTRUCTIONS",
            default_instructions="Create a teaching plan based on the user instructions.",
            title="Teaching Assistant",
            temperature=0.2,
            clean_markdown=True
        )
        
        if isinstance(response, dict) and "error" in response:
            print(f"Error processing {filename}: {response['error']}")
        else:
            # Write the response to the output file
            with open(output_filepath, "w", encoding="utf-8") as file:
                file.write(response)
            processed_count += 1
            print(f"Successfully processed {filename}")
                
    except Exception as e:
        print(f"Error processing {filename}: {e}")

end_time = time.time()
print(f"Total runtime: {end_time - start_time:.2f} seconds")
print(f"Files processed: {processed_count}, Files skipped: {skipped_count}")
