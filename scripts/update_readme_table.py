import os
import nbformat
import yaml
import re
from typing import Dict, Optional

def extract_front_matter(notebook_path: str) -> Dict[str, any]:
    """
    Extract YAML front matter from the first markdown cell of a notebook.
    Returns default values if no front matter is found.
    """
    try:
        with open(notebook_path, 'r', encoding='utf-8') as f:
            nb = nbformat.read(f, as_version=4)

        # Look for front matter in the first markdown cell
        if nb.cells and nb.cells[0].cell_type == 'markdown':
            content = nb.cells[0].source
            front_matter_match = re.match(r'^---\n(.*?\n)---\n', content, re.DOTALL)
            
            if front_matter_match:
                try:
                    metadata = yaml.safe_load(front_matter_match.group(1))
                    return {
                        'type': metadata.get('type', 'CPU, Serial'),
                        'required_modules': metadata.get('required_modules', [])
                    }
                except yaml.YAMLError as e:
                    print(f"Error parsing YAML in {notebook_path}: {str(e)}")
                    
        # Return default values if no valid front matter is found
        return {
            'type': 'CPU, Serial',
            'required_modules': []
        }
    except Exception as e:
        print(f"Error processing {notebook_path}: {str(e)}")
        return {
            'type': 'CPU, Serial',
            'required_modules': []
        }

def generate_table_row(project: str, notebook_path: str) -> str:
    """Generate a markdown table row for a notebook."""
    notebook_name = os.path.basename(notebook_path)
    metadata = extract_front_matter(notebook_path)
    
    # Convert required_modules list to formatted string
    modules_str = ', '.join(f'`{module}`' for module in metadata['required_modules']) if metadata['required_modules'] else ''
    
    return f"| {project} | [{notebook_name}](./{project}/{notebook_name}) | {metadata['type']} | {modules_str} |"

def update_readme_table(root_dir: str, readme_path: str):
    """Update the README.md file with current notebook information."""
    # Get all notebooks
    notebooks = []
    for dirpath, dirnames, filenames in os.walk(root_dir):
        if '.git' in dirpath or '.github' in dirpath:
            continue
        
        for filename in filenames:
            if filename.endswith('.ipynb'):
                project = os.path.basename(dirpath)
                full_path = os.path.join(dirpath, filename)
                notebooks.append((project, full_path))

    # Sort notebooks by project name
    notebooks.sort(key=lambda x: x[0].lower())

    # Generate table rows
    table_rows = [generate_table_row(project, nb_path) for project, nb_path in notebooks]

    # Read current README
    with open(readme_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # Find the table section
    table_pattern = r'(\|\s*Notebook Project\s*\|.*?\n\|[-\s|]*\n)(.*?)(?=\n\n|$)'
    table_match = re.search(table_pattern, content, re.DOTALL)
    
    if table_match:
        # Replace table content
        new_content = content.replace(
            table_match.group(0),
            f"{table_match.group(1)}{''.join(row + '\n' for row in table_rows)}"
        )
        
        # Write updated README
        with open(readme_path, 'w', encoding='utf-8') as f:
            f.write(new_content)

if __name__ == '__main__':
    update_readme_table('.', 'README.md')
