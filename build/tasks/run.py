import os
import csv
from pathlib import Path

script_path = Path(os.path.abspath(__file__))
parent_dir = str(script_path.parent.parent.parent)  # Move up THREE directories
os.chdir(parent_dir)

from openai import OpenAI
from dotenv import load_dotenv
import time
import re
load_dotenv()

# Define path to CSV file - you can adjust this or add to .env
CSV_PATH = "data/tasks.csv"  # You may want to set this in .env as TASKS_CSV

client = OpenAI(
  base_url=os.getenv("BASE_URL"),
  api_key = os.getenv("OR_API_KEY") 
)

with open(os.getenv("TASK_INSTRUCTIONS"), "r") as file:
    system_instructions = file.read()

# Create output directory
target_dir = "data/tasks/processed/"
os.makedirs(target_dir, exist_ok=True)

# Read tasks from CSV file
tasks = []
with open(CSV_PATH, 'r', encoding='utf-8',errors='replace') as csvfile:
    csv_reader = csv.reader(csvfile)
    try:
        next(csv_reader)  # Skip the header row
    except StopIteration:
        print("CSV file is empty")
        exit(1)
    
    for row in csv_reader:
        if row and len(row) > 0:
            tasks.append(row[0])

print(f"Found {len(tasks)} tasks to process")

# Process each task
for i, task in enumerate(tasks):
    print(f"Processing task {i+1}/{len(tasks)}: {task[:30]}...")
    start_time = time.time()
    
    try:
        completion = client.chat.completions.create(
            extra_headers={
                "HTTP-Referer": os.getenv("REFERER"), 
                "X-Title": os.getenv("TITLE"),
            },
            extra_body={},
            model=os.getenv("OR_MODEL"),
            messages=[
                {"role": "system", "content": system_instructions},
                {"role": "user", "content": task}
            ],
            temperature=0.2
        )
        
        # Generate a filename based on the task (use first few words)
        task_words = re.sub(r'[^a-zA-Z0-9\s]', '', task.strip())[:30].strip().replace(' ', '_')
        output_filename = f"task_{i+1}_{task_words}.txt"
        
        # Clean and save content
        cleaned_content = re.sub(r'```[\w]*\n|```', '', completion.choices[0].message.content)
        with open(os.path.join(target_dir, output_filename), "w") as file:
            file.write(cleaned_content)
        
        end_time = time.time()
        print(f"  Completed in {end_time - start_time:.2f} seconds")
        
    except Exception as e:
        print(f"  Error processing task {i+1}: {e}")

print("All tasks completed!")