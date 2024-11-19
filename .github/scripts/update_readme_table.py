import os
import nbformat
import yaml
import re

def extract_front_matter(notebook_path):
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

def parse_table(content):
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

def generate_table_rows(notebooks, existing_entries):
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

def update_readme(notebooks, readme_path):
    """
    Update the README.md file with sorted notebooks.
    """
    with open(readme_path, 'r', encoding='utf-8') as f:
        content = f.read()

    existing_entries = parse_table(content)
    new_entries = generate_table_rows(notebooks, existing_entries)

    # Sort all notebooks alphabetically
    sorted_entries = sorted(new_entries, key=lambda x: x['notebook'].lower())

    # Generate rows for README
    rows = "\n".join(
        f"| {entry['project']} | [{entry['notebook']}](./{entry['project']}/{entry['notebook']}) | {entry['type']} | {entry['modules']} |"
        for entry in sorted_entries
    )

    # Replace the table in README.md
    table_pattern = r'(\|\s*Notebook Project\s*\|.*?\n\|[-\s|]*\n)(.*?)(?=\n\n|$)'
    content = re.sub(table_pattern, f"\\1{rows}\n", content, flags=re.DOTALL)

    with open(readme_path, 'w', encoding='utf-8') as f:
        f.write(content)

def update_notebook_table(notebooks, md_path):
    """
    Update the Notebook_Table_Type(Serial_Parallel).md file with sorted entries.
    """
    with open(md_path, 'r', encoding='utf-8') as f:
        content = f.read()

    existing_entries = parse_table(content)
    new_entries = generate_table_rows(notebooks, existing_entries)

    # Sort into Serial and Parallel
    serial_notebooks = sorted(
        [entry for entry in new_entries if 'Serial' in entry['type']],
        key=lambda x: x['notebook'].lower()
    )
    parallel_notebooks = sorted(
        [entry for entry in new_entries if 'Parallel' in entry['type']],
        key=lambda x: x['notebook'].lower()
    )

    def format_section(title, notebooks):
        rows = "\n".join(
            f"| {entry['project']} | [{entry['notebook']}](./{entry['project']}/{entry['notebook']}) | {entry['type']} | {entry['modules']} |"
            for entry in notebooks
        )
        return f"### {title} Notebooks\n\n| Notebook Project | Notebook | Type | Required (Sub) Modules |\n|-----------------|----------|------|------------------------|\n{rows}\n"

    updated_content = (
        "## Expanse-Notebooks-dev: Notebook Table Sorted by Type (Serial/Parallel)\n\n"
        + format_section("Serial", serial_notebooks)
        + "\n"
        + format_section("Parallel", parallel_notebooks)
    )

    with open(md_path, 'w', encoding='utf-8') as f:
        f.write(updated_content)

if __name__ == '__main__':
    root_dir = '.'  # Specify root directory of notebooks
    readme_path = 'README.md'
    table_md_path = 'Notebook_Table_Type(Serial\Parallel).md'

    notebooks = []
    for dirpath, _, filenames in os.walk(root_dir):
        for filename in filenames:
            if filename.endswith('.ipynb'):
                project = os.path.basename(dirpath)
                notebooks.append((project, os.path.join(dirpath, filename)))

    # Update both README.md and Notebook_Table_Type(Serial_Parallel).md
    update_readme(notebooks, readme_path)
    update_notebook_table(notebooks, table_md_path)

