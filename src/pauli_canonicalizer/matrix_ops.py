"""Apply contractions and certified macros to adjacency matrices."""

def contract(A, source, target):

    """Contract a source generator into an anticommuting target.

    Parameters
    ----------
    A : numpy.ndarray
        Anticommutation adjacency matrix.
    source : int
        Vertex multiplied into the target.
    target : int
        Vertex replaced by the contracted generator.

    Raises
    ------
    ValueError
        If either vertex is invalid or the vertices commute.
    """

    n = A.shape[0]

    if not (0 <= source and source < n):
        raise ValueError("source should be b/w 0 and n-1 (inclusive)")
    
    if not (0 <= target and target < n):
        raise ValueError("target should be b/w 0 and n-1 (inclusive)")
    
    if source == target:
        raise ValueError("source cannot be equal to target")
    
    if A[source][target] != 1:
        raise ValueError("source and target should anticommute for 'contraction'")

    for k in range(n):
        if k == target: # since [q', q'] = 0
            continue
        
        else:
            value = A[k, target] ^ A[k, source]
            A[k, target] = value
            A[target, k] = value
        
def apply_certified_macro(A, target, sources):
    """Apply the net XOR effect of a certified contraction sequence.

    Parameters
    ----------
    A : numpy.ndarray
        Anticommutation adjacency matrix.
    target : int
        Vertex updated by the macro.
    sources : sequence of int
        Vertices whose columns are XORed into the target.

    Returns
    -------
    numpy.ndarray
        The modified adjacency matrix.

    Raises
    ------
    ValueError
        If a vertex index is invalid or a source equals the target.
    """

    n = A.shape[0]
    sources = list(sources)
    for source in sources:
        if not (0 <= source < n):
            raise ValueError("source should be b/w 0 and n-1 (inclusive)")

        if source == target:
            raise ValueError("source cannot be equal to target")
    
    if not (0 <= target and target < n):
        raise ValueError("target should be b/w 0 and n-1 (inclusive)")
    
    new_column = A[:, target].copy()

    for source in sources:
        new_column ^= A[:,source]
    
    new_column[target] = 0 #Restore commutation [q', q'] = 0

    #Replace target column/row in matrix A after effective contraction sequence

    A[:, target] = new_column 
    A[target, :] = new_column

    return A