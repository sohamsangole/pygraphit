from pygraphit.storage.sqlite import SQLiteStorage

class Ranking:
    def __init__(self, storage: SQLiteStorage):
        self.storage = storage
        
    def rank_nodes(self, node_ids, query):
        scored_nodes = []
        for n_id in node_ids:
            node = self.storage.get_node(n_id)
            if not node:
                continue
            id_, type_, name, file_, start, end = node
            score = 0
            if name == query:
                score += 10
            if type_ in ("Class", "Function", "Method"):
                score += 5
            scored_nodes.append((score, node))
            
        scored_nodes.sort(key=lambda x: x[0], reverse=True)
        return [node for score, node in scored_nodes]

    def extract_code_chunks(self, nodes):
        chunks = []
        for node in nodes:
            id_, type_, name, file_, start_line, end_line = node
            content = self.storage.get_file_content(file_)
            if content and start_line is not None and end_line is not None:
                lines = content.splitlines()
                start = max(0, start_line - 1)
                end = min(len(lines), end_line)
                chunk = "\n".join(lines[start:end])
                chunks.append({
                    "node_id": id_,
                    "type": type_,
                    "name": name,
                    "file": file_,
                    "code": chunk
                })
        return chunks
