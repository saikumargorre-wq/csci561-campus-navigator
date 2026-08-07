import math
import tkinter as tk
from tkinter import ttk, messagebox

from graph_logic import Graph, calculate_walk_time
from map_loader import load_graph_from_json

class CampusMapApp:
    def __init__(self, root, graph, all_edges):
        self.root = root
        self.root.title("Campus Navigation Planner")
        self.root.geometry("1000x720")
        self.root.configure(bg="#eef3f7")
        
        self.graph = graph
        self.all_edges = all_edges
        self.click_step = 0
        
        # --- UI CONTROL PANEL (TOP) ---
        control_frame = tk.Frame(self.root, bg="#f5f7fa", padx=12, pady=10, relief=tk.GROOVE, bd=1)
        control_frame.pack(fill=tk.X, side=tk.TOP, padx=10, pady=8)
        
        node_list = sorted(list(self.graph.adj_list.keys()))

        # UI Title
        tk.Label(control_frame, text="Campus Navigation Planner", bg="#f5f7fa", fg="#1565C0", font=("Arial", 14, "bold")).grid(row=0, column=0, columnspan=8, sticky="w", pady=(0, 8))
        
        # 1. Start Dropdown
        tk.Label(control_frame, text="Start:", bg="#f5f7fa", font=("Arial", 9, "bold")).grid(row=1, column=0, padx=3)
        self.start_var = tk.StringVar()
        self.start_combo = ttk.Combobox(control_frame, textvariable=self.start_var, values=node_list, state="readonly", width=15)
        self.start_combo.grid(row=1, column=1, padx=3)
        if node_list:
            self.start_combo.set(node_list[0])
        
        # 2. Middle Stop (Via) Dropdown
        tk.Label(control_frame, text="Via (Optional):", bg="#f5f7fa", font=("Arial", 9, "bold")).grid(row=1, column=2, padx=3)
        self.via_var = tk.StringVar()
        via_options = ["None"] + node_list  # Allows user to skip middle stop
        self.via_combo = ttk.Combobox(control_frame, textvariable=self.via_var, values=via_options, state="readonly", width=15)
        self.via_combo.grid(row=1, column=3, padx=3)
        self.via_combo.set("None")

        # 3. End Dropdown
        tk.Label(control_frame, text="End:", bg="#f5f7fa", font=("Arial", 9, "bold")).grid(row=1, column=4, padx=3)
        self.end_var = tk.StringVar()
        self.end_combo = ttk.Combobox(control_frame, textvariable=self.end_var, values=node_list, state="readonly", width=15)
        self.end_combo.grid(row=1, column=5, padx=3)
        if node_list:
            self.end_combo.set(node_list[-1])
        
        # Buttons
        find_btn = tk.Button(control_frame, text="Find Route", bg="#2E7D32", fg="white", activebackground="#1B5E20", activeforeground="white", font=("Arial", 9, "bold"), relief=tk.FLAT, padx=8, pady=4, command=self.find_and_draw_route)
        find_btn.grid(row=1, column=6, padx=5)
        
        reset_btn = tk.Button(control_frame, text="Reset", bg="#616161", fg="white", activebackground="#424242", activeforeground="white", font=("Arial", 9, "bold"), relief=tk.FLAT, padx=8, pady=4, command=self.reset_map)
        reset_btn.grid(row=1, column=7, padx=5)
        
        # Status Message Label
        self.result_label = tk.Label(control_frame, text="Select points via dropdown or click nodes directly on the map.", bg="white", fg="#37474F", font=("Arial", 10, "bold"), justify=tk.LEFT, anchor="w", relief=tk.GROOVE, bd=1, padx=6, pady=5)
        self.result_label.grid(row=2, column=0, columnspan=8, sticky="ew", pady=(8, 0))

        # --- CANVAS MAP DISPLAY ---
        self.canvas = tk.Canvas(self.root, bg="white", highlightbackground="#c7d0d9", highlightthickness=1)
        self.canvas.pack(fill=tk.BOTH, expand=True, padx=10, pady=(0, 8))
        self.canvas.bind("<Button-1>", self.on_canvas_click)

        self.draw_base_map()

    def draw_base_map(self):
        """Draws basic map elements."""
        self.canvas.delete("all")
        
        # Draw edges
        for edge in self.all_edges:
            u, v = edge["u"], edge["v"]
            if u in self.graph.coordinates and v in self.graph.coordinates:
                x1, y1 = self.graph.coordinates[u]
                x2, y2 = self.graph.coordinates[v]
                mid_x, mid_y = (x1 + x2) / 2, (y1 + y2) / 2
                
                if edge.get("closed", False):
                    self.canvas.create_line(x1, y1, x2, y2, fill="#ef5350", width=2, dash=(4, 4))
                    self.canvas.create_oval(mid_x-10, mid_y-10, mid_x+10, mid_y+10, fill="#FFA000", outline="white")
                    self.canvas.create_text(mid_x, mid_y, text="!", fill="white", font=("Arial", 9, "bold"))
                    detour_msg = edge.get("detour_info", "Road Closed")
                    self.canvas.create_text(mid_x, mid_y + 15, text=detour_msg, fill="#d32f2f", font=("Arial", 8, "bold"))
                else:
                    self.canvas.create_line(x1, y1, x2, y2, fill="#d3d3d3", width=3)
                    self.canvas.create_text(mid_x, mid_y, text=f"{edge['weight']}m", fill="#888888", font=("Arial", 8))

        # Draw nodes
        for node_id, (x, y) in self.graph.coordinates.items():
            r = 15
            self.canvas.create_oval(x-r, y-r, x+r, y+r, fill="#2196F3", outline="#0b7dda", width=2)
            self.canvas.create_text(x, y-22, text=node_id, font=("Arial", 10, "bold"), fill="#333333")

    def reset_map(self):
        """Resets inputs and map canvas."""
        self.click_step = 0
        self.via_combo.set("None")
        self.result_label.config(text="Select points via dropdown or click nodes directly on the map.", fg="black")
        self.draw_base_map()

    def on_canvas_click(self, event):
        """Allows selecting nodes by clicking map."""
        clicked_node = None
        radius = 15
        
        for node_id, (nx, ny) in self.graph.coordinates.items():
            if math.hypot(event.x - nx, event.y - ny) <= radius:
                clicked_node = node_id
                break
                
        if clicked_node:
            if self.click_step == 0:
                self.start_combo.set(clicked_node)
                self.click_step = 1
                self.result_label.config(text=f"Start: '{clicked_node}'. Now click an End node.", fg="#1976D2")
                
                sx, sy = self.graph.coordinates[clicked_node]
                self.canvas.create_oval(sx-radius, sy-radius, sx+radius, sy+radius, fill="#4CAF50", outline="black", width=2)
            else:
                self.end_combo.set(clicked_node)
                self.click_step = 0
                self.find_and_draw_route()

    def find_and_draw_route(self):
        """Calculates multi-leg shortest path and updates canvas display."""
        start = self.start_var.get()
        via = self.via_var.get()
        end = self.end_var.get()
        
        if start == end or (via != "None" and (start == via or end == via)):
            messagebox.showwarning("Invalid Selection", "Start, Via, and End locations must be distinct!")
            return
            
        self.draw_base_map()
        
        # --- Multi-Leg Routing Logic ---
        if via != "None":
            # Leg 1: Start -> Via
            dist1, path1 = self.graph.dijkstra(start, via)
            # Leg 2: Via -> End
            dist2, path2 = self.graph.dijkstra(via, end)
            
            if dist1 == float('inf') or dist2 == float('inf') or not path1 or not path2:
                self.result_label.config(text="No valid path passing through the selected middle stop!", fg="red")
                return
                
            dist = dist1 + dist2
            path = path1 + path2[1:]  # Avoid repeating the middle stop name
        else:
            # Direct Navigation: Start -> End
            dist, path = self.graph.dijkstra(start, end)
            if dist == float('inf') or not path:
                self.result_label.config(text="No path exists between selected points!", fg="red")
                return

        # Calculate Walk Time in Minutes
        walk_mins = calculate_walk_time(dist)

        # Check Detour Warnings
        warnings = []
        path_set = set(path)
        for edge in self.all_edges:
            if edge.get("closed", False) and (edge["u"] in path_set or edge["v"] in path_set):
                status = edge.get("status", "Closed")
                info = edge.get("detour_info", "Detour active")
                warnings.append(f"⚠️ [{edge['u']} ↔ {edge['v']} ({status})]: {info}")

        # Display Total Distance + Walk Time
        result_msg = f"Total Distance: {dist} meters (~{walk_mins} min walk) | Route: {' -> '.join(path)}"
        if warnings:
            result_msg += "\n" + "\n".join(warnings)
            self.result_label.config(text=result_msg, fg="#d32f2f")
        else:
            self.result_label.config(text=result_msg, fg="#2e7d32")

        # Draw calculated route in red
        for i in range(len(path) - 1):
            u, v = path[i], path[i+1]
            x1, y1 = self.graph.coordinates[u]
            x2, y2 = self.graph.coordinates[v]
            self.canvas.create_line(x1, y1, x2, y2, fill="#e53935", width=5)

        # Highlight Start (Green), Via (Yellow), and End (Orange)
        r = 15
        sx, sy = self.graph.coordinates[start]
        ex, ey = self.graph.coordinates[end]
        self.canvas.create_oval(sx-r, sy-r, sx+r, sy+r, fill="#4CAF50", outline="black", width=2)
        self.canvas.create_oval(ex-r, ey-r, ex+r, ey+r, fill="#FF9800", outline="black", width=2)
        
        if via != "None":
            vx, vy = self.graph.coordinates[via]
            self.canvas.create_oval(vx-r, vy-r, vx+r, vy+r, fill="#FFEB3B", outline="black", width=2)


if __name__ == "__main__":
    root = tk.Tk()
    campus_graph = Graph()
    edges_data = load_graph_from_json("map_data.json", campus_graph)
    app = CampusMapApp(root, campus_graph, edges_data)
    root.mainloop()
