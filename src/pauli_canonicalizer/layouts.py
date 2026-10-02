"""Create and inspect canonical graph layouts."""

def make_type_a(path, pendants = None): 
    """Create a Type-A canonical graph layout.

    Parameters
    ----------
    path : iterable of int
        Vertices forming the ordered path.
    pendants : iterable of int, optional
        Additional vertices attached to the path center.

    Returns
    -------
    dict
        Type-A layout metadata.

    Raises
    ------
    ValueError
        If the path is too short or vertices are repeated.
    """
    path = list(path) # written left to right

    if pendants is None:
        pendants = []
    else:
        pendants = list(pendants)
    
    all_vertices = path + pendants

    if len(path) < 2:
        raise ValueError("Path must have atleast 2 elements")
    
    if len(set(all_vertices)) != len(all_vertices):
        raise ValueError("Path/Pendants cannot contain duplicates")
    
    return {"kind": "A", "path": path, "pendants": pendants, "center": None, "legs": []}

def make_type_b(kind, center, legs):

    """Create a Type-B canonical graph layout.

    Parameters
    ----------
    kind : {"B1", "B2", "B3"}
        Type-B canonical form.
    center : int
        Central vertex of the graph.
    legs : iterable of iterable of int
        Ordered legs extending outward from the center.

    Returns
    -------
    dict
        Type-B layout metadata.

    Raises
    ------
    ValueError
        If the kind or leg structure is invalid.
    """

    if kind not in {"B1", "B2", "B3"}:
        raise ValueError("kind must be B1, B2, or B3")
    
    legs = [list(leg) for leg in legs]

    if any(len(leg) == 0 for leg in legs):
        raise ValueError("legs cannot be empty")

    if not legs:
        raise ValueError("A type-B graph must have at least one leg")

    all_vertices = [center]

    for leg in legs:
        all_vertices.extend(leg)
    
    if len(set(all_vertices)) != len(all_vertices):
        raise ValueError("Centre/legs cannot contain duplicates")
    
    return {"kind": kind, "path": [], "pendants": [], "center": center, "legs": legs}

#Helper function for returning all vertices depending on canonical type

def layout_vertices(layout):
    if layout["kind"] == "A":
        return layout["path"] + layout["pendants"]

    vertices = [layout["center"]]

    for leg in layout["legs"]:
        vertices.extend(leg)

    return vertices

#Initialization with two vertices for the induction

def initialize_two_vertices(A, order):
    if len(order) < 2:
        raise ValueError("At least two vertices are required")

    v1 = order[0]
    v2 = order[1]

    if A[v1, v2] != 1: #In case an ordered list is not provided
        raise ValueError("The first two vertices must be connected")
    
    return make_type_a(path=[v1, v2], pendants=[])

#Helper Function to Get Length 1 Vertices for each canonical graph type

def get_length_one_vertices(layout):

    if layout["kind"] == "A":
        return [layout["path"][0]] + layout["pendants"]

    return [leg[0] for leg in layout["legs"] if len(leg) == 1]
