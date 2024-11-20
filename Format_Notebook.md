
## Required Header Format

Each notebook must include a YAML front matter at the beginning of the notebook in the first markdown cell. The format should be:

```
---
type: [CPU/GPU Type], [Serial/Parallel Type]
required_modules:
  - module1
  - module2
  - module3
---
```

### Type Specification Guidelines

#### CPU/GPU Type Options:
- `CPU`: For notebooks that run on CPU only
- `GPU`: For notebooks that require GPU
- `CPU, GPU`: For notebooks that can run on both CPU and GPU

#### Serial/Parallel Type Options:
- `Serial`: For notebooks that run serially
- `Parallel`: For notebooks that use parallel processing

### Examples:

Valid type specifications:
```yaml
type: CPU, Serial
type: GPU, Parallel
type: CPU GPU, Parallel
```

### Required Modules Section

The `required_modules` section should list all Python packages needed to run the notebook:

```yaml
required_modules:
  - numpy
  - pandas
  - scipy
  - matplotlib
  - torch  # for deep learning notebooks
  - tensorflow  # specify version if needed
```

## Important Notes

1. **Header Location**: The YAML front matter must be in the **first markdown cell** of the notebook.

2. **Updating Requirements**:
   - When adding new package dependencies, update the `required_modules` list
   - When changing computation methods, update the type specification
   - 
4. **Automatic Table Updates**:
   The repository maintains three automatically generated tables:
   - Main README table (alphabetically sorted)
   - Serial/Parallel classification table
   - CPU/GPU classification table

## Example of a Complete Header

```
---
type: CPU GPU, Parallel
required_modules:
  - numpy>=1.20.0
  - pandas>=1.3.0
  - matplotlib>=3.4.0
  - scipy>=1.7.0
  - scikit-learn>=0.24.0
---
```
