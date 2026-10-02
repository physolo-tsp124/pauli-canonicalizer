"""Handle mixed lighting states on length-one legs."""

import numpy as np
from ..layouts import get_length_one_vertices, layout_vertices

#Checks if we are in Case 1: Type A/B, with atleast two length one differently lit vertices

def has_mixed_length_one_states(A, V, layout):

    """Check whether the length-one vertices have mixed states.

    Parameters
    ----------
    A : numpy.ndarray
        Anticommutation adjacency matrix.
    V : int
        Vertex being added to the canonical graph.
    layout : dict
        Current canonical graph layout.

    Returns
    -------
    bool
        Whether both lit and unlit length-one vertices exist.
    """

    length_one_vertices = get_length_one_vertices(layout)

    states = [A[vertex, V] for vertex in length_one_vertices]

    return 0 in states and 1 in states 

#Case 1 Lightning Reduction

def reduce_mixed_length_one_lighting(A, V, layout):

    """Reduce mixed length-one states to one lit vertex.

    Parameters
    ----------
    A : numpy.ndarray
        Anticommutation adjacency matrix.
    V : int
        Vertex being added to the canonical graph.
    layout : dict
        Current canonical graph layout.

    Returns
    -------
    int
        The unique active vertex remaining connected to V

    Raises
    ------
    ValueError
        If the case conditions fail or the reduction is unsuccessful.
    """

    active_vertices = layout_vertices(layout)
    length_one_vertices = get_length_one_vertices(layout)

    lit_length_one = []
    unlit_length_one = []

    for vertex in length_one_vertices:
        if A[V, vertex] == 1:
            lit_length_one.append(vertex)
        else:
            unlit_length_one.append(vertex)

    if not (lit_length_one and unlit_length_one):
        raise ValueError("Wrong case called. Needs to contain two length one differently lit vertices ")
    
    P = lit_length_one[0]
    Q = unlit_length_one[0]

    lit_vertices = [vertex for vertex in active_vertices if A[V, vertex] == 1]

    flip_column = A[:, P] ^ A[:, Q]

    #Useful for debugging if the neighbourhoods don't match
    if np.any(flip_column[active_vertices]):
        raise ValueError("P and Q do not have identical internal neighbourhoods")

    for g in lit_vertices:
        if g == P:
            continue
        A[: ,g] = A[:,g]^ flip_column #Change state only if lit/unlit duality between P/Q for all vertices
        A[g, g] = 0
        A[g, :] = A[:, g]
            
    
    final_lit_vertices = [vertex for vertex in active_vertices if A[V, vertex] == 1]

    if set(final_lit_vertices) != {P}:
        raise ValueError("Reduction to one lit vertex failed")

    return P