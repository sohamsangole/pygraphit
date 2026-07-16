# PyGraph

Turn any Python repository into a queryable knowledge graph using static analysis via Python's built-in `ast`. It instantly finds functions, classes, and variables, maps how they interact, and saves the graph and source code to a portable SQLite database.

## Quick Start

### 1. Build the Graph
Map an entire Python project to a local `.db` file:

```bash
python cli/index.py /path/to/project --db my_project.db
```

### 2. Query the Graph
Retrieve code chunks and trace dependencies for any node (e.g. `login`), traversing outwards by `--depth`:

```bash
python cli/query.py login --depth 2 --db my_project.db
```

### 3. Visualize
Generate an interactive HTML graph of the architecture:

```bash
python cli/visualize.py --db my_project.db --out graph_view.html
```
*(Open `graph_view.html` in any web browser!)*
