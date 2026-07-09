#!/bin/bash

# Check if a directory is provided
if [ -z "$1" ]; then
  echo "Usage: $0 /path/to/txt/files"
  exit 1
fi

# The directory containing the text files
DIR=$1

# Get the current date in YYYY-MM-DD format
CURRENT_DATE=$(date +"%Y-%m-%d")

# The output file, located in the same directory as the script
OUTPUT_FILE="$(dirname "$0")/collated_text_${CURRENT_DATE}.md"

# Clear the output file if it exists
> "$OUTPUT_FILE"

# Loop through all .txt files in the directory
for file in "$DIR"/*.txt; do
  # Check if the file exists and is not the output file itself
  if [ -f "$file" ] && [ "$(basename "$file")" != "$(basename "$OUTPUT_FILE")" ]; then
    # Get the filename without the path
    filename=$(basename "$file")
    
    # Append the title and separator to the output file
    echo "## $filename" >> "$OUTPUT_FILE"
    echo "---" >> "$OUTPUT_FILE"
    
    # Append the file content
    cat "$file" >> "$OUTPUT_FILE"
    
    # Append the final separator
    echo "" >> "$OUTPUT_FILE"
    echo "---" >> "$OUTPUT_FILE"
    echo "" >> "$OUTPUT_FILE"
  fi
done

echo "Collated text files into $OUTPUT_FILE"
