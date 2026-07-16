import ast
import os
from .visitors import GraphVisitor
from pygraphit.storage.sqlite import SQLiteStorage

class ProjectParser:
    def __init__(self, root_dir: str, storage: SQLiteStorage):
        self.root_dir = root_dir
        self.storage = storage

    def parse_all(self):
        ignore_dirs = {'.git', 'venv', 'env', '.env', 'node_modules', '__pycache__', '.pytest_cache'}
        for root, dirs, files in os.walk(self.root_dir):
            dirs[:] = [d for d in dirs if d not in ignore_dirs]
            for file in files:
                if file.endswith('.py'):
                    file_path = os.path.join(root, file)
                    self.parse_file(file_path)

    def parse_file(self, file_path: str):
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
        except Exception as e:
            print(f"Failed to read {file_path}: {e}")
            return

        # Store file content
        self.storage.add_file(file_path, content)

        try:
            tree = ast.parse(content, filename=file_path)
        except SyntaxError as e:
            print(f"Syntax error in {file_path}: {e}")
            return

        # Add Module node
        self.storage.add_node(
            node_id=file_path,
            type="Module",
            name=os.path.basename(file_path),
            file=file_path,
            start_line=1,
            end_line=len(content.splitlines())
        )

        visitor = GraphVisitor(file_path)
        visitor.visit(tree)

        for node in visitor.nodes:
            self.storage.add_node(
                node.id, node.type, node.name, node.file, node.start_line, node.end_line
            )

        for edge in visitor.edges:
            self.storage.add_edge(
                edge.source_id, edge.relation, edge.target_id
            )
