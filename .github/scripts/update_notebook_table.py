# Save this as .github/workflows/update_type_table.yml
name: Update Notebook Type Table

on:
  push:
    paths:
      - '**/*.ipynb'
    branches:
      - main  # or your default branch name

jobs:
  update-table:
    runs-on: ubuntu-latest
    
    steps:
    - uses: actions/checkout@v3
      with:
        fetch-depth: 0  # Fetch all history for proper tracking
    
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.x'
    
    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install pyyaml
    
    - name: List changed files
      run: |
        echo "Changed files:"
        git diff --name-only ${{ github.event.before }} ${{ github.sha }}
    
    - name: Update notebook table
      run: |
        echo "Starting notebook table update..."
        python update_notebook_table.py
        echo "Finished updating table"
    
    - name: Check for changes
      id: check_changes
      run: |
        if [[ -n "$(git status --porcelain)" ]]; then
          echo "Changes detected"
          echo "has_changes=true" >> $GITHUB_OUTPUT
        else
          echo "No changes detected"
          echo "has_changes=false" >> $GITHUB_OUTPUT
        fi
    
    - name: Commit changes
      if: steps.check_changes.outputs.has_changes == 'true'
      run: |
        git config --local user.email "github-actions[bot]@users.noreply.github.com"
        git config --local user.name "github-actions[bot]"
        git add Notebook_Table_Type(Serial_Parallel).md
        git commit -m "Update notebook table [skip ci]"
        echo "Changes committed"
    
    - name: Push changes
      if: steps.check_changes.outputs.has_changes == 'true'
      uses: ad-m/github-push-action@master
      with:
        github_token: ${{ secrets.GITHUB_TOKEN }}
        branch: ${{ github.ref }}
