def update_cpu_gpu_table(notebooks, md_path):
    """
    Update the Notebook_Table_Type(CPU_GPU).md file with entries sorted by CPU/GPU type.
    """
    print(f"Updating CPU/GPU table at: {md_path}")

    try:
        # Read existing content or create if doesn't exist
        try:
            with open(md_path, 'r', encoding='utf-8') as f:
                content = f.read()
        except FileNotFoundError:
            content = "## Expanse-Notebooks-dev: Notebook Table Sorted by Type (CPU/GPU)\n\n"
            print(f"Creating new file: {md_path}")

        new_entries = generate_table_rows(notebooks, [])

        # Create categories for different types of notebooks
        cpu_notebooks = []
        gpu_notebooks = []
        hybrid_notebooks = []  # For notebooks that can use both CPU and GPU

        # Categorize notebooks based on their type
        for entry in new_entries:
            notebook_type = entry['type'].lower()
            if 'cpu, gpu' in notebook_type or 'gpu, cpu' in notebook_type:
                hybrid_notebooks.append(entry)
            elif 'gpu' in notebook_type:
                gpu_notebooks.append(entry)
            elif 'cpu' in notebook_type or 'serial' in notebook_type:  # Assume serial implies CPU
                cpu_notebooks.append(entry)
            else:
                cpu_notebooks.append(entry)  # Default to CPU if not specified

        # Sort each category alphabetically by notebook name
        cpu_notebooks.sort(key=lambda x: x['notebook'].lower())
        gpu_notebooks.sort(key=lambda x: x['notebook'].lower())
        hybrid_notebooks.sort(key=lambda x: x['notebook'].lower())

        def format_section(title, notebooks):
            if not notebooks:
                return ""
            
            table_header = "| Notebook Project | Notebook | Type | Required (Sub) Modules |\n|-----------------|----------|------|------------------------|\n"
            rows = "\n".join(
                f"| {entry['project']} | [{entry['notebook']}](./{entry['project']}/{entry['notebook']}) | {entry['type']} | {entry['modules']} |"
                for entry in notebooks
            )
            return f"### {title}\n\n{table_header}{rows}\n"

        # Build the content
        updated_content = [
            "## Expanse-Notebooks-dev: Notebook Table Sorted by Type (CPU/GPU)\n"
        ]
        
        if cpu_notebooks:
            updated_content.append(format_section("CPU Notebooks", cpu_notebooks))
        if gpu_notebooks:
            updated_content.append(format_section("GPU Notebooks", gpu_notebooks))
        if hybrid_notebooks:
            updated_content.append(format_section("Hybrid (CPU/GPU) Notebooks", hybrid_notebooks))

        final_content = "\n".join(filter(None, updated_content))

        # Write the updated content
        with open(md_path, 'w', encoding='utf-8') as f:
            f.write(final_content)
        
        print(f"Successfully updated {md_path}")

    except Exception as e:
        print(f"Error updating CPU/GPU table: {str(e)}")
        raise

if __name__ == '__main__':
    root_dir = '.'
    readme_path = 'README.md'
    serial_parallel_path = 'Notebook_Table_Type(Serial_Parallel).md'
    cpu_gpu_path = 'Notebook_Table_Type(CPU_GPU).md'

    notebooks = []
    print("Scanning for notebooks...")
    for dirpath, _, filenames in os.walk(root_dir):
        for filename in filenames:
            if filename.endswith('.ipynb'):
                project = os.path.basename(dirpath)
                notebook_path = os.path.join(dirpath, filename)
                print(f"Found notebook: {notebook_path}")
                notebooks.append((project, notebook_path))

    print(f"Found {len(notebooks)} notebooks")

    # Update all three files
    update_readme(notebooks, readme_path)
    update_notebook_table(notebooks, serial_parallel_path)
    update_cpu_gpu_table(notebooks, cpu_gpu_path)
