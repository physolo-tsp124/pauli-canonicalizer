"""Reduce equal length-one lighting states on Type-A graphs."""

import numpy as np
from ..layouts import layout_vertices
from ..matrix_ops import apply_certified_macro



#Case 2: Type A with all legs of length one in the same initial state

def reduce_type_a_same_lighting(A, V, layout):

    """Reduce a Type-A lighting configuration to one lit vertex.

    Parameters
    ----------
    A : numpy.ndarray
        Anticommutation adjacency matrix.
    V : int
        Vertex being added to the canonical graph.
    layout : dict
        Current Type-A canonical layout.

    Returns
    -------
    int
        The unique active vertex remaining connected to V.

    Raises
    ------
    ValueError
        If the case conditions fail or the reduction is unsuccessful.

    Notes
    -----
    The reduction maps the lighting to auxiliary bits, sorts them by
    legal adjacent swaps, and applies the resulting parity as one macro.
    """

    if layout["kind"] != "A":
        raise ValueError("Case 2 requires a type-A graph")

    path = layout["path"]
    pendants = layout["pendants"]
    active_vertices = layout_vertices(layout)

    length_one_vertices = [path[0]] + pendants #length one leg vertices

    length_one_states = [A[V, vertex] for vertex in length_one_vertices]

    if len(set(length_one_states)) != 1: #Checks if all length one legs have the same initial state
        raise ValueError("Wrong case called: length-one legs have different states")

    if not any(A[V, vertex] == 1 for vertex in active_vertices): #Checks if V is connected to current canonical graph
        raise ValueError("V has no connection to the current canonical graph")

    x = np.array([A[V, vertex] for vertex in path], dtype=np.uint8) #Choose vertex[0] to be representative of all length 1 vertices

    y = np.zeros(len(path) + 1, dtype=np.uint8)

    y[0] = 0 #Choose initial gauge for y_0

    for i in range(len(path)):
        y[i + 1] = y[i] ^ x[i] #x[0] corresponds to x_1

    # parity[i] records whether path[i] is toggled an even or odd number of times.abs

    parity = np.zeros(len(path), dtype=np.uint8) #Initialized with all 0's


    ones_seen = 0

    #Performing adjacent swaps b/w unequal 0&1 bits

    #NOTE: Need to implement better algorithm to avoid worst case O(n^2)

    number_of_ones = int(np.count_nonzero(y))
    number_of_zeros = len(y) - number_of_ones

    if number_of_ones == 0 or number_of_zeros == 0:
        raise ValueError("The lighting has no domain wall")

    if pendants and number_of_ones == 1:
        # Sort zeros first.
        zeros_seen = 0

        for i in range(len(y)):
            if y[i] == 0:
                parity[zeros_seen:i] ^= 1

                y[i] = 1
                y[zeros_seen] = 0

                zeros_seen += 1

        final_vertex = path[number_of_zeros - 1]

    else:
        # Sort ones first.
        ones_seen = 0

        for i in range(len(y)):
            if y[i] == 1:
                parity[ones_seen:i] ^= 1

                y[i] = 0
                y[ones_seen] = 1

                ones_seen += 1

        final_vertex = path[number_of_ones - 1]

    

    #Apply compiled macro for contraction process

    sources = [path[i] for i in range(len(path)) if parity[i] == 1]

    apply_certified_macro(A, target=V, sources=sources)

    final_lit_vertices = [vertex for vertex in active_vertices if A[V, vertex] == 1]

    if final_lit_vertices != [final_vertex]:
        raise ValueError("Type-A reduction did not produce exactly one lit vertex")

    return final_vertex
