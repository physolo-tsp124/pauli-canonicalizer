"""Restore canonical form after adding a reduced vertex."""

from .layouts import layout_vertices, make_type_a, make_type_b
from .matrix_ops import apply_certified_macro, contract


def canonical_cleanup(A, V, layout, final_vertex):

    """Insert a singly connected vertex and restore canonical form.

    Parameters
    ----------
    A : numpy.ndarray
        Current anticommutation matrix.
    V : int
        Vertex being added to the canonical graph.
    layout : dict
        Current canonical graph layout.
    final_vertex : int
        Unique active vertex connected to V.

    Returns
    -------
    dict
        Updated Type-A or Type-B canonical layout.

    Raises
    ------
    ValueError
        If the attachment is invalid or canonicalization fails.
    """

    n = A.shape[0]
    
    if not (0 <= V < n):
        raise ValueError("V must be between 0 and n-1")
    
    active_vertices = layout_vertices(layout)

    if V in active_vertices:
        raise ValueError("V must not already belong to the canonical graph")
    
    final_lit_vertices = [vertex for vertex in active_vertices if A[V, vertex] == 1]

    if final_lit_vertices != [final_vertex]:
        raise ValueError(f"Requires only one lit vertex -> {final_vertex}")
    
    #Deal with simple cases where after adding a vertex, graph remains canonical
    #Also convert graphs into a star type (not necessarily canonical)
    
    if layout["kind"] == "A":
        path = list(layout["path"])
        pendants = list(layout["pendants"])
        center = path[1]

        # Extending the end of the path preserves Type A.

        if final_vertex == path[-1]:
            return make_type_a(path=path + [V], pendants=pendants)
        
        # Attaching V directly to the center adds a new pendant.
        if final_vertex == path[1]:
             return make_type_a(path=path, pendants=pendants + [V])
        
        #With no other pendants, the final vertex attaching just extends the path
        
        if final_vertex == path[0] and not pendants:
             return make_type_a(path=[V]+path, pendants=[])
        
        omega = path[0]

        # Initially represent all Type-A pendants as star legs.

        legs = [[path[0]]]
        legs.extend([[vertex] for vertex in pendants])
        length_one_vertices = [path[0]] + pendants
        long_leg = path[2:]

        if final_vertex in length_one_vertices:
            # The chosen length-one leg becomes length two.
            for leg in legs:
                if leg[0] == final_vertex:
                    leg.append(V)
                    break

            if long_leg:
                legs.append(long_leg)

        else:
            # V is attached to an internal vertex of the long path.
            path_position = path.index(final_vertex)
            if not (2 <= path_position < len(path) - 1):
                raise ValueError("Unexpected Type-A attachment position")

            next_vertex = path[path_position + 1]
            # Compressed macro of Equation (B9).
            # This removes final_vertex--next_vertex-stuff and creates center--next_vertex-stuff.

            apply_certified_macro(A, target=next_vertex, sources=[omega, V])

            prefix_leg = path[2:path_position + 1] + [V]
            suffix_leg = path[path_position + 1:]

            legs.extend([prefix_leg, suffix_leg,])

    else:
        #Current layout is type B
        center = layout["center"]
        legs = [list(leg) for leg in layout["legs"]]
        
         # Attaching V directly to O preserves the Type-B kind.
        if final_vertex == center:
            legs.append([V])
            return make_type_b(kind=layout["kind"], center=center, legs = legs)
        
        containing_leg = None
        attachment_position = None
        
        for leg in legs:
            if final_vertex in leg:
                containing_leg = leg
                attachment_position = leg.index(final_vertex)
                break

        if containing_leg is None:
            raise ValueError("Could not find final_vertex in the Type-B legs")

        if attachment_position == len(containing_leg) - 1:
            # V extends the outer endpoint of this leg.
            containing_leg.append(V)

        else:
            # V creates a second branching point, so use B9.
            length_one_legs = [leg for leg in legs if len(leg) == 1]

            if not length_one_legs:
                raise ValueError("Equation (B9) requires a length-one leg")

            omega = length_one_legs[0][0]
            next_vertex = containing_leg[attachment_position + 1]
            apply_certified_macro(A, target=next_vertex, sources=[omega, V])

            prefix_leg = (containing_leg[:attachment_position + 1] + [V])
            suffix_leg = containing_leg[attachment_position + 1:]

            leg_index = legs.index(containing_leg)
            legs[leg_index:leg_index + 1] = [prefix_leg, suffix_leg]
        
    #Check exit to type A case after B9 Macro for instance
    length_one_legs = [leg for leg in legs if len(leg) == 1]
    nontrivial_legs = [leg for leg in legs if len(leg) >= 2]
        
    if len(nontrivial_legs) <= 1:
        # Choose one length-one leg as omega, the left endpoint of our Type-A path.
        omega = length_one_legs[0][0]
        pendants = [length_one_legs[i][0] for i in range(1, len(length_one_legs))]
        
        new_path = [omega,center]

        # If a nontrivial leg exists, append it to the path.
        if nontrivial_legs:
            new_path.extend(nontrivial_legs[0])

        return make_type_a(path=new_path, pendants=pendants)
    
    #Stage 1: Split every leg longer than length 4 
    
    pending_legs = list(legs)
    shortened_legs = []

    while pending_legs:
        leg = pending_legs.pop()

        if len(leg) <= 4:
            shortened_legs.append(leg)
        else:
            
            # Obtain L1, L3, and L5 from leg using their zero-based positions.
            L1 = leg[0]
            L3 = leg[2]
            L5 = leg[4]
            
            # Apply the certified macro L5 -> L5 * L1 * L3
            apply_certified_macro(A, target=L5, sources=[L1, L3])

            first_leg = leg[:4]
            remaining_leg = leg[4:]

            shortened_legs.append(first_leg)
            
            # remaining_leg might still be longer than four
            pending_legs.append(remaining_leg)
            

    legs = shortened_legs

    # Debugging assertion:
    if any(len(leg) > 4 for leg in legs):
        raise ValueError("Failed to split every long leg")
        
    #Bucket legs for future cases
    length_one_legs = [leg for leg in legs if len(leg) == 1]
    length_two_legs = [leg for leg in legs if len(leg) == 2]
    length_three_legs = [leg for leg in legs if len(leg) == 3]
    length_four_legs = [leg for leg in legs if len(leg) == 4]
    
    omega = length_one_legs[0][0] 
    
    #Stage 2: Split repeated legs of length three. 
    
    #Requires two length three legs L and M. We will be splitting only L into [L_1, L_2] and [L_3]

    while len(length_three_legs) >= 2:
        
        # Remove one length-three leg that will be split.
        L = length_three_legs.pop()

        # Keep another length-three leg as the auxiliary leg M.
        M = length_three_legs[0]

        L1 = L[0]
        L2 = L[1]
        L3 = L[2]

        M1 = M[0]
        M3 = M[2]

        apply_certified_macro(A, target=L3, sources=[L1, M1, M3, omega])

        length_two_legs.append([L1, L2])
        length_one_legs.append([L3])

    if len(length_three_legs) > 1:
        raise ValueError("Failed to eliminate repeated length-three legs")
        
    #Stage 3: Split length four legs into 2 legs of length two if a length three exists.
    
    if length_three_legs:
        # There is now exactly one length-three leg after Stage 2
        M = length_three_legs[0]
    
        M1 = M[0]
        M3 = M[2]

        while length_four_legs:
            # Remove one length-four leg.
            L = length_four_legs.pop()

            L1 = L[0]
            L2 = L[1]
            L3 = L[2]
            L4 = L[3]

            apply_certified_macro(A, target=L3, sources=[L1, M1, M3, omega])
            
            length_two_legs.append([L1, L2])
            length_two_legs.append([L3, L4])


        if length_four_legs:
            raise ValueError("Failed to eliminate length-four legs using the length-three leg")
    else:
        #Stage 4: Split pair of length four legs into four legs of length two
        while len(length_four_legs) >= 2:
            # Remove two length-four legs, calling them L and M.
            L = length_four_legs.pop()
            M = length_four_legs.pop()

            L1 = L[0]
            L2 = L[1]
            L3 = L[2]
            L4 = L[3]

            M1 = M[0]
            M2 = M[1]
            M3 = M[2]
            M4 = M[3]

            # Apply the compressed parity of Equation (B4):
            apply_certified_macro(A, target=L3, sources=[L1, M1])
    
            # Apply the two legal contractions from B5 and B6:
            contract(A, target=M2, source=M1)
            contract(A, target=center, source=M2)


            # Apply the compressed Lemma-2 cleanup:
            apply_certified_macro(A, target=M2, sources=[L4, M4])
            
  
            length_two_legs.append([L1, L2])
            length_two_legs.append([L3, L4])
            length_two_legs.append([M2, M1])
            length_two_legs.append([M3, M4])
            
    #Stage 5: Classify the resulting canonical Type-B graph
    
    if len(length_three_legs) > 1:
        raise ValueError("More than one length-three leg remains")

    if len(length_four_legs) > 1:
        raise ValueError("More than one length-four leg remains")

    if length_three_legs and length_four_legs:
        raise ValueError("Length-three and length-four legs cannot coexist in canonical form")

    if not length_one_legs:
        raise ValueError("Canonical Type B requires at least one length-one leg")

    if not length_two_legs:
        raise ValueError("Canonical Type B requires at least one length-two leg")

    if length_three_legs:
        kind = "B3"

    elif length_four_legs:
        kind = "B2"

    else:
        kind = "B1"

    canonical_legs = (length_one_legs + length_two_legs + length_three_legs + length_four_legs)

    return make_type_b(kind=kind, center=center, legs=canonical_legs)

