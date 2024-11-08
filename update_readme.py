import os
import re
from pathlib import Path

def extract_notebook_info():
    """
    Scans the repository for .ipynb files and extracts relevant information.
    Returns a list of tuples containing (project_name, notebook_path).
    """
    notebooks = []
    
    # Walk through all directories
    for root, dirs, files in os.walk('.'):
        # Skip hidden directories and specific folders if needed
        if '/.' in root or '\.' in root:
            continue
            
        for file in files:
            if file.endswith('.ipynb'):
                # Get the full path
                full_path = os.path.join(root, file)
                # Convert to forward slashes for consistency
                full_path = full_path.replace('\\', '/')
                # Remove leading './' if present
                if full_path.startswith('./'):
                    full_path = full_path[2:]
                    
                # Extract project name from directory name
                project_name = os.path.basename(os.path.dirname(full_path))
                
                # Format the notebook link in markdown
                notebook_link = f"[{file}]({full_path})"
                
                notebooks.append((project_name, notebook_link))
    
    return sorted(notebooks, key=lambda x: x[0])  # Sort by project name

def update_readme_table(readme_path='README.md'):
    """
    Updates the README.md file with the current notebook information.
    """
    notebooks = extract_notebook_info()
    
    # Read existing README content
    with open(readme_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Create new table content
    table_rows = []
    table_rows.append("| Notebook Project | Notebook |")
    table_rows.append("|-----------------|-----------|")
    
    for project_name, notebook_link in notebooks:
        table_rows.append(f"| {project_name} | {notebook_link} |")
    
    new_table = '\n'.join(table_rows)
    
    # Define regex pattern to find the existing table
    table_pattern = r'\| Notebook Project.*?(?=\n\n|$)'
    
    # Replace the existing table with the new one
    new_content = re.sub(table_pattern, new_table, content, flags=re.DOTALL)
    
    # Write updated content back to README
    with open(readme_path, 'w', encoding='utf-8') as f:
        f.write(new_content)

if __name__ == '__main__':
    update_readme_table()
