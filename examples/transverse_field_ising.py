import numpy as np
from pauli_canonicalizer import canonicalize


def tfim_adjacency(number_of_qubits):
    if number_of_qubits < 2:
        raise ValueError("The TFIM example requires at least two qubits")

    number_of_generators = 2 * number_of_qubits - 1
    A = np.zeros((number_of_generators, number_of_generators), dtype=np.uint8)

    # Generator ordering:
    # X1, Z1Z2, X2, Z2Z3, ..., XN. Consecutive generators anticommute.
    for i in range(number_of_generators - 1):
        A[i, i + 1] = 1
        A[i + 1, i] = 1

    return A


def main():
    number_of_qubits = 10
    A = tfim_adjacency(number_of_qubits)

    canonical_A, layout, order, dimension = canonicalize(A, visualization=True, step=1)

    expected_dimension = number_of_qubits * (2 * number_of_qubits - 1)

    print("Final layout:")
    print(layout)

    print("Vertex order:")
    print(order)

    print("Calculated dimension:")
    print(dimension)

    print("Expected dimension:")
    print(expected_dimension)

    assert layout["kind"] == "A"
    assert len(layout["path"]) == 2 * number_of_qubits - 1
    assert len(layout["pendants"]) == 0
    assert dimension == expected_dimension

    print("TFIM example passed.")


if __name__ == "__main__":
    main()