"""Compute Lie-algebra dimensions from canonical graph layouts."""

def calculate_lie_dimension(layout):
    
    """Compute the Lie-algebra dimension of a canonical graph.

    Parameters
    ----------
    layout : dict
        Type-A or Type-B canonical graph layout.

    Returns
    -------
    int
        Dimension of the corresponding Lie algebra.

    Raises
    ------
    ValueError
        If the canonical graph kind is unknown.
    """

    kind = layout["kind"]

    if kind == "A":
        path_length = len(layout["path"])
        number_of_pendants = len(layout["pendants"])

        number_of_sectors = 2 ** number_of_pendants
        simple_dimension = path_length * (path_length + 1) // 2

        return number_of_sectors * simple_dimension

    if kind not in {"B1", "B2", "B3"}:
        raise ValueError(f"Unknown canonical graph kind: {kind}")

    leg_lengths = [len(leg) for leg in layout["legs"]]

    # A canonical Type-B graph has n_c + 1 length-one legs.
    number_of_symmetries = leg_lengths.count(1) - 1
    number_of_length_two_legs = leg_lengths.count(2)

    number_of_sectors = 2 ** number_of_symmetries

    if kind == "B1":
        # sp(2^n_2)
        representation_dimension = 2 ** number_of_length_two_legs
        simple_dimension = (representation_dimension * (representation_dimension + 1)// 2)

    elif kind == "B2":
        # so(2^(n_2 + 3))
        representation_dimension = 2 ** (number_of_length_two_legs + 3)

        simple_dimension = (representation_dimension * (representation_dimension - 1) // 2)

    else:
        # B3: su(2^(n_2 + 2))
        representation_dimension = 2 ** (number_of_length_two_legs + 2)
        simple_dimension = representation_dimension**2 - 1

    return number_of_sectors * simple_dimension