import sqlite3
from typing import List, Tuple, Dict, Any, Optional

class SQLiteStorage:
    def __init__(self, db_path: str = "pygraph.db"):
        self.db_path = db_path
        self.conn = sqlite3.connect(db_path)
        self._create_tables()

    def _create_tables(self):
        cursor = self.conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS Files (
                path TEXT PRIMARY KEY,
                content TEXT
            )
        ''')
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS Nodes (
                id TEXT PRIMARY KEY,
                type TEXT,
                name TEXT,
                file TEXT,
                start_line INTEGER,
                end_line INTEGER
            )
        ''')
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS Edges (
                source_id TEXT,
                relation TEXT,
                target_id TEXT
            )
        ''')
        # Create indexes for faster lookups
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_node_name ON Nodes(name)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_edge_source ON Edges(source_id)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_edge_target ON Edges(target_id)')
        self.conn.commit()

    def add_file(self, path: str, content: str):
        cursor = self.conn.cursor()
        cursor.execute('INSERT OR REPLACE INTO Files (path, content) VALUES (?, ?)', (path, content))
        self.conn.commit()

    def add_node(self, node_id: str, type: str, name: str, file: str, start_line: Optional[int], end_line: Optional[int]):
        cursor = self.conn.cursor()
        cursor.execute('''
            INSERT OR REPLACE INTO Nodes (id, type, name, file, start_line, end_line)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (node_id, type, name, file, start_line, end_line))
        self.conn.commit()

    def add_edge(self, source_id: str, relation: str, target_id: str):
        cursor = self.conn.cursor()
        cursor.execute('''
            INSERT INTO Edges (source_id, relation, target_id)
            VALUES (?, ?, ?)
        ''', (source_id, relation, target_id))
        self.conn.commit()

    def get_node(self, node_id: str):
        cursor = self.conn.cursor()
        cursor.execute('SELECT * FROM Nodes WHERE id = ? OR name = ?', (node_id, node_id))
        return cursor.fetchone()

    def get_file_content(self, path: str):
        cursor = self.conn.cursor()
        cursor.execute('SELECT content FROM Files WHERE path = ?', (path,))
        row = cursor.fetchone()
        return row[0] if row else None

    def get_edges_from(self, source_id: str):
        cursor = self.conn.cursor()
        cursor.execute('SELECT relation, target_id FROM Edges WHERE source_id = ?', (source_id,))
        return cursor.fetchall()
        
    def get_edges_to(self, target_id: str):
        cursor = self.conn.cursor()
        cursor.execute('SELECT source_id, relation FROM Edges WHERE target_id = ?', (target_id,))
        return cursor.fetchall()
