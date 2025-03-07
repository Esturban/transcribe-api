import os
import csv
from pathlib import Path
import sys
import time
import re

script_path = Path(os.path.abspath(__file__))
parent_dir = str(script_path.parent.parent.parent)  # Move up THREE directories
os.chdir(parent_dir)
sys.path.insert(0, parent_dir)

from dotenv import load_dotenv
from aims.assistants import run_tasks
load_dotenv()

# Define path to CSV file - you can adjust this or add to .env
CSV_PATH = os.getenv("TASKS_CSV", "data/tasks.csv")

# Create output directory
target_dir = "data/tasks/processed/"
os.makedirs(target_dir, exist_ok=True)

# Read tasks from CSV file
tasks = []
with open(CSV_PATH, 'r', encoding='utf-8', errors='replace') as csvfile:
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
    # Generate a filename based on the task (use first few words)
    task_words = re.sub(r'[^a-zA-Z0-9\s]', '', task.strip())[:30].strip().replace(' ', '_')
    output_filename = f"task_{i+1}_{task_words}.txt"
    
    if output_filename not in os.listdir(target_dir):
        try:
            # Use the run_tasks function from aims.assistants
            result = run_tasks(task)
            
            # Handle the response
            if isinstance(result, dict) and "error" in result:
                print(f"  Error processing task {i+1}: {result['error']}")
                continue
            
            # Write the result to the output file
            with open(os.path.join(target_dir, output_filename), "w") as file:
                file.write(result)
            
            end_time = time.time()
            print(f"  Completed in {end_time - start_time:.2f} seconds")
            
        except Exception as e:
            print(f"  Error processing task {i+1}: {e}")
    else: 
        print(f"  Skipping task {i+1} (output file already exists)")

print("All tasks completed!")