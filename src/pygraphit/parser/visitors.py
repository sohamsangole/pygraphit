import ast
from pygraphit.graph.node import Node
from pygraphit.graph.edge import Edge

class GraphVisitor(ast.NodeVisitor):
    def __init__(self, file_path: str):
        self.file_path = file_path
        self.nodes = []
        self.edges = []
        self.scope_stack = []

    def current_parent(self):
        return self.scope_stack[-1] if self.scope_stack else None

    def make_id(self, name):
        parent = self.current_parent()
        if parent:
            return f"{parent}.{name}"
        return f"{self.file_path}:{name}"

    def add_node(self, node_id, node_type, name, start_line, end_line):
        self.nodes.append(Node(
            id=node_id,
            type=node_type,
            name=name,
            file=self.file_path,
            start_line=start_line,
            end_line=end_line
        ))

    def add_edge(self, source, relation, target):
        self.edges.append(Edge(
            source_id=source,
            relation=relation,
            target_id=target
        ))

    def visit_Import(self, node):
        for alias in node.names:
            target_name = alias.name
            self.add_edge(self.file_path, "IMPORTS", target_name)
        self.generic_visit(node)

    def visit_ImportFrom(self, node):
        if node.module:
            self.add_edge(self.file_path, "IMPORTS", node.module)
        self.generic_visit(node)

    def visit_ClassDef(self, node):
        class_id = self.make_id(node.name)
        self.add_node(class_id, "Class", node.name, node.lineno, getattr(node, 'end_lineno', node.lineno))
        
        parent = self.current_parent()
        if parent:
            self.add_edge(class_id, "BELONGS_TO", parent)
        else:
            self.add_edge(class_id, "BELONGS_TO", self.file_path)

        for base in node.bases:
            if isinstance(base, ast.Name):
                self.add_edge(class_id, "INHERITS", base.id)
            elif isinstance(base, ast.Attribute):
                self.add_edge(class_id, "INHERITS", base.attr)
                
        self.scope_stack.append(class_id)
        self.generic_visit(node)
        self.scope_stack.pop()

    def visit_FunctionDef(self, node):
        parent = self.current_parent()
        node_type = "Method" if parent else "Function"
        func_id = self.make_id(node.name)
        
        self.add_node(func_id, node_type, node.name, node.lineno, getattr(node, 'end_lineno', node.lineno))
        
        if parent:
            self.add_edge(func_id, "BELONGS_TO", parent)
        else:
            self.add_edge(func_id, "BELONGS_TO", self.file_path)

        self.scope_stack.append(func_id)
        self.generic_visit(node)
        self.scope_stack.pop()

    def visit_Call(self, node):
        caller = self.current_parent()
        if caller:
            if isinstance(node.func, ast.Name):
                self.add_edge(caller, "CALLS", node.func.id)
            elif isinstance(node.func, ast.Attribute):
                self.add_edge(caller, "CALLS", node.func.attr)
        self.generic_visit(node)

    def visit_Assign(self, node):
        parent = self.current_parent()
        for target in node.targets:
            if isinstance(target, ast.Name):
                var_name = target.id
                var_id = self.make_id(var_name)
                self.add_node(var_id, "Variable", var_name, node.lineno, getattr(node, 'end_lineno', node.lineno))
                
                if parent:
                    self.add_edge(parent, "DEFINES", var_id)
                else:
                    self.add_edge(self.file_path, "DEFINES", var_id)
        self.generic_visit(node)

    def visit_Name(self, node):
        if isinstance(node.ctx, ast.Load):
            parent = self.current_parent()
            if parent:
                self.add_edge(parent, "USES", node.id)
        self.generic_visit(node)
