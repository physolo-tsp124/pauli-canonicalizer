"""Validate anticommutation adjacency matrices."""

import numpy as np

def validate_adjacency(A):

    """Validate and convert an anticommutation adjacency matrix.

    Parameters
    ----------
    A : array_like
        Candidate binary adjacency matrix.

    Returns
    -------
    numpy.ndarray
        Validated matrix with unsigned 8-bit entries.

    Raises
    ------
    ValueError
        If the matrix is not square, binary, symmetric, or has a
        nonzero diagonal.
    """

    A = np.asarray(A)

    if A.ndim != 2 or A.shape[0] != A.shape[1]:
        raise ValueError("The matrix must be square.")
    
    if not np.all((A == 0) | (A == 1)):
        raise ValueError("The matrix must be binary.")

    if not np.array_equal(A, A.T):
        raise ValueError("The matrix must be symmetric.")

    if np.any(np.diag(A) != 0):
        raise ValueError("The adjacency matrix must have a zero diagonal")
        
    A = A.astype(np.uint8, copy=False)

    return A