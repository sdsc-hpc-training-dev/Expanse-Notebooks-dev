import os
import json
import yaml
import re
from pathlib import Path
import sys

def extract_notebook_metadata(notebook_path):
    """Extract metadata from Jupyter notebook header."""
    print(f"Processing notebook: {notebook_path}")
    try:
        with open(notebook_path, 'r', encoding='utf-8') as f:
            notebook = json.load(f)
        
        # Look for metadata in the first markdown cell
        for cell in notebook['cells']:
            if cell['cell_type'] == 'markdown':
                content = cell['source']
                if isinstance(content, list):
                    content = ''.join(content)
                
                # Extract YAML metadata between --- markers
                yaml_match = re.search(r'---\n(.*?)\n---', content, re.DOTALL)
                if yaml_match:
                    try:
                        metadata = yaml.safe_load(yaml_match.group(1))
                        print(f"Found metadata: {metadata}")
                        return {
                            'type': metadata.get('type', ''),
                            'required_modules': metadata.get('required_modules', [])
                        }
                    except yaml.YAMLError as e:
                        print(f"YAML parsing error: {e}")
                        continue
        
        print("No metadata found in notebook")
        return {'type': '', 'required_modules': []}
    except Exception as e:
        print(f"Error processing notebook {notebook_path}: {e}")
        return {'type': '', 'required_modules': []}

def update_notebook_table(repo_path):
    """Update the notebook table markdown file."""
    print(f"Starting update process in: {repo_path}")
    serial_notebooks = []
    parallel_notebooks = []
    
    # Recursively find all .ipynb files
    notebook_files = list(Path(repo_path).rglob('*.ipynb'))
    print(f"Found {len(notebook_files)} notebook files")
    
    for notebook_path in notebook_files:
        if '.ipynb_checkpoints' in str(notebook_path):
            continue
            
        try:
            metadata = extract_notebook_metadata(notebook_path)
            
            # Get relative path from repo root
            rel_path = notebook_path.relative_to(repo_path)
            project_name = rel_path.parent.name
            notebook_name = rel_path.name
            
            entry = {
                'project': project_name,
                'notebook': f'[{notebook_name}](./{rel_path})',
                'type': metadata['type'],
                'modules': ', '.join(metadata['required_modules'])
            }
            
            print(f"Processing entry: {entry}")
            
            # Sort into serial or parallel based on metadata
            if 'Parallel' in metadata['type']:
                parallel_notebooks.append(entry)
                print(f"Added to parallel notebooks: {project_name}")
            else:
                serial_notebooks.append(entry)
                print(f"Added to serial notebooks: {project_name}")
                
        except Exception as e:
            print(f"Error processing {notebook_path}: {e}")
            continue
    
    print(f"Found {len(serial_notebooks)} serial notebooks and {len(parallel_notebooks)} parallel notebooks")
    
    # Generate markdown content
    md_content = "## Expanse-Notebooks-dev: Notebook Table Sorted by Type (Serial/Parallel)\n\n"
    
    # Serial notebooks table
    md_content += "### Serial Notebooks\n\n"
    md_content += "| Notebook Project | Notebook | Type | Required (Sub) Modules |\n"
    md_content += "|-----------------|-----------|------|----------------------|\n"
    for entry in sorted(serial_notebooks, key=lambda x: x['project']):
        md_content += f"| {entry['project']} | {entry['notebook']} | {entry['type']} | {entry['modules']} |\n"
    
    # Parallel notebooks table
    md_content += "\n### Parallel Notebooks\n\n"
    md_content += "| Notebook Project | Notebook | Type | Required (Sub) Modules |\n"
    md_content += "|-----------------|-----------|------|----------------------|\n"
    for entry in sorted(parallel_notebooks, key=lambda x: x['project']):
        md_content += f"| {entry['project']} | {entry['notebook']} | {entry['type']} | {entry['modules']} |\n"
    
    # Write to file
    table_path = os.path.join(repo_path, 'Notebook_Table_Type(Serial_Parallel).md')
    print(f"Writing to {table_path}")
    try:
        with open(table_path, 'w', encoding='utf-8') as f:
            f.write(md_content)
        print("Successfully wrote table file")
    except Exception as e:
        print(f"Error writing file: {e}")
        raise

if __name__ == '__main__':
    try:
        update_notebook_table('.')
    except Exception as e:
        print(f"Error in main: {e}")
        sys.exit(1)
