import os
import nbformat
import yaml
import re
from typing import List, Dict, Tuple

def extract_front_matter(notebook_path: str) -> Dict:
    """
    Extract YAML front matter from the first markdown cell of a notebook.
    Returns default values if no front matter is found.
    """
    try:
        with open(notebook_path, 'r', encoding='utf-8') as f:
            nb = nbformat.read(f, as_version=4)

        if nb.cells and nb.cells[0].cell_type == 'markdown':
            content = nb.cells[0].source.strip()
            front_matter_match = re.match(r'^---\n(.*?\n)---\n?', content, re.DOTALL)
            if front_matter_match:
                metadata = yaml.safe_load(front_matter_match.group(1))
                return {
                    'type': metadata.get('type', 'CPU, Serial'),
                    'required_modules': metadata.get('required_modules', [])
                }
    except Exception as e:
        print(f"Error processing {notebook_path}: {e}")
    return {'type': 'CPU, Serial', 'required_modules': []}

def parse_table(content: str) -> List[Dict]:
    """
    Parse existing notebook table into a dictionary.
    """
    entries = []
    table_pattern = r'\|\s*([^|]+)\s*\|\s*\[([^]]+)]\([^)]*\)\s*\|\s*([^|]+)\s*\|\s*(.*)\|'
    for match in re.finditer(table_pattern, content):
        entries.append({
            'project': match.group(1).strip(),
            'notebook': match.group(2).strip(),
            'type': match.group(3).strip(),
            'modules': match.group(4).strip()
        })
    return entries

def generate_table_rows(notebooks: List[Tuple[str, str]], existing_entries: List[Dict]) -> List[Dict]:
    """
    Generate markdown rows for the notebook table.
    """
    rows = []
    for project, notebook_path in notebooks:
        metadata = extract_front_matter(notebook_path)
        modules_str = ', '.join(f'`{mod}`' for mod in metadata['required_modules']) if metadata['required_modules'] else ''
        rows.append({
            'project': project,
            'notebook': os.path.basename(notebook_path),
            'type': metadata['type'],
            'modules': modules_str
        })
    return rows

def format_table_section(title: str, notebooks: List[Dict]) -> str:
    """
    Format a section of the table with headers and rows.
    """
    if not notebooks:
        return ""
    
    table_header = "| Notebook Project | Notebook | Type | Required (Sub) Modules |\n|-----------------|----------|------|------------------------|\n"
    rows = "\n".join(
        f"| {entry['project']} | [{entry['notebook']}](./{entry['project']}/{entry['notebook']}) | {entry['type']} | {entry['modules']} |"
        for entry in notebooks
    )
    return f"### {title}\n\n{table_header}{rows}\n"

def update_readme(notebooks: List[Tuple[str, str]], readme_path: str):
    """
    Update the README.md file with alphabetically sorted notebooks.
    """
    print(f"Updating README: {readme_path}")
    with open(readme_path, 'r', encoding='utf-8') as f:
        content = f.read()

    new_entries = generate_table_rows(notebooks, [])
    sorted_entries = sorted(new_entries, key=lambda x: x['notebook'].lower())
    
    rows = "\n".join(
        f"| {entry['project']} | [{entry['notebook']}](./{entry['project']}/{entry['notebook']}) | {entry['type']} | {entry['modules']} |"
        for entry in sorted_entries
    )

    table_pattern = r'(\|\s*Notebook Project\s*\|.*?\n\|[-\s|]*\n)(.*?)(?=\n\n|$)'
    content = re.sub(table_pattern, f"\\1{rows}\n", content, flags=re.DOTALL)

    with open(readme_path, 'w', encoding='utf-8') as f:
        f.write(content)

def update_serial_parallel_table(notebooks: List[Tuple[str, str]], md_path: str):
    """
    Update the Serial/Parallel table with sorted entries.
    """
    print(f"Updating Serial/Parallel table: {md_path}")
    new_entries = generate_table_rows(notebooks, [])
    
    serial_notebooks = sorted(
        [entry for entry in new_entries if 'Serial' in entry['type']],
        key=lambda x: x['notebook'].lower()
    )
    parallel_notebooks = sorted(
        [entry for entry in new_entries if 'Parallel' in entry['type']],
        key=lambda x: x['notebook'].lower()
    )

    content = (
        "## Expanse-Notebooks-dev: Notebook Table Sorted by Type (Serial/Parallel)\n\n"
        + format_table_section("Serial", serial_notebooks)
        + "\n"
        + format_table_section("Parallel", parallel_notebooks)
    )

    with open(md_path, 'w', encoding='utf-8') as f:
        f.write(content)

def update_cpu_gpu_table(notebooks: List[Tuple[str, str]], md_path: str):
    """
    Update the CPU/GPU table with sorted entries.
    """
    print(f"Updating CPU/GPU table: {md_path}")
    new_entries = generate_table_rows(notebooks, [])
    
    cpu_notebooks = []
    gpu_notebooks = []
    hybrid_notebooks = []

    for entry in new_entries:
        notebook_type = entry['type'].lower()
        if 'cpu, gpu' in notebook_type or 'gpu, cpu' in notebook_type:
            hybrid_notebooks.append(entry)
        elif 'gpu' in notebook_type:
            gpu_notebooks.append(entry)
        elif 'cpu' in notebook_type or 'serial' in notebook_type:
            cpu_notebooks.append(entry)
        else:
            cpu_notebooks.append(entry)

    # Sort each category
    for notebooks in [cpu_notebooks, gpu_notebooks, hybrid_notebooks]:
        notebooks.sort(key=lambda x: x['notebook'].lower())

    content = (
        "## Expanse-Notebooks-dev: Notebook Table Sorted by Type (CPU/GPU)\n\n"
        + format_table_section("CPU Notebooks", cpu_notebooks)
        + "\n"
        + format_table_section("GPU Notebooks", gpu_notebooks)
        + "\n"
        + format_table_section("Hybrid (CPU/GPU) Notebooks", hybrid_notebooks)
    )

    with open(md_path, 'w', encoding='utf-8') as f:
        f.write(content)

def main():
    # Configuration
    root_dir = '.'
    readme_path = 'README.md'
    serial_parallel_path = 'Notebook_Table_Type(Serial_Parallel).md'
    cpu_gpu_path = 'Notebook_Table_Type(CPU_GPU).md'

    # Scan for notebooks
    print("Scanning for notebooks...")
    notebooks = []
    for dirpath, _, filenames in os.walk(root_dir):
        for filename in filenames:
            if filename.endswith('.ipynb'):
                project = os.path.basename(dirpath)
                notebook_path = os.path.join(dirpath, filename)
                print(f"Found notebook: {notebook_path}")
                notebooks.append((project, notebook_path))

    print(f"Found {len(notebooks)} notebooks")

    # Update all three tables
    try:
        update_readme(notebooks, readme_path)
        update_serial_parallel_table(notebooks, serial_parallel_path)
        update_cpu_gpu_table(notebooks, cpu_gpu_path)
        print("Successfully updated all tables!")
    except Exception as e:
        print(f"Error updating tables: {str(e)}")

if __name__ == '__main__':
    main()
