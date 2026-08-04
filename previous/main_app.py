import math
import tkinter as tk
from tkinter import ttk, messagebox

# Import logic from Person 1 and Person 2
from graph_logic import Graph
from map_loader import load_graph_from_json

class CampusMapApp:
    def __init__(self, root, graph, all_edges):
        self.root = root
        self.root.title("Campus Navigation Planner")
        self.root.geometry("850x650")
        
        self.graph = graph
        self.all_edges = all_edges
        
        # Track selection state
        self.click_step = 0  # 0: next click sets start, 1: next click sets end
        
        # --- UI CONTROL PANEL (TOP) ---
        control_frame = tk.Frame(self.root, bg="#f0f0f0", padx=10, pady=10)
        control_frame.pack(fill=tk.X, side=tk.TOP)
        
        node_list = sorted(list(self.graph.adj_list.keys()))
        
        tk.Label(control_frame, text="Start:", bg="#f0f0f0").grid(row=0, column=0, padx=5)
        self.start_var = tk.StringVar()
        self.start_combo = ttk.Combobox(control_frame, textvariable=self.start_var, values=node_list, state="readonly", width=15)
        self.start_combo.grid(row=0, column=1, padx=5)
        self.start_combo.set(node_list[0])
        
        tk.Label(control_frame, text="End:", bg="#f0f0f0").grid(row=0, column=2, padx=5)
        self.end_var = tk.StringVar()
        self.end_combo = ttk.Combobox(control_frame, textvariable=self.end_var, values=node_list, state="readonly", width=15)
        self.end_combo.grid(row=0, column=3, padx=5)
        self.end_combo.set(node_list[-1])
        
        find_btn = tk.Button(control_frame, text="Find Route", bg="#4CAF50", fg="white", font=("Arial", 9, "bold"), command=self.find_and_draw_route)
        find_btn.grid(row=0, column=4, padx=10)
        
        self.result_label = tk.Label(control_frame, text="Select points via dropdown or click nodes directly on the map.", bg="#f0f0f0", font=("Arial", 10, "bold"))
        self.result_label.grid(row=1, column=0, columnspan=5, pady=5)

        # --- CANVAS MAP DISPLAY (BOTTOM) ---
        self.canvas = tk.Canvas(self.root, bg="white")
        self.canvas.pack(fill=tk.BOTH, expand=True)

        # Bind mouse click event for interactive node selection
        self.canvas.bind("<Button-1>", self.on_canvas_click)

        self.draw_base_map()

    def draw_base_map(self):
        """Draws all default roads and location nodes onto the canvas."""
        self.canvas.delete("all")
        
        # Draw all roads (edges)
        for edge in self.all_edges:
            u, v = edge["u"], edge["v"]
            if u in self.graph.coordinates and v in self.graph.coordinates:
                x1, y1 = self.graph.coordinates[u]
                x2, y2 = self.graph.coordinates[v]
                self.canvas.create_line(x1, y1, x2, y2, fill="#d3d3d3", width=3)
                
                # Draw edge weight (distance) label
                mid_x, mid_y = (x1 + x2) / 2, (y1 + y2) / 2
                self.canvas.create_text(mid_x, mid_y, text=f"{edge['weight']}m", fill="#888888", font=("Arial", 8))

        # Draw all locations (nodes)
        for node_id, (x, y) in self.graph.coordinates.items():
            r = 15  # Circle radius
            self.canvas.create_oval(x-r, y-r, x+r, y+r, fill="#2196F3", outline="#0b7dda", width=2)
            self.canvas.create_text(x, y-22, text=node_id, font=("Arial", 10, "bold"), fill="#333333")

    def on_canvas_click(self, event):
        """Allows selecting Start and End nodes by clicking on the canvas."""
        clicked_node = None
        radius = 15
        
        # Find if a node circle was clicked
        for node_id, (nx, ny) in self.graph.coordinates.items():
            dist = math.hypot(event.x - nx, event.y - ny)
            if dist <= radius:
                clicked_node = node_id
                break
                
        if clicked_node:
            if self.click_step == 0:
                self.start_combo.set(clicked_node)
                self.click_step = 1
                self.result_label.config(text=f"Start: '{clicked_node}'. Now click an End node.", fg="#1976D2")
            else:
                self.end_combo.set(clicked_node)
                self.click_step = 0
                self.find_and_draw_route()

    def find_and_draw_route(self):
        """Calculates shortest path using Person 1's code and highlights it."""
        start = self.start_var.get()
        end = self.end_var.get()
        
        if start == end:
            messagebox.showwarning("Invalid Selection", "Start and End locations must be different!")
            return
            
        # Reset map canvas
        self.draw_base_map()
        
        # Call Person 1's Dijkstra algorithm
        dist, path = self.graph.dijkstra(start, end)
        
        if dist == float('inf') or not path:
            self.result_label.config(text="No path exists between selected points!", fg="red")
            return

        self.result_label.config(text=f"Shortest Distance: {dist} meters | Route: {' -> '.join(path)}", fg="#2e7d32")

        # Highlight path edges in RED
        for i in range(len(path) - 1):
            u, v = path[i], path[i+1]
            x1, y1 = self.graph.coordinates[u]
            x2, y2 = self.graph.coordinates[v]
            self.canvas.create_line(x1, y1, x2, y2, fill="#e53935", width=5)

        # Highlight start (Green) and end (Orange) nodes
        sx, sy = self.graph.coordinates[start]
        ex, ey = self.graph.coordinates[end]
        r = 15
        self.canvas.create_oval(sx-r, sy-r, sx+r, sy+r, fill="#4CAF50", outline="black", width=2)
        self.canvas.create_oval(ex-r, ey-r, ex+r, ey+r, fill="#FF9800", outline="black", width=2)


if __name__ == "__main__":
    root = tk.Tk()
    
    # Initialize Graph
    campus_graph = Graph()
    
    # Person 2's loader populates the graph from JSON
    edges_data = load_graph_from_json("map_data.json", campus_graph)
    
    # Person 3's UI runs the desktop window
    app = CampusMapApp(root, campus_graph, edges_data)
    root.mainloop()