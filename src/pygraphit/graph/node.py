from dataclasses import dataclass
from typing import Optional

@dataclass
class Node:
    id: str
    type: str
    name: str
    file: str
    start_line: Optional[int]
    end_line: Optional[int]
