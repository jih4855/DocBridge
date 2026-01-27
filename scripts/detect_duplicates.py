import os
import re

def find_duplicate_imports(root_dir):
    duplicates = []
    
    # Extensions to check
    extensions = {'.py', '.ts', '.tsx', '.js', '.jsx'}
    
    # Dirs to ignore
    ignore_dirs = {'node_modules', 'venv', '.venv', '__pycache__', '.git', 'dist', 'build', '.next'}

    for root, dirs, files in os.walk(root_dir):
        # Filter ignored dirs
        dirs[:] = [d for d in dirs if d not in ignore_dirs]
        
        for file in files:
            if os.path.splitext(file)[1] in extensions:
                file_path = os.path.join(root, file)
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        lines = f.readlines()
                        
                    imports_seen = {}
                    
                    for i, line in enumerate(lines):
                        stripped = line.strip()
                        # Simple detection: check if line starts with import keyword and is identical to a previous line
                        # This catches exact duplicate lines.
                        is_import = False
                        if file.endswith('.py'):
                            if stripped.startswith('import ') or stripped.startswith('from '):
                                is_import = True
                        else: # JS/TS
                            if stripped.startswith('import '):
                                is_import = True
                        
                        if is_import:
                            # Normalize spaces for comparison? strict for now
                            if stripped in imports_seen:
                                duplicates.append({
                                    'file': file_path,
                                    'line': i + 1,
                                    'content': stripped,
                                    'original_line': imports_seen[stripped]
                                })
                            else:
                                imports_seen[stripped] = i + 1
                                
                except Exception as e:
                    print(f"Error reading {file_path}: {e}")

    return duplicates

if __name__ == "__main__":
    results = find_duplicate_imports(".")
    if results:
        print(f"Found {len(results)} duplicate imports:")
        for dup in results:
            print(f"File: {dup['file']}:{dup['line']}")
            print(f"  Duplicate: {dup['content']}")
            print(f"  First seen at line: {dup['original_line']}")
            print("-" * 20)
    else:
        print("No duplicate imports found.")
