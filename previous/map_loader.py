import json

def load_graph_from_json(json_filepath, graph_obj):
    """
    Reads a JSON file containing nodes and edges, 
    and populates the provided Graph object.
    """
    with open(json_filepath, 'r') as file:
        data = json.load(file)

    # Load Nodes
    for node in data.get("nodes", []):
        graph_obj.add_node(node["id"], x=node["x"], y=node["y"])

    # Load Edges (skipping closed roads)
    for edge in data.get("edges", []):
        if not edge.get("closed", False):  # Edge Case: Closed roads are ignored
            graph_obj.add_edge(edge["u"], edge["v"], weight=edge["weight"])

    return data["edges"]  # Return raw edges so UI can draw all roads