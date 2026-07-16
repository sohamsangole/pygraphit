from dataclasses import dataclass

@dataclass
class Edge:
    source_id: str
    relation: str
    target_id: str
