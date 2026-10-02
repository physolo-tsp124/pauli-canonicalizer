import numpy as np
import random
from pauli_canonicalizer import canonicalize


def random_connected_symmetric_matrix(N):
    if N < 2:
        raise ValueError("The graph must contain at least two vertices")

    A = np.zeros((N, N), dtype=np.uint8)

    # Add random edges
    for i in range(N):
        for j in range(i):
            A[i, j] = random.randint(0, 1)
            A[j, i] = A[i, j]

    # Add a random spanning tree to guarantee connectivity
    for i in range(1, N):
        previous_vertex = random.randint(0, i - 1)
        A[i, previous_vertex] = 1
        A[previous_vertex, i] = 1

    return A


def main():
    #Change parameter values here
    A = random_connected_symmetric_matrix(N = 30)

    canonical_A, layout, order, dimension = canonicalize(A, visualization=True, step=2) 

    print("Final layout:")
    print(layout)

    print("Vertex order:")
    print(order)

    print("Calculated dimension:")
    print(dimension)

    print("Random connected-matrix example passed.")


if __name__ == "__main__":
    main()