"""Construct a connected processing order for graph vertices."""

import numpy as np

#Create Ordered list for vertices

def connected_vertex_order(A, start = 0):
    """Order graph vertices using breadth-first search.

    Parameters
    ----------
    A : numpy.ndarray
        Anticommutation adjacency matrix.
    start : int, default=0
        Vertex from which the search begins.

    Returns
    -------
    list of int
        Vertex order in which each new vertex is connected to an
        earlier vertex.

    Raises
    ------
    ValueError
        If ``start`` is invalid or the graph is disconnected.
    """

    n = A.shape[0]

    if not (0 <= start < n):
        raise ValueError("start should be between 0 and n-1 (inclusive)")

    current = [start]
    visited = np.zeros(n, dtype=bool)
    visited[start] = True

    #BFS to get ordered list: [v_1, v_2, ... , v_n] s.t for all 1<k<=n, v_{k} has atleast one neighbour in [v_1,..., v_{k-1}]
    
    for vertex in current:
        if len(current) == n:
            break
        for i in range(n):
            if A[i, vertex] == 1 and visited[i] == False:
                current.append(i)
                visited[i] = True
    
    if len(current) != n:
        raise ValueError("The anticommutation graph is disconnected.")
    
    return current
