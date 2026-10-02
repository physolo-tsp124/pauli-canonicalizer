"""Reduce equal length-one lighting states on Type-B graphs."""

import numpy as np
from ..layouts import layout_vertices
from ..matrix_ops import apply_certified_macro
from .lookup import solve_residual_path

#Case 3: Type B with all legs of length one in the same initial state


def reduce_type_b_same_lighting(A, V, layout):

    """Reduce a Type-B lighting configuration to one lit vertex.

    Parameters
    ----------
    A : numpy.ndarray
        Anticommutation adjacency matrix.
    V : int
        Vertex being added to the canonical graph.
    layout : dict
        Current Type-B canonical layout.

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
    The reduction records the parity of legal toggles and applies their
    combined effect as one certified macro. 
    """

    n = A.shape[0]

    if layout["kind"] not in {"B1", "B2", "B3"}:
        raise ValueError("Case 3 requires a type-B layout")

    if not (0 <= V < n):
        raise ValueError("V must be between 0 and n-1")

    center = layout["center"]
    legs = layout["legs"]
    active_vertices = layout_vertices(layout)

    if V in active_vertices:
        raise ValueError("V must not already belong to the canonical graph")

    #Might help if we store this in the layout and make changes to it instead of finding it each time
    length_one_legs = [leg for leg in legs if len(leg) == 1] 
    length_two_legs = [leg for leg in legs if len(leg) == 2]

    if not length_one_legs:
        raise ValueError("A canonical type-B graph requires a length-one leg")

    if not length_two_legs:
        raise ValueError("A canonical type-B graph requires a length-two leg")
    
    length_one_vertices = [leg[0] for leg in length_one_legs]

    length_one_states = [A[V, vertex] for vertex in length_one_vertices]

    # Different states belong to Case 1.
    if len(set(length_one_states)) != 1:
        raise ValueError("Wrong case called: length-one legs have different states")

    lit_vertices = [vertex for vertex in active_vertices if A[V, vertex] == 1]

    if not lit_vertices:
        raise ValueError("V is disconnected from the current canonical graph")

    # a chosen length-one leg used as the auxiliary vertex omega.
    omega = length_one_vertices[0]

    
    neighbours = {vertex: [] for vertex in active_vertices}

    for leg in legs:
        # Connect O to L1.
        neighbours[center].append(leg[0])
        neighbours[leg[0]].append(center)

        # Connect L1-L2-L3-... along each leg.
        for i in range(len(leg) - 1):
            u = leg[i]
            w = leg[i + 1]

            neighbours[u].append(w)
            neighbours[w].append(u)


    # We use global vertex indices, which keeps the indexing simple.
    lighting = A[V, :].copy()
    parity = np.zeros(n, dtype=np.uint8)

    def toggle(vertex):
        if lighting[vertex] != 1:
            raise ValueError(f"Cannot legally toggle unlit vertex {vertex}")

        # Only the neighbours of vertex change their states.
        for neighbour in neighbours[vertex]:
            lighting[neighbour] ^= 1

        # Record whether this vertex is used an odd number of times.
        parity[vertex] ^= 1

    #Stage 1: Make O lit
      
    skip_length_two_normalization = False #To check if Stage 3 can be skipped from search in Stage 1

    if lighting[center] == 0:
        if lighting[omega] == 1:
            # omega is adjacent only to O.
            toggle(omega)
    
        else:
            chosen_leg = None

            # First look through all length-two legs.
            for leg in length_two_legs:
                if any(lighting[vertex] == 1 for vertex in leg):
                    chosen_leg = leg
                    break

            # If every length-two leg is unlit, any remaining
            # light must lie on the exceptional length-three/four leg.
            if chosen_leg is None:
                skip_length_two_normalization = True
                for leg in legs:
                    if len(leg) not in {3, 4}:
                        continue

                    if any(lighting[vertex] == 1 for vertex in leg):
                        chosen_leg = leg
                        break

            if chosen_leg is None:
                raise ValueError(
                    "Could not find a lit leg from which to light O"
                )

            # Find the lit vertex closest to O.
            innermost_lit_position = None

            for i, vertex in enumerate(chosen_leg):
                if lighting[vertex] == 1:
                    innermost_lit_position = i
                    break

            if innermost_lit_position is None:
                raise ValueError("The selected leg contains no lit vertex")

            # Toggle L_j, L_{j-1}, ..., L_1.
            for i in range(innermost_lit_position, -1, -1):
                toggle(chosen_leg[i])

            
    #Stage 2: Make all length one legs lit

    if lighting[omega] == 0: #If length one vertices unlit, toggle Centre
        toggle(center)

    #Stage 3: Make every L_2 unlit (length 2,3/4)

    if skip_length_two_normalization:
        # All length-two legs are already known to have M2 = 0.
        # Only the exceptional length-three/four leg needs checking.
        legs_to_normalize = [leg for leg in legs if len(leg) in {3, 4}]

    
    else:
        legs_to_normalize = [leg for leg in legs if len(leg) >= 2]

    
    for leg in legs_to_normalize:
        L1 = leg[0]
        L2 = leg[1]

        if lighting[L2] == 0: #If L2 already unlit, skip
            continue
        else:
            if lighting[L1] == 0:
                toggle(L2)
                toggle(L1)
                toggle(omega)
            else: #In case L1 & L2 is lit
                toggle(L1)
                toggle(omega)

        if lighting[L2] != 0:
            raise ValueError("Failed to switch L2 off")

        if lighting[center] == 0:
            raise ValueError("Toggling L1 should have switched O off (omega toggle is missed)")
    

    #Stage 4: Make M_1 of all length 2 legs lit

    if layout["kind"] == "B1":
        # Any length-two leg can be distinguished.
        distinguished_leg = length_two_legs[0]
        ordinary_length_two_legs = length_two_legs[1:]
    
    elif layout["kind"] == "B2":
        length_four_legs = [leg for leg in legs if len(leg) == 4]

        if len(length_four_legs) != 1:
            raise ValueError("Type B2 must have exactly one length-four leg")

        distinguished_leg = length_four_legs[0]
        ordinary_length_two_legs = length_two_legs
    
    elif layout["kind"] == "B3":
        length_three_legs = [leg for leg in legs if len(leg) == 3]

        if len(length_three_legs) != 1:
            raise ValueError("Type B3 must have exactly one length-three leg")

        distinguished_leg = length_three_legs[0]
        ordinary_length_two_legs = length_two_legs

    L2 = distinguished_leg[1]

    for M in ordinary_length_two_legs:
        M1 = M[0]
        M2 = M[1]
    
         # Stage 3 guarantees these preconditions.
        if lighting[L2] != 0 or lighting[M2] != 0:
            raise ValueError("Lemma 2 requires L2 and M2 to be unlit")
    
        # This leg is already in the required state (1, 0).
        if lighting[M1] == 1:
            continue
        
        # Compressed net effect of the certified Lemma 2 sequence: V -> V L2 M2
        # L2 and M2 themselves are unlit, so these are not two individual legal toggles. This  is the parity of the full
        # legal contraction sequence proved in Lemma 2.
        for source in (L2, M2):
            for neighbour in neighbours[source]:
                lighting[neighbour] ^= 1
    
            parity[source] ^= 1
    
        if lighting[M1] != 1:
            raise ValueError("Failed to light M1 using Lemma 2")
    
    #Stage 5: Make all length 2/1 legs dark
    
    toggle(center) #Since centre and all L_1 vertices (except distinguished leg) are lit
    
    # Stage 6: Solve the remaining constant-size path.
    final_vertex = solve_residual_path(layout["kind"], distinguished_leg, center, lighting, toggle)

    #Update Adjacency Matrix globally using parity
    sources = [vertex for vertex in active_vertices if parity[vertex] == 1]

    apply_certified_macro(A, target=V, sources=sources)
    
    final_lit_vertices = [vertex for vertex in active_vertices if A[V, vertex] == 1]

    if final_lit_vertices != [final_vertex]:
        raise ValueError("Type-B reduction did not produce exactly one lit vertex")
    
    return final_vertex


