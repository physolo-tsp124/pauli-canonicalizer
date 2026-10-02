"""Solve the constant-size residual paths arising in Type-B reduction."""

def solve_residual_path(kind, distinguished_leg, center, lighting, toggle):
    """Reduce a Type-B residual path to one lit vertex.

    Parameters
    ----------
    kind : {"B1", "B2", "B3"}
        Canonical Type-B form.
    distinguished_leg : sequence of int
        Ordered vertices of the remaining nontrivial leg.
    center : int
        Central vertex of the graph.
    lighting : numpy.ndarray
        Current binary lighting state.
    toggle : callable
        Function that legally toggles a lit vertex.

    Returns
    -------
    int
        The unique vertex remaining lit

    Raises
    ------
    ValueError
        If the kind or residual configuration is unknown

    Notes
    -----
    This function assumes that the center is lit and L2 is unlit.
    The supplied "toggle" function modifies lighting in place.
    """
    
    if kind == "B1":  # O - L1 - L2
        L1 = distinguished_leg[0]
        L2 = distinguished_leg[1]

        if lighting[L1] == 1:
            toggle(L1)
            toggle(L2)
            final_vertex = L2
        else:
            final_vertex = center

    elif kind == "B2":  # O - L1 - L2 - L3 - L4
        L1 = distinguished_leg[0]
        L2 = distinguished_leg[1]
        L3 = distinguished_leg[2]
        L4 = distinguished_leg[3]

        initial_config = (lighting[L1], lighting[L3], lighting[L4])

        if initial_config == (1, 1, 1):
            toggle(L1)
            toggle(L2)
            toggle(L4)
            toggle(L3)
            final_vertex = L3

        elif initial_config == (1, 1, 0):  # L-L-D-L-D
            toggle(L1)  # D-L-L-L-D
            toggle(L2)  # D-D-L-D-D
            final_vertex = L2

        elif initial_config == (1, 0, 1):  # L-L-D-D-L
            toggle(L1)  # D-L-L-D-L
            toggle(L2)  # D-D-L-L-L
            toggle(L3)  # D-D-D-L-D
            final_vertex = L3

        elif initial_config == (0, 1, 1):  # L-D-D-L-L
            toggle(L3)  # L-D-L-L-D
            toggle(L2)  # L-L-L-D-D
            toggle(L1)  # D-L-D-D-D
            final_vertex = L1

        elif initial_config == (1, 0, 0):  # L-L-D-D-D
            toggle(L1)  # D-L-L-D-D
            toggle(L2)  # D-D-L-L-D
            toggle(L3)  # D-D-D-L-L
            toggle(L4)  # D-D-D-D-L
            final_vertex = L4

        elif initial_config == (0, 1, 0):  # L-D-D-L-D
            toggle(L3)  # L-D-L-L-L
            toggle(L2)  # L-L-L-D-L
            toggle(L1)  # D-L-D-D-L
            toggle(L4)  # D-L-D-L-L
            toggle(L3)  # D-L-L-L-D
            toggle(L2)  # D-D-L-D-D
            final_vertex = L2

        elif initial_config == (0, 0, 1):  # L-D-D-D-L
            toggle(L4)  # L-D-D-L-L
            toggle(L3)  # L-D-L-L-D
            toggle(L2)  # L-L-L-D-D
            toggle(L1)  # D-L-D-D-D
            final_vertex = L1

        elif initial_config == (0, 0, 0):  # L-D-D-D-D
            final_vertex = center

        else:
            raise ValueError(f"Unknown B2 residual configuration: {initial_config}")

    elif kind == "B3":  # O - L1 - L2 - L3
        L1 = distinguished_leg[0]
        L2 = distinguished_leg[1]
        L3 = distinguished_leg[2]

        initial_config = (lighting[L1], lighting[L3])

        if initial_config == (1, 1):  # L-L-D-L
            toggle(L1)  # D-L-L-L
            toggle(L2)  # D-D-L-D
            final_vertex = L2

        elif initial_config == (1, 0):  # L-L-D-D
            toggle(L1)  # D-L-L-D
            toggle(L2)  # D-D-L-L
            toggle(L3)  # D-D-D-L
            final_vertex = L3

        elif initial_config == (0, 1):  # L-D-D-L
            toggle(L3)  # L-D-L-L
            toggle(L2)  # L-L-L-D
            toggle(L1)  # D-L-D-D
            final_vertex = L1

        elif initial_config == (0, 0):  # L-D-D-D
            final_vertex = center

        else:
            raise ValueError(f"Unknown B3 residual configuration: {initial_config}")

    else:
        raise ValueError(f"Unknown canonical Type-B kind: {kind}")

    return final_vertex