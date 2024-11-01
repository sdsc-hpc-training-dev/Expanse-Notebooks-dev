import os

# Define the path to the README file
readme_path = "README.md"

# Define the table header
table_header = """## Notebook Table: Alphabetical Order
| Notebook Project               | Notebook                                                                                   | Type               | Required (Sub) Modules                   |
|--------------------------------|--------------------------------------------------------------------------------------------|--------------------|------------------------------------------|"""

# Define the beginning and end of the file sections where the table will be inserted
intro_section = """# Expanse-Notebooks-dev

Refer to this [guide](./Expanse_Notebook_User_Guide.md) for instructions on loading required packages and launching Jupyter Notebook in Expanse.

## View by: Name (Alphabetical-Order)

The following table lists the notebooks in alphabetical order. To view by type, use the links below:

- [CPU/GPU](./Notebook_Table_Type(CPU\\GPU).md)
- [Serial/Parallel](./Notebook_Table_Type(Serial\\Parallel).md)
"""

# Template for a row entry
table_row_template = "| {name:<30} | [{title}](./{path}) | {type:<15} | {modules:<40} |"

def get_notebook_info():
    # Mock data - replace this with actual logic to extract notebook details
    notebooks = [
        {
            "name": "CUDA_GPU_Computing_Pi",
            "title": "cuda_gpu_nvidia_computing_pi_solution.ipynb",
            "path": "CUDA_GPU_Computing_Pi/cuda_gpu_nvidia_computing_pi_solution.ipynb",
            "type": "GPU, Parallel",
            "modules": "`numba`, `math`, `numpy`, `cuda`"
        },
        # Add other notebooks here or add code to dynamically find them
    ]
    return sorted(notebooks, key=lambda x: x["name"])  # Sort notebooks alphabetically by name

def update_readme():
    notebook_entries = get_notebook_info()

    # Generate table rows for each notebook
    table_rows = "\n".join(
        table_row_template.format(
            name=nb["name"],
            title=nb["title"],
            path=nb["path"],
            type=nb["type"],
            modules=nb["modules"]
        )
        for nb in notebook_entries
    )

    # Combine all sections
    readme_content = f"{intro_section}\n\n{table_header}\n{table_rows}\n"
    
    # Write the new README content
    with open(readme_path, "w") as readme_file:
        readme_file.write(readme_content)

# Run the script
if __name__ == "__main__":
    update_readme()

