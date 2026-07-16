import sqlite3
import json
import argparse
import os
import math

def main():
    parser = argparse.ArgumentParser(description="Visualize PyGraph")
    parser.add_argument("--db", default="pygraph.db", help="Path to SQLite database")
    parser.add_argument("--out", default="graph_view.html", help="Output HTML file")

    args = parser.parse_args()

    if not os.path.exists(args.db):
        print(f"Error: Database {args.db} not found.")
        return

    conn = sqlite3.connect(args.db)
    cursor = conn.cursor()

    # Fetch all nodes
    cursor.execute("SELECT id, type, name FROM Nodes")
    nodes_raw = cursor.fetchall()

    # Fetch all edges
    cursor.execute("SELECT source_id, relation, target_id FROM Edges")
    edges_raw = cursor.fetchall()
    
    conn.close()

    # Calculate degrees for sizing (hub nodes should be larger)
    degrees = {}
    for source, relation, target in edges_raw:
        degrees[source] = degrees.get(source, 0) + 1
        degrees[target] = degrees.get(target, 0) + 1

    type_colors = {
        "Module": "#ff5252",
        "Class": "#ffb142",
        "Function": "#33d9b2",
        "Method": "#34ace0",
        "Variable": "#a55eea"
    }

    vis_nodes = []
    for row in nodes_raw:
        node_id, node_type, name = row
        degree = degrees.get(node_id, 0)
        # Organic size scaling: base size 10, grows with connections
        size = 10 + min(math.sqrt(degree) * 4, 40)
        
        vis_nodes.append({
            "id": node_id,
            "label": name,
            "title": f"Type: {node_type}<br>ID: {node_id}<br>Connections: {degree}",
            "color": type_colors.get(node_type, "#d1ccc0"),
            "shape": "dot",
            "size": size,
            "font": {"color": "#e0e0e0", "size": 12, "face": "Helvetica"}
        })

    vis_edges = []
    for row in edges_raw:
        source, relation, target = row
        vis_edges.append({
            "from": source,
            "to": target,
            "label": relation,
            "font": {"align": "middle", "color": "#888888", "size": 9},
            "color": {"color": "#444444", "highlight": "#888888"},
            "arrows": {"to": {"enabled": True, "scaleFactor": 0.5}}
        })

    nodes_json = json.dumps(vis_nodes)
    edges_json = json.dumps(vis_edges)

    html_content = f"""<!DOCTYPE html>
<html>
<head>
    <title>PyGraph View</title>
    <script type="text/javascript" src="https://unpkg.com/vis-network/standalone/umd/vis-network.min.js"></script>
    <style type="text/css">
        body {{
            background-color: #1e1e1e;
            margin: 0;
            padding: 0;
            overflow: hidden;
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
        }}
        #mynetwork {{
            width: 100vw;
            height: 100vh;
        }}
        #title {{
            position: absolute;
            top: 20px;
            left: 20px;
            color: #ffffff;
            z-index: 10;
            pointer-events: none;
            opacity: 0.8;
        }}
        .legend {{
            position: absolute;
            bottom: 20px;
            left: 20px;
            background: rgba(30, 30, 30, 0.8);
            padding: 10px;
            border-radius: 8px;
            border: 1px solid #444;
            color: #ccc;
            z-index: 10;
            font-size: 14px;
        }}
        .legend-item {{
            display: flex;
            align-items: center;
            margin-bottom: 5px;
        }}
        .color-box {{
            width: 15px;
            height: 15px;
            border-radius: 50%;
            margin-right: 10px;
        }}
    </style>
</head>
<body>
    <h2 id="title">PyGraph Knowledge Graph</h2>
    
    <div class="legend">
        <div class="legend-item"><div class="color-box" style="background: #ff5252"></div> Module</div>
        <div class="legend-item"><div class="color-box" style="background: #ffb142"></div> Class</div>
        <div class="legend-item"><div class="color-box" style="background: #33d9b2"></div> Function</div>
        <div class="legend-item"><div class="color-box" style="background: #34ace0"></div> Method</div>
        <div class="legend-item"><div class="color-box" style="background: #a55eea"></div> Variable</div>
    </div>

    <div id="mynetwork"></div>

    <script type="text/javascript">
        var nodes = new vis.DataSet({nodes_json});
        var edges = new vis.DataSet({edges_json});

        var container = document.getElementById('mynetwork');
        var data = {{
            nodes: nodes,
            edges: edges
        }};
        var options = {{
            nodes: {{
                borderWidth: 1,
                borderWidthSelected: 3,
                color: {{
                    border: '#111111',
                    highlight: {{
                        border: '#ffffff',
                        background: '#ffffff'
                    }}
                }}
            }},
            edges: {{
                smooth: false, // Straight lines look more organic in huge cluster graphs
                width: 1,
                hoverWidth: 2,
                selectionWidth: 2
            }},
            physics: {{
                solver: 'barnesHut',
                barnesHut: {{
                    gravitationalConstant: -3000, // Stronger repulsion for spacing
                    centralGravity: 0.1, // Keeps the graph centered
                    springLength: 100, // Organic edge lengths
                    springConstant: 0.02, // Loose springs for a more floaty feel
                    damping: 0.09,
                    avoidOverlap: 0
                }},
                maxVelocity: 50,
                minVelocity: 0.1,
                stabilization: {{ 
                    enabled: true,
                    iterations: 150, // Let the physics play out quickly
                    updateInterval: 25
                }}
            }},
            interaction: {{
                hover: true,
                tooltipDelay: 100,
                hideEdgesOnDrag: false // Keep edges visible to feel more fluid
            }}
        }};
        var network = new vis.Network(container, data, options);
    </script>
</body>
</html>
"""

    with open(args.out, "w", encoding="utf-8") as f:
        f.write(html_content)
    
    print(f"Graph visualization saved to {args.out}")
    print(f"Open this file in your web browser to explore the graph!")

if __name__ == "__main__":
    main()
