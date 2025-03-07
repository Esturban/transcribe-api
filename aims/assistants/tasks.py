import os
import csv
import re
import tempfile
from pathlib import Path
import time
from .client import get_client
from .utils import call_ai

def run_tasks(task_text):
    """Process a single task using OpenAI API and return the result"""
    return call_ai(
        user_text=task_text,
        instructions_env_var="TASK_INSTRUCTIONS",
        default_instructions="You are a helpful task assistant.",
        title="Task Assistant",
        temperature=0.2,
        clean_markdown=True
    )

def run_tasks_batch(csv_path):
    """Process multiple tasks from a CSV file and return results as a list"""
    # Read tasks from CSV file
    tasks = []
    try:
        with open(csv_path, 'r', encoding='utf-8', errors='replace') as csvfile:
            csv_reader = csv.reader(csvfile)
            try:
                next(csv_reader)  # Skip the header row
            except StopIteration:
                return {"error": "CSV file is empty"}
            
            for row in csv_reader:
                if row and len(row) > 0:
                    tasks.append(row[0])
    except Exception as e:
        return {"error": f"Failed to read CSV: {str(e)}"}

    results = []
    
    # Process each task
    for i, task in enumerate(tasks):
        result = call_ai(
            user_text=task,
            instructions_env_var="TASK_INSTRUCTIONS",
            default_instructions="You are a helpful task assistant.",
            title="Task Assistant",
            temperature=0.2,
            clean_markdown=True
        )
        
        results.append({
            "task": task,
            "result": result if not isinstance(result, dict) else result.get("error", "Unknown error")
        })
    
    return results
