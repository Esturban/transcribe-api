#!/usr/bin/env python3
import os
import sys
import argparse
from aims.utils import unicode_spaces, replace_spaces_in_lines


def has_unicode_spaces(content: str) -> bool:
    """Check if the content already contains any of the unicode spaces."""
    for space_value in unicode_spaces.values():
        if space_value in content:
            return True
    return False


def process_text_file(file_path: str, space_types: list, dry_run: bool = False) -> bool:
    """Process a single text file, replacing spaces with unicode if needed.
    
    Args:
        file_path: Path to the text file
        space_types: List of unicode space types to use
        dry_run: If True, don't modify files, just report what would be done
        
    Returns:
        True if file was modified, False otherwise
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Skip if file already contains unicode spaces
        if has_unicode_spaces(content):
            print(f"Skipping {file_path}: Already contains unicode spaces")
            return False
        
        # Replace spaces with unicode spaces
        modified_lines = replace_spaces_in_lines(content.split('\n'), space_types)
        modified_content = '\n'.join(modified_lines)
        
        if dry_run:
            print(f"Would modify: {file_path}")
            return True
        
        # Write modified content back to file
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(modified_content)
        
        print(f"Modified: {file_path}")
        return True
        
    except Exception as e:
        print(f"Error processing {file_path}: {str(e)}")
        return False


def process_directory(directory: str, space_types: list, dry_run: bool = False) -> tuple:
    """Process all .txt files in a directory, replacing spaces with unicode.
    
    Returns:
        (processed_count, skipped_count, error_count)
    """
    if not os.path.exists(directory):
        print(f"Error: Directory '{directory}' does not exist")
        return (0, 0, 0)
        
    processed = 0
    skipped = 0
    errors = 0
    
    for root, _, files in os.walk(directory):
        for file in files:
            if file.lower().endswith('.txt'):
                file_path = os.path.join(root, file)
                result = process_text_file(file_path, space_types, dry_run)
                
                if result is True:
                    processed += 1
                elif result is False:
                    skipped += 1
                else:
                    errors += 1
    
    return (processed, skipped, errors)


def main():
    parser = argparse.ArgumentParser(description='Replace spaces with unicode spaces in text files')
    parser.add_argument('directory', help='Directory containing text files to process')
    parser.add_argument('--space-types', nargs='+', default=['Thin Space', 'Hair Space3'],
                        choices=list(unicode_spaces.keys()),
                        help='Types of unicode spaces to use (default: Thin Space and Hair Space3)')
    parser.add_argument('--dry-run', action='store_true', 
                        help='Show what would be changed without modifying files')
    
    args = parser.parse_args()
    
    # Validate space types
    invalid_spaces = [s for s in args.space_types if s not in unicode_spaces]
    if invalid_spaces:
        print(f"Error: Invalid space types: {', '.join(invalid_spaces)}")
        print(f"Available space types: {', '.join(unicode_spaces.keys())}")
        return 1
    
    print(f"Processing directory: {args.directory}")
    print(f"Using space types: {', '.join(args.space_types)}")
    if args.dry_run:
        print("DRY RUN - no files will be modified")
    
    processed, skipped, errors = process_directory(args.directory, args.space_types, args.dry_run)
    
    print("\nSummary:")
    print(f"  Files processed: {processed}")
    print(f"  Files skipped (already had unicode): {skipped}")
    print(f"  Files with errors: {errors}")
    
    return 0


if __name__ == "__main__":
    sys.exit(main())