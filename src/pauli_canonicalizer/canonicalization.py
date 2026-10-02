from .cleanup import canonical_cleanup
from .dimension import calculate_lie_dimension
from .layouts import initialize_two_vertices
from .ordering import connected_vertex_order
from .reductions.mixed import has_mixed_length_one_states
from .reductions.mixed import reduce_mixed_length_one_lighting
from .reductions.type_a import reduce_type_a_same_lighting
from .reductions.type_b import reduce_type_b_same_lighting
from .validation import validate_adjacency
from .visualization import draw_history, take_snapshot, write_history

def canonicalize(A, start=0, visualization=False, step=1):
    """Transform a connected anticommutation graph into canonical form.

    Parameters
    ----------
    A : array_like
        Square binary symmetric adjacency matrix with zero diagonal.
    start : int, default=0
        Starting vertex for the connected ordering.

    Returns
    -------
    canonical_A : numpy.ndarray
        Canonicalized adjacency matrix.
    layout : dict
        Description of the final canonical graph.
    order : list of int
        Order in which the vertices were processed.
    dimension : int
        Dimension of the corresponding Lie algebra.

    Raises
    ------
    ValueError
        If the matrix is invalid or its graph is disconnected.

    Notes
    -----
    The generators are assumed to form a minimal, multiplicatively
    independent set.
    """


    A = validate_adjacency(A).copy()
    n = A.shape[0]

    history = []

    if n < 2:
        raise ValueError("Canonicalization requires at least two vertices")

    if visualization and (step < 1):
        raise ValueError("step must be at least 1")
    # Find an ordering such that every new vertex has at least one neighbour among the previously processed vertices.
    order = connected_vertex_order(A, start=start)

    # The first two connected vertices form the initial Type-A path.
    layout = initialize_two_vertices(A, order)

    if visualization:
        snapshot = take_snapshot(A, layout, stage=2, added_vertex=order[1])
        history.append(snapshot)

    # Add the remaining vertices one at a time.
    for k in range(2, n):
        V = order[k]

        # Case 1: At least two length-one legs have different states.
        if has_mixed_length_one_states(A, V, layout):
            final_vertex = reduce_mixed_length_one_lighting(A, V, layout)

        # Case 2: Type A with all length-one legs in the same state.
        elif layout["kind"] == "A":
            final_vertex = reduce_type_a_same_lighting(A, V, layout)

        # Case 3: Type B with all length-one legs in the same state.
        else:
            final_vertex = reduce_type_b_same_lighting(A, V, layout)

        # Insert V at its unique remaining connection and return the enlarged graph to canonical form.
        layout = canonical_cleanup(A, V, layout, final_vertex)

        if visualization:
            snapshot = take_snapshot(A, layout, stage= k + 1, added_vertex=V)
            history.append(snapshot)
    # Compute the dimension from the final canonical layout.
    lie_dimension = calculate_lie_dimension(layout)
    
    if visualization:
        write_history(history, "canonicalization_history.txt")
        draw_history(history, step, "canonicalization_history.png")
    return A, layout, order, lie_dimension