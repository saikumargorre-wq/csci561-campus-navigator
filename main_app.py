import math
import tkinter as tk
from tkinter import ttk, messagebox

from graph_logic import Graph, calculate_walk_time
from map_loader import load_graph_from_json


class CampusMapApp:
    def __init__(self, root, graph, all_edges):
        self.root = root
        self.root.title("Campus Navigation Planner")
        self.root.geometry("1000x700")
        self.root.minsize(900, 650)
        self.root.configure(bg="#EAF0F6")

        self.graph = graph
        self.all_edges = all_edges
        self.click_step = 0

        self.node_list = sorted(list(self.graph.adj_list.keys()))

        # -------------------------------
        # APPLICATION HEADER
        # -------------------------------
        header_frame = tk.Frame(
            self.root,
            bg="#1565C0",
            padx=20,
            pady=14
        )
        header_frame.pack(fill=tk.X)

        tk.Label(
            header_frame,
            text="Campus Navigation Planner",
            bg="#1565C0",
            fg="white",
            font=("Arial", 22, "bold")
        ).pack(anchor="w")

        tk.Label(
            header_frame,
            text="Find the shortest path between campus locations using Dijkstra's Algorithm",
            bg="#1565C0",
            fg="#E3F2FD",
            font=("Arial", 10)
        ).pack(anchor="w", pady=(3, 0))

        # -------------------------------
        # CONTROL PANEL
        # -------------------------------
        control_frame = tk.Frame(
            self.root,
            bg="#F7F9FC",
            padx=15,
            pady=12,
            relief=tk.RIDGE,
            bd=1
        )
        control_frame.pack(
            fill=tk.X,
            side=tk.TOP,
            padx=12,
            pady=(12, 6)
        )

        for column in range(8):
            control_frame.grid_columnconfigure(column, weight=1)

        # Start dropdown
        tk.Label(
            control_frame,
            text="Start Location",
            bg="#F7F9FC",
            fg="#263238",
            font=("Arial", 10, "bold")
        ).grid(
            row=0,
            column=0,
            columnspan=2,
            padx=5,
            sticky="w"
        )

        self.start_var = tk.StringVar()

        self.start_combo = ttk.Combobox(
            control_frame,
            textvariable=self.start_var,
            values=self.node_list,
            state="readonly",
            width=20,
            font=("Arial", 10)
        )
        self.start_combo.grid(
            row=1,
            column=0,
            columnspan=2,
            padx=5,
            pady=5,
            sticky="ew"
        )

        if self.node_list:
            self.start_combo.set(self.node_list[0])

        # Via dropdown
        tk.Label(
            control_frame,
            text="Via Location (Optional)",
            bg="#F7F9FC",
            fg="#263238",
            font=("Arial", 10, "bold")
        ).grid(
            row=0,
            column=2,
            columnspan=2,
            padx=5,
            sticky="w"
        )

        self.via_var = tk.StringVar()

        via_options = ["None"] + self.node_list

        self.via_combo = ttk.Combobox(
            control_frame,
            textvariable=self.via_var,
            values=via_options,
            state="readonly",
            width=20,
            font=("Arial", 10)
        )
        self.via_combo.grid(
            row=1,
            column=2,
            columnspan=2,
            padx=5,
            pady=5,
            sticky="ew"
        )
        self.via_combo.set("None")

        # End dropdown
        tk.Label(
            control_frame,
            text="Destination",
            bg="#F7F9FC",
            fg="#263238",
            font=("Arial", 10, "bold")
        ).grid(
            row=0,
            column=4,
            columnspan=2,
            padx=5,
            sticky="w"
        )

        self.end_var = tk.StringVar()

        self.end_combo = ttk.Combobox(
            control_frame,
            textvariable=self.end_var,
            values=self.node_list,
            state="readonly",
            width=20,
            font=("Arial", 10)
        )
        self.end_combo.grid(
            row=1,
            column=4,
            columnspan=2,
            padx=5,
            pady=5,
            sticky="ew"
        )

        if self.node_list:
            self.end_combo.set(self.node_list[-1])

        # Find route button
        find_btn = tk.Button(
            control_frame,
            text="Find Route",
            bg="#2E7D32",
            fg="white",
            activebackground="#1B5E20",
            activeforeground="white",
            font=("Arial", 10, "bold"),
            relief=tk.FLAT,
            cursor="hand2",
            padx=12,
            pady=7,
            command=self.find_and_draw_route
        )
        find_btn.grid(
            row=1,
            column=6,
            padx=7,
            pady=5,
            sticky="ew"
        )

        # Reset button
        reset_btn = tk.Button(
            control_frame,
            text="Reset",
            bg="#616161",
            fg="white",
            activebackground="#424242",
            activeforeground="white",
            font=("Arial", 10, "bold"),
            relief=tk.FLAT,
            cursor="hand2",
            padx=12,
            pady=7,
            command=self.reset_map
        )
        reset_btn.grid(
            row=1,
            column=7,
            padx=7,
            pady=5,
            sticky="ew"
        )

        # -------------------------------
        # RESULT PANEL
        # -------------------------------
        result_frame = tk.Frame(
            self.root,
            bg="white",
            relief=tk.GROOVE,
            bd=1,
            padx=12,
            pady=9
        )
        result_frame.pack(
            fill=tk.X,
            padx=12,
            pady=(0, 6)
        )

        self.result_label = tk.Label(
            result_frame,
            text="Select locations from the dropdown menus or click nodes directly on the map.",
            bg="white",
            fg="#37474F",
            font=("Arial", 10, "bold"),
            justify=tk.LEFT,
            anchor="w",
            wraplength=940
        )
        self.result_label.pack(fill=tk.X)

        # -------------------------------
        # CANVAS MAP DISPLAY
        # -------------------------------
        map_frame = tk.Frame(
            self.root,
            bg="white",
            relief=tk.SUNKEN,
            bd=1
        )
        map_frame.pack(
            fill=tk.BOTH,
            expand=True,
            padx=12,
            pady=(0, 6)
        )

        self.canvas = tk.Canvas(
            map_frame,
            bg="#FAFCFE",
            highlightthickness=0
        )
        self.canvas.pack(fill=tk.BOTH, expand=True)
        self.canvas.bind("<Button-1>", self.on_canvas_click)

        # -------------------------------
        # MAP LEGEND
        # -------------------------------
        legend_frame = tk.Frame(
            self.root,
            bg="#EAF0F6",
            padx=12,
            pady=6
        )
        legend_frame.pack(fill=tk.X)

        tk.Label(
            legend_frame,
            text="Legend:",
            bg="#EAF0F6",
            fg="#263238",
            font=("Arial", 9, "bold")
        ).pack(side=tk.LEFT, padx=(0, 10))

        tk.Label(
            legend_frame,
            text=(
                "Blue = Location    "
                "Green = Start    "
                "Yellow = Via    "
                "Orange = Destination    "
                "Red = Selected Route    "
                "Dashed Red = Closed Road"
            ),
            bg="#EAF0F6",
            fg="#455A64",
            font=("Arial", 8)
        ).pack(side=tk.LEFT)

        self.draw_base_map()

    def draw_base_map(self):
        """Draws basic map elements."""
        self.canvas.delete("all")

        self.canvas.create_text(
            20,
            20,
            text="Campus Map",
            anchor="w",
            fill="#263238",
            font=("Arial", 14, "bold")
        )

        # Draw edges
        for edge in self.all_edges:
            u, v = edge["u"], edge["v"]

            if (
                u in self.graph.coordinates
                and v in self.graph.coordinates
            ):
                x1, y1 = self.graph.coordinates[u]
                x2, y2 = self.graph.coordinates[v]

                mid_x = (x1 + x2) / 2
                mid_y = (y1 + y2) / 2

                if edge.get("closed", False):
                    self.canvas.create_line(
                        x1,
                        y1,
                        x2,
                        y2,
                        fill="#EF5350",
                        width=3,
                        dash=(6, 5)
                    )

                    self.canvas.create_oval(
                        mid_x - 11,
                        mid_y - 11,
                        mid_x + 11,
                        mid_y + 11,
                        fill="#F57C00",
                        outline="white",
                        width=2
                    )

                    self.canvas.create_text(
                        mid_x,
                        mid_y,
                        text="!",
                        fill="white",
                        font=("Arial", 10, "bold")
                    )

                    detour_msg = edge.get(
                        "detour_info",
                        "Road Closed"
                    )

                    self.canvas.create_text(
                        mid_x,
                        mid_y + 18,
                        text=detour_msg,
                        fill="#C62828",
                        font=("Arial", 8, "bold")
                    )

                else:
                    self.canvas.create_line(
                        x1,
                        y1,
                        x2,
                        y2,
                        fill="#B0BEC5",
                        width=4
                    )

                    self.canvas.create_text(
                        mid_x,
                        mid_y - 8,
                        text=f"{edge['weight']} m",
                        fill="#607D8B",
                        font=("Arial", 8)
                    )

        # Draw nodes
        for node_id, (x, y) in self.graph.coordinates.items():
            radius = 16

            self.canvas.create_oval(
                x - radius,
                y - radius,
                x + radius,
                y + radius,
                fill="#2196F3",
                outline="#0D47A1",
                width=2,
                tags="node"
            )

            self.canvas.create_text(
                x,
                y,
                text="●",
                fill="white",
                font=("Arial", 7, "bold"),
                tags="node"
            )

            self.canvas.create_text(
                x,
                y - 25,
                text=node_id,
                font=("Arial", 9, "bold"),
                fill="#263238",
                tags="node_label"
            )

    def reset_map(self):
        """Resets inputs and map canvas."""
        self.click_step = 0

        if self.node_list:
            self.start_combo.set(self.node_list[0])
            self.end_combo.set(self.node_list[-1])

        self.via_combo.set("None")

        self.result_label.config(
            text="Select locations from the dropdown menus or click nodes directly on the map.",
            fg="#37474F"
        )

        self.draw_base_map()

    def on_canvas_click(self, event):
        """Allows selecting nodes by clicking map."""
        clicked_node = None
        radius = 18

        for node_id, (nx, ny) in self.graph.coordinates.items():
            if math.hypot(event.x - nx, event.y - ny) <= radius:
                clicked_node = node_id
                break

        if clicked_node:
            if self.click_step == 0:
                self.start_combo.set(clicked_node)
                self.click_step = 1

                self.draw_base_map()

                self.result_label.config(
                    text=f"Start selected: {clicked_node}. Now click a different destination.",
                    fg="#1565C0"
                )

                sx, sy = self.graph.coordinates[clicked_node]

                self.canvas.create_oval(
                    sx - radius,
                    sy - radius,
                    sx + radius,
                    sy + radius,
                    fill="#43A047",
                    outline="black",
                    width=2
                )

                self.canvas.create_text(
                    sx,
                    sy - 27,
                    text=clicked_node,
                    fill="#263238",
                    font=("Arial", 9, "bold")
                )

            else:
                if clicked_node == self.start_var.get():
                    self.result_label.config(
                        text="Destination must be different from the Start location.",
                        fg="#C62828"
                    )
                    return

                self.end_combo.set(clicked_node)
                self.click_step = 0
                self.find_and_draw_route()

    def find_and_draw_route(self):
        """Calculates multi-leg shortest path and updates canvas display."""
        start = self.start_var.get()
        via = self.via_var.get()
        end = self.end_var.get()

        if start == end or (
            via != "None"
            and (start == via or end == via)
        ):
            messagebox.showwarning(
                "Invalid Selection",
                "Start, Via, and End locations must be distinct."
            )
            return

        self.draw_base_map()

        # Multi-leg routing logic remains unchanged.
        if via != "None":
            # Leg 1: Start to Via
            dist1, path1 = self.graph.dijkstra(start, via)

            # Leg 2: Via to End
            dist2, path2 = self.graph.dijkstra(via, end)

            if (
                dist1 == float("inf")
                or dist2 == float("inf")
                or not path1
                or not path2
            ):
                self.result_label.config(
                    text="No valid path passes through the selected middle stop.",
                    fg="#C62828"
                )
                return

            dist = dist1 + dist2
            path = path1 + path2[1:]

        else:
            # Direct navigation
            dist, path = self.graph.dijkstra(start, end)

            if dist == float("inf") or not path:
                self.result_label.config(
                    text="No path exists between the selected locations.",
                    fg="#C62828"
                )
                return

        # Calculate walking time.
        walk_mins = calculate_walk_time(dist)

        # Check detour warnings.
        warnings = []
        path_set = set(path)

        for edge in self.all_edges:
            if (
                edge.get("closed", False)
                and (
                    edge["u"] in path_set
                    or edge["v"] in path_set
                )
            ):
                status = edge.get("status", "Closed")
                info = edge.get(
                    "detour_info",
                    "Detour active"
                )

                warnings.append(
                    f"[{edge['u']} ↔ {edge['v']} - {status}]: {info}"
                )

        # Display route result.
        result_msg = (
            f"Shortest Route: {' → '.join(path)}\n"
            f"Total Distance: {dist} metres | "
            f"Estimated Walking Time: {walk_mins} minute(s)"
        )

        if warnings:
            result_msg += "\nDetour Notice: " + " | ".join(warnings)

            self.result_label.config(
                text=result_msg,
                fg="#C62828"
            )
        else:
            self.result_label.config(
                text=result_msg,
                fg="#2E7D32"
            )

        # Draw calculated route in red.
        for index in range(len(path) - 1):
            u = path[index]
            v = path[index + 1]

            x1, y1 = self.graph.coordinates[u]
            x2, y2 = self.graph.coordinates[v]

            self.canvas.create_line(
                x1,
                y1,
                x2,
                y2,
                fill="#D32F2F",
                width=6,
                arrow=tk.LAST,
                arrowshape=(10, 12, 5),
                tags="route"
            )

        # Keep nodes above route lines.
        self.canvas.tag_raise("node")
        self.canvas.tag_raise("node_label")

        # Highlight Start, Via, and End.
        radius = 18

        sx, sy = self.graph.coordinates[start]
        ex, ey = self.graph.coordinates[end]

        self.canvas.create_oval(
            sx - radius,
            sy - radius,
            sx + radius,
            sy + radius,
            fill="#43A047",
            outline="black",
            width=2
        )

        self.canvas.create_oval(
            ex - radius,
            ey - radius,
            ex + radius,
            ey + radius,
            fill="#FB8C00",
            outline="black",
            width=2
        )

        self.canvas.create_text(
            sx,
            sy - 28,
            text=start,
            font=("Arial", 9, "bold"),
            fill="#263238"
        )

        self.canvas.create_text(
            ex,
            ey - 28,
            text=end,
            font=("Arial", 9, "bold"),
            fill="#263238"
        )

        if via != "None":
            vx, vy = self.graph.coordinates[via]

            self.canvas.create_oval(
                vx - radius,
                vy - radius,
                vx + radius,
                vy + radius,
                fill="#FDD835",
                outline="black",
                width=2
            )

            self.canvas.create_text(
                vx,
                vy - 28,
                text=via,
                font=("Arial", 9, "bold"),
                fill="#263238"
            )


if __name__ == "__main__":
    root = tk.Tk()

    campus_graph = Graph()

    edges_data = load_graph_from_json(
        "map_data.json",
        campus_graph
    )

    app = CampusMapApp(
        root,
        campus_graph,
        edges_data
    )

    root.mainloop()
