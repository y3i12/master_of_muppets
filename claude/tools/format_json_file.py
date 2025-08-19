#!/usr/bin/env python3
import json
import os
import glob

def format_json_file(file_path):
    """Format a JSON file with consistent indentation for readability."""
    try:
        # Read the original file
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # Write back with readable formatting (2-space indentation)
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        
        return True, "Success"
    except json.JSONDecodeError as e:
        return False, f"JSON decode error: {e}"
    except Exception as e:
        return False, f"Error: {e}"

def main():
    # Base directory for knowledge files
    base_dir = "claude/data_store/knowledge"
    
    # Find all JSON files recursively
    pattern = os.path.join(base_dir, "**", "*.json")
    json_files = glob.glob(pattern, recursive=True)
    
    print(f"Found {len(json_files)} JSON files to format")
    
    success_count = 0
    error_count = 0
    
    for file_path in json_files:
        print(f"Processing: {file_path}")
        success, message = format_json_file(file_path)
        
        if success:
            success_count += 1
            print(f"  OK Formatted successfully")
        else:
            error_count += 1
            print(f"  ERROR Failed: {message}")
    
    print(f"\nSummary:")
    print(f"  Successfully formatted: {success_count}")
    print(f"  Errors: {error_count}")
    print(f"  Total files: {len(json_files)}")

if __name__ == "__main__":
    main()