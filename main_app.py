import math
import tkinter as tk
from tkinter import ttk, messagebox

from graph_logic import Graph, calculate_walk_time
from map_loader import load_graph_from_json


class CampusMapApp:
    def __init__(self, root, graph, all_edges):
        self.root = root
        self.graph = graph
        self.all_edges = all_edges

        self.root.title("Campus Navigation Planner")
        self.root.geometry("1000x720")
        self.root.minsize(850, 620)
        self.root.configure(bg="#eef2f5")

        self.click_step = 0
        self.node_radius = 15

        self.node_list = sorted(self.graph.adj_list.keys())

        self.create_header()
        self.create_control_panel()
        self.create_canvas()
        self.create_legend()

        self.draw_base_map()

    def create_header(self):
        """Creates the application title area."""
        header_frame = tk.Frame(
            self.root,
            bg="#1565C0",
            padx=15,
            pady=12
        )
        header_frame.pack(fill=tk.X)

        title_label = tk.Label(
            header_frame,
            text="Campus Navigation Planner",
            bg="#1565C0",
            fg="white",
            font=("Arial", 20, "bold")
        )
        title_label.pack(anchor="w")

        subtitle_label = tk.Label(
            header_frame,
            text=(
                "Find the shortest route between campus locations "
                "using Dijkstra's Algorithm."
            ),
            bg="#1565C0",
            fg="#E3F2FD",
            font=("Arial", 10)
        )
        subtitle_label.pack(anchor="w", pady=(3, 0))

    def create_control_panel(self):
        """Creates the route selection controls."""
        control_frame = tk.Frame(
            self.root,
            bg="#f5f7fa",
            padx=12,
            pady=10,
            relief=tk.RIDGE,
            bd=1
        )
        control_frame.pack(
            fill=tk.X,
            padx=10,
            pady=(10, 5)
        )

        for column in range(8):
            control_frame.grid_columnconfigure(column, weight=1)

        tk.Label(
            control_frame,
            text="Start Location",
            bg="#f5f7fa",
            font=("Arial", 9, "bold")
        ).grid(
            row=0,
            column=0,
            columnspan=2,
            sticky="w",
            padx=4
        )

        tk.Label(
            control_frame,
            text="Via Location (Optional)",
            bg="#f5f7fa",
            font=("Arial", 9, "bold")
        ).grid(
            row=0,
            column=2,
            columnspan=2,
            sticky="w",
            padx=4
        )

        tk.Label(
            control_frame,
            text="Destination",
            bg="#f5f7fa",
            font=("Arial", 9, "bold")
        ).grid(
            row=0,
            column=4,
            columnspan=2,
            sticky="w",
            padx=4
        )

        self.start_var = tk.StringVar()
        self.start_combo = ttk.Combobox(
            control_frame,
            textvariable=self.start_var,
            values=self.node_list,
            state="readonly",
            width=20
        )
        self.start_combo.grid(
            row=1,
            column=0,
            columnspan=2,
            sticky="ew",
            padx=4,
            pady=4
        )

        self.via_var = tk.StringVar()
        self.via_combo = ttk.Combobox(
            control_frame,
            textvariable=self.via_var,
            values=["None"] + self.node_list,
            state="readonly",
            width=20
        )
        self.via_combo.grid(
            row=1,
            column=2,
            columnspan=2,
            sticky="ew",
            padx=4,
            pady=4
        )

        self.end_var = tk.StringVar()
        self.end_combo = ttk.Combobox(
            control_frame,
            textvariable=self.end_var,
            values=self.node_list,
            state="readonly",
            width=20
        )
        self.end_combo.grid(
            row=1,
            column=4,
            columnspan=2,
            sticky="ew",
            padx=4,
            pady=4
        )

        if self.node_list:
            self.start_combo.set(self.node_list[0])
            self.end_combo.set(self.node_list[-1])

        self.via_combo.set("None")

        find_button = tk.Button(
            control_frame,
            text="Find Route",
            bg="#2E7D32",
            fg="white",
            activebackground="#1B5E20",
            activeforeground="white",
            font=("Arial", 10, "bold"),
            cursor="hand2",
            command=self.find_and_draw_route
        )
        find_button.grid(
            row=1,
            column=6,
            sticky="ew",
            padx=5,
            pady=4,
            ipady=4
        )

        reset_button = tk.Button(
            control_frame,
            text="Reset",
            bg="#616161",
            fg="white",
            activebackground="#424242",
            activeforeground="white",
            font=("Arial", 10, "bold"),
            cursor="hand2",
            command=self.reset_map
        )
        reset_button.grid(
            row=1,
            column=7,
            sticky="ew",
            padx=5,
            pady=4,
            ipady=4
        )

        self.result_label = tk.Label(
            control_frame,
            text=(
                "Select Start, Via, and Destination, "
                "then press Find Route."
            ),
            bg="#f5f7fa",
            fg="#333333",
            font=("Arial", 10, "bold"),
            justify=tk.LEFT,
            anchor="w",
            wraplength=900
        )
        self.result_label.grid(
            row=2,
            column=0,
            columnspan=8,
            sticky="ew",
            padx=4,
            pady=(8, 2)
        )

    def create_canvas(self):
        """Creates the scrollable campus map area."""
        map_frame = tk.Frame(
            self.root,
            bg="white",
            relief=tk.SUNKEN,
            bd=1
        )
        map_frame.pack(
            fill=tk.BOTH,
            expand=True,
            padx=10,
            pady=5
        )

        self.canvas = tk.Canvas(
            map_frame,
            bg="white",
            highlightthickness=0,
            scrollregion=(0, 0, 900, 650)
        )

        horizontal_scrollbar = ttk.Scrollbar(
            map_frame,
            orient=tk.HORIZONTAL,
            command=self.canvas.xview
        )

        vertical_scrollbar = ttk.Scrollbar(
            map_frame,
            orient=tk.VERTICAL,
            command=self.canvas.yview
        )

        self.canvas.configure(
            xscrollcommand=horizontal_scrollbar.set,
            yscrollcommand=vertical_scrollbar.set
        )

        self.canvas.grid(
            row=0,
            column=0,
            sticky="nsew"
        )

        vertical_scrollbar.grid(
            row=0,
            column=1,
            sticky="ns"
        )

        horizontal_scrollbar.grid(
            row=1,
            column=0,
            sticky="ew"
        )

        map_frame.grid_rowconfigure(0, weight=1)
        map_frame.grid_columnconfigure(0, weight=1)

        self.canvas.bind(
            "<Button-1>",
            self.on_canvas_click
        )

    def create_legend(self):
        """Creates the map color legend."""
        legend_frame = tk.Frame(
            self.root,
            bg="#eef2f5",
            padx=10,
            pady=6
        )
        legend_frame.pack(fill=tk.X)

        tk.Label(
            legend_frame,
            text="Legend:",
            bg="#eef2f5",
            font=("Arial", 9, "bold")
        ).pack(side=tk.LEFT, padx=(0, 10))

        legend_text = (
            "Blue = Location    "
            "Green = Start    "
            "Yellow = Via    "
            "Orange = Destination    "
            "Red Line = Route    "
            "Dashed Red = Closed Road"
        )

        tk.Label(
            legend_frame,
            text=legend_text,
            bg="#eef2f5",
            font=("Arial", 8)
        ).pack(side=tk.LEFT)

    def draw_base_map(self):
        """Draws all campus roads and locations."""
        self.canvas.delete("all")

        self.canvas.create_text(
            20,
            20,
            text="Campus Map",
            anchor="w",
            fill="#333333",
            font=("Arial", 14, "bold")
        )

        for edge in self.all_edges:
            self.draw_edge(edge)

        for node_id in self.graph.coordinates:
            self.draw_node(
                node_id,
                fill_color="#2196F3",
                outline_color="#0D47A1"
            )

    def draw_edge(self, edge):
        """Draws one path or road."""
        u = edge["u"]
        v = edge["v"]

        if u not in self.graph.coordinates:
            return

        if v not in self.graph.coordinates:
            return

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
                fill="#E53935",
                width=3,
                dash=(7, 5)
            )

            self.canvas.create_oval(
                mid_x - 10,
                mid_y - 10,
                mid_x + 10,
                mid_y + 10,
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

            detour_message = edge.get(
                "detour_info",
                "Road closed"
            )

            self.canvas.create_text(
                mid_x,
                mid_y + 20,
                text=detour_message,
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
                fill="#616161",
                font=("Arial", 8)
            )

    def draw_node(
        self,
        node_id,
        fill_color,
        outline_color="black"
    ):
        """Draws one location node and its label."""
        x, y = self.graph.coordinates[node_id]
        radius = self.node_radius

        self.canvas.create_oval(
            x - radius,
            y - radius,
            x + radius,
            y + radius,
            fill=fill_color,
            outline=outline_color,
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
            fill="#263238",
            font=("Arial", 9, "bold"),
            tags="node_label"
        )

    def reset_map(self):
        """Resets selections and redraws the map."""
        self.click_step = 0

        if self.node_list:
            self.start_combo.set(self.node_list[0])
            self.end_combo.set(self.node_list[-1])

        self.via_combo.set("None")

        self.result_label.config(
            text=(
                "Select Start, Via, and Destination, "
                "then press Find Route."
            ),
            fg="#333333"
        )

        self.draw_base_map()

    def on_canvas_click(self, event):
        """Allows the user to select map points directly."""
        canvas_x = self.canvas.canvasx(event.x)
        canvas_y = self.canvas.canvasy(event.y)

        clicked_node = self.get_clicked_node(
            canvas_x,
            canvas_y
        )

        if clicked_node is None:
            return

        if self.click_step == 0:
            self.start_combo.set(clicked_node)
            self.click_step = 1

            self.draw_base_map()

            self.draw_node(
                clicked_node,
                fill_color="#43A047"
            )

            self.result_label.config(
                text=(
                    f"Start selected: {clicked_node}. "
                    "Now click a different destination."
                ),
                fg="#1565C0"
            )

        else:
            if clicked_node == self.start_var.get():
                self.result_label.config(
                    text=(
                        "Destination must be different "
                        "from the Start location."
                    ),
                    fg="#C62828"
                )
                return

            self.end_combo.set(clicked_node)
            self.click_step = 0
            self.find_and_draw_route()

    def get_clicked_node(self, click_x, click_y):
        """Returns the node clicked by the user."""
        for node_id, coordinates in self.graph.coordinates.items():
            node_x, node_y = coordinates

            distance = math.hypot(
                click_x - node_x,
                click_y - node_y
            )

            if distance <= self.node_radius + 5:
                return node_id

        return None

    def validate_selection(self, start, via, end):
        """Checks that route selections are valid."""
        if not start or not end:
            messagebox.showwarning(
                "Missing Selection",
                "Select both a Start and Destination."
            )
            return False

        if start == end:
            messagebox.showwarning(
                "Invalid Selection",
                "Start and Destination must be different."
            )
            return False

        if via != "None":
            if via == start or via == end:
                messagebox.showwarning(
                    "Invalid Selection",
                    (
                        "The Via location must differ from "
                        "Start and Destination."
                    )
                )
                return False

        return True

    def find_and_draw_route(self):
        """Calculates and displays the shortest route."""
        start = self.start_var.get()
        via = self.via_var.get()
        end = self.end_var.get()

        if not self.validate_selection(
            start,
            via,
            end
        ):
            return

        if via == "None":
            distance, path = self.graph.dijkstra(
                start,
                end
            )
        else:
            distance, path = self.calculate_route_with_via(
                start,
                via,
                end
            )

        if distance == float("inf") or not path:
            self.draw_base_map()

            self.result_label.config(
                text=(
                    "No available route exists between "
                    "the selected locations."
                ),
                fg="#C62828"
            )
            return

        walking_minutes = calculate_walk_time(distance)

        self.draw_base_map()
        self.draw_route(path)
        self.highlight_route_points(
            start,
            via,
            end
        )

        route_text = " → ".join(path)

        result_text = (
            f"Shortest Route: {route_text}\n"
            f"Total Distance: {distance} metres | "
            f"Estimated Walking Time: "
            f"{walking_minutes} minute(s)"
        )

        detour_messages = self.get_detour_messages(path)

        if detour_messages:
            result_text += (
                "\nDetour Notice: "
                + " | ".join(detour_messages)
            )
            result_color = "#C62828"
        else:
            result_color = "#2E7D32"

        self.result_label.config(
            text=result_text,
            fg=result_color
        )

    def calculate_route_with_via(
        self,
        start,
        via,
        end
    ):
        """Calculates a route containing a middle stop."""
        first_distance, first_path = self.graph.dijkstra(
            start,
            via
        )

        second_distance, second_path = self.graph.dijkstra(
            via,
            end
        )

        if (
            first_distance == float("inf")
            or second_distance == float("inf")
            or not first_path
            or not second_path
        ):
            return float("inf"), []

        total_distance = (
            first_distance + second_distance
        )

        full_path = (
            first_path + second_path[1:]
        )

        return total_distance, full_path

    def draw_route(self, path):
        """Draws the shortest route using red arrows."""
        for index in range(len(path) - 1):
            current_node = path[index]
            next_node = path[index + 1]

            x1, y1 = self.graph.coordinates[current_node]
            x2, y2 = self.graph.coordinates[next_node]

            self.canvas.create_line(
                x1,
                y1,
                x2,
                y2,
                fill="#D32F2F",
                width=6,
                arrow=tk.LAST,
                arrowshape=(10, 12, 5),
                tags="selected_route"
            )

        self.canvas.tag_raise("node")
        self.canvas.tag_raise("node_label")

    def highlight_route_points(
        self,
        start,
        via,
        end
    ):
        """Highlights the main route locations."""
        self.draw_node(
            start,
            fill_color="#43A047"
        )

        if via != "None":
            self.draw_node(
                via,
                fill_color="#FDD835"
            )

        self.draw_node(
            end,
            fill_color="#FB8C00"
        )

    def get_detour_messages(self, path):
        """Returns relevant closed-road notices."""
        route_nodes = set(path)
        messages = []

        for edge in self.all_edges:
            if not edge.get("closed", False):
                continue

            u = edge["u"]
            v = edge["v"]

            if u in route_nodes and v in route_nodes:
                detour_information = edge.get(
                    "detour_info",
                    "Use an alternative route."
                )

                messages.append(
                    f"{u} to {v} is closed; "
                    f"{detour_information}"
                )

        return messages


def run_application():
    """Loads the data and starts the application."""
    root = tk.Tk()

    try:
        campus_graph = Graph()

        edges_data = load_graph_from_json(
            "map_data.json",
            campus_graph
        )

        CampusMapApp(
            root,
            campus_graph,
            edges_data
        )

        root.mainloop()

    except FileNotFoundError:
        messagebox.showerror(
            "File Error",
            (
                "map_data.json was not found. "
                "Keep it in the same folder as main_app.py."
            )
        )
        root.destroy()

    except Exception as error:
        messagebox.showerror(
            "Application Error",
            f"The application could not start:\n{error}"
        )
        root.destroy()


if __name__ == "__main__":
    run_application()
