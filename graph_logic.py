import heapq

class Graph:
    def __init__(self):
        # Adjacency list representation: {node: [(neighbor, weight), ...]}
        self.adj_list = {}
        # Store physical/canvas coordinates for UI rendering: {node: (x, y)}
        self.coordinates = {}

    def add_node(self, node_id, x=0, y=0):
        """Adds a location (vertex) to the graph with optional UI coordinates."""
        if node_id not in self.adj_list:
            self.adj_list[node_id] = []
            self.coordinates[node_id] = (x, y)

    def add_edge(self, u, v, weight, bidirectional=True):
        """Adds a road (edge) between two nodes with a given distance/weight."""
        self.add_node(u)
        self.add_node(v)
        self.adj_list[u].append((v, weight))
        
        if bidirectional:
            self.adj_list[v].append((u, weight))

    def dijkstra(self, start_node, target_node):
        """
        Calculates the shortest path using a Min-Heap (Priority Queue).
        Returns: (total_distance, path_list)
        """
        if start_node not in self.adj_list or target_node not in self.adj_list:
            return float('inf'), []

        # Min-Heap stores tuples of: (current_distance, current_node)
        pq = [(0, start_node)]
        
        # Track shortest distance found so far to each node
        distances = {node: float('inf') for node in self.adj_list}
        distances[start_node] = 0
        
        # Track previous node to reconstruct the final path
        previous_nodes = {node: None for node in self.adj_list}

        while pq:
            current_dist, current_node = heapq.heappop(pq)

            # Reached destination early
            if current_node == target_node:
                break

            # If we found a longer path than already recorded, skip it
            if current_dist > distances[current_node]:
                continue

            for neighbor, weight in self.adj_list[current_node]:
                distance = current_dist + weight

                # If a shorter path to neighbor is found
                if distance < distances[neighbor]:
                    distances[neighbor] = distance
                    previous_nodes[neighbor] = current_node
                    heapq.heappush(pq, (distance, neighbor))

        # Reconstruct the shortest path backwards from target -> start
        path = []
        curr = target_node
        while curr is not None:
            path.append(curr)
            curr = previous_nodes[curr]
        path.reverse()

        # Handle unreachable case
        if distances[target_node] == float('inf'):
            return float('inf'), []

        return distances[target_node], path


def calculate_walk_time(distance_meters, speed_m_per_s=1.4):
    """
    Calculates walking time in minutes based on distance in meters.
    Default walking speed is 1.4 m/s (~0.71 seconds per meter).
    """
    if distance_meters == float('inf') or distance_meters == 0:
        return 0
    seconds = distance_meters / speed_m_per_s
    minutes = round(seconds / 60)
    return max(1, minutes)  # Minimum 1 minute for short distances


# ==========================================
# QUICK TEST EXAMPLE
# ==========================================
if __name__ == "__main__":
    campus_map = Graph()

    # Add Nodes (Location ID, X-coord, Y-coord)
    campus_map.add_node("Library", 100, 100)
    campus_map.add_node("Hostel", 100, 300)
    campus_map.add_node("Canteen", 300, 100)
    campus_map.add_node("Auditorium", 300, 300)
    campus_map.add_node("Lab", 500, 200)

    # Add Edges (Source, Destination, Distance in meters)
    campus_map.add_edge("Library", "Canteen", 200)
    campus_map.add_edge("Library", "Hostel", 150)
    campus_map.add_edge("Hostel", "Auditorium", 100)
    campus_map.add_edge("Canteen", "Auditorium", 80)
    campus_map.add_edge("Canteen", "Lab", 300)
    campus_map.add_edge("Auditorium", "Lab", 120)

    # Calculate Shortest Path from Library to Lab
    start = "Library"
    end = "Lab"
    total_dist, shortest_path = campus_map.dijkstra(start, end)
    walk_mins = calculate_walk_time(total_dist)

    print(f"Shortest distance from {start} to {end}: {total_dist} meters (~{walk_mins} min walk)")
    print(f"Route: {' -> '.join(shortest_path)}")