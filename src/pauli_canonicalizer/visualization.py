"""Store and draw intermediate canonical graphs."""

import math
from .layouts import layout_vertices


def take_snapshot(A, layout, stage, added_vertex):
    """Store the current canonical graph."""
    vertices = layout_vertices(layout)
    matrix = []

    for first_vertex in vertices:
        row = []

        for second_vertex in vertices:
            value = int(A[first_vertex, second_vertex])
            row.append(value)

        matrix.append(row)

    return {
        "stage": stage,
        "kind": layout["kind"],
        "vertices": vertices,
        "matrix": matrix,
        "added_vertex": added_vertex,
        "path": list(layout["path"]),
        "pendants": list(layout["pendants"]),
        "center": layout["center"],
        "legs": [list(leg) for leg in layout["legs"]]}


def write_history(history, filename):
    """Write the canonicalization history to a text file."""
    with open(filename, "w", encoding="utf-8") as file:
        for snapshot in history:
            file.write(f"stage: {snapshot['stage']}\n")
            file.write(f"kind: {snapshot['kind']}\n")
            file.write(f"added vertex: {snapshot['added_vertex']}\n")
            file.write("vertices: ")

            for vertex in snapshot["vertices"]:
                file.write(f"{vertex} ")

            file.write("\nmatrix:\n")

            for row in snapshot["matrix"]:
                for value in row:
                    file.write(f"{value} ")

                file.write("\n")

            file.write("end\n\n")


def get_edges(matrix):
    """Find the edges in an adjacency matrix."""
    edges = []

    for i in range(len(matrix)):
        for j in range(i + 1, len(matrix)):
            if matrix[i][j] == 1:
                edges.append([i, j])

    return edges


def choose_snapshots(history, step):
    """Choose regularly spaced graphs for the final image."""
    if not history:
        raise ValueError("history cannot be empty")

    if step < 1:
        raise ValueError("step must be at least 1")

    selected = []

    for i in range(0, len(history), step):
        selected.append(history[i])

    if selected[-1] != history[-1]:
        selected.append(history[-1])

    return selected


def get_type_a_positions(snapshot):
    """Place a Type-A path horizontally with its pendants above it."""
    path = snapshot["path"]
    pendants = snapshot["pendants"]
    positions = {}

    center = path[1]
    positions[center] = (0.0, 0.0)
    positions[path[0]] = (-1.0, 0.0)

    for i in range(2, len(path)):
        positions[path[i]] = (float(i - 1), 0.0)

    for i, vertex in enumerate(pendants):
        if len(pendants) == 1:
            angle = math.pi / 2
        else:
            angle = math.pi / 4 + i * (math.pi / 2) / (len(pendants) - 1)

        positions[vertex] = (math.cos(angle), math.sin(angle))

    return positions


def get_type_b_positions(snapshot):
    """Place the legs of a Type-B graph evenly around its center."""
    center = snapshot["center"]
    legs = sorted(snapshot["legs"], key=len, reverse=True)
    positions = {center: (0.0, 0.0)}

    for leg_number, leg in enumerate(legs):
        angle = 2 * math.pi * leg_number / len(legs)

        for distance, vertex in enumerate(leg, start=1):
            x = distance * math.cos(angle)
            y = distance * math.sin(angle)
            positions[vertex] = (x, y)

    return positions


def get_positions(snapshot):
    """Choose positions from the canonical graph type."""
    if snapshot["kind"] == "A":
        return get_type_a_positions(snapshot)

    return get_type_b_positions(snapshot)


def draw_snapshot(axis, snapshot, node_size, font_size, line_width):
    """Draw one canonical graph on a Matplotlib axis."""
    vertices = snapshot["vertices"]
    positions = get_positions(snapshot)
    edges = get_edges(snapshot["matrix"])

    for first_index, second_index in edges:
        first_vertex = vertices[first_index]
        second_vertex = vertices[second_index]

        first_x, first_y = positions[first_vertex]
        second_x, second_y = positions[second_vertex]

        axis.plot([first_x, second_x], [first_y, second_y], color="red", linewidth=line_width, zorder=1)

    for vertex in vertices:
        x, y = positions[vertex]

        if vertex == snapshot["added_vertex"]:
            color = "#1d4ed8"
        else:
            color = "red"

        axis.scatter(x, y, s=node_size, color=color, edgecolors="white", linewidths=0.8, zorder=2)

        axis.text(x, y, str(vertex), color="white", fontsize=font_size, ha="center", va="center", zorder=3)

    x_values = [position[0] for position in positions.values()]
    y_values = [position[1] for position in positions.values()]

    x_padding = max(0.8, (max(x_values) - min(x_values)) * 0.04)
    y_padding = max(0.8, (max(y_values) - min(y_values)) * 0.08)

    axis.set_xlim(min(x_values) - x_padding, max(x_values) + x_padding)

    axis.set_ylim(min(y_values) - y_padding, max(y_values) + y_padding)

    axis.set_aspect("equal")
    axis.axis("off")
    title_x = (min(x_values) + max(x_values)) / 2
    title_y = max(y_values)

    axis.annotate(
        f"{snapshot['stage']} vertices — type {snapshot['kind']}",
        xy=(title_x, title_y),
        xytext=(0, 50),
        textcoords="offset points",
        fontsize=12,
        ha="center",
        va="bottom")
       


def draw_history(history, step, filename):
    """Draw the selected canonical graphs in one image."""
    import matplotlib.pyplot as plt

    selected = choose_snapshots(history, step)

    number_of_graphs = len(selected)
    number_of_columns = min(3, number_of_graphs)
    number_of_rows = (number_of_graphs + number_of_columns - 1) // number_of_columns

    largest_graph = max(len(snapshot["vertices"]) for snapshot in selected)

    node_size = max(18, min(500, 2000 / largest_graph))
    font_size = max(2.5, min(8, 30 / math.sqrt(largest_graph)))
    line_width = max(0.7, min(2, 15 / math.sqrt(largest_graph)))

    figure = plt.figure(
        figsize=(4.8 * number_of_columns, 3.8 * number_of_rows,), constrained_layout=True)

    for i, snapshot in enumerate(selected):
        axis = figure.add_subplot(number_of_rows, number_of_columns, i + 1)

        draw_snapshot(axis, snapshot, node_size, font_size, line_width)

    figure.savefig(filename, dpi=200, bbox_inches="tight", facecolor="white")

    plt.close(figure)
