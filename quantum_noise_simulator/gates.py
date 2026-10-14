"""Quantum gate matrices (used by Circuit Builder and all simulators)."""
import numpy as np

_R = 1 / np.sqrt(2)

H = np.array([[_R, _R], [_R, -_R]], dtype=complex)
X = np.array([[0, 1], [1, 0]], dtype=complex)
Y = np.array([[0, -1j], [1j, 0]], dtype=complex)
Z = np.array([[1, 0], [0, -1]], dtype=complex)
S = np.array([[1, 0], [0, 1j]], dtype=complex)
T = np.array([[1, 0], [0, np.exp(1j * np.pi / 4)]], dtype=complex)

FIXED = {"H": H, "X": X, "Y": Y, "Z": Z, "S": S, "T": T}
ROTATIONS = {"RX", "RY", "RZ"}
SINGLE_QUBIT = set(FIXED) | ROTATIONS
TWO_QUBIT = {"CNOT"}
MEASURE = "M"
ALL_GATES = SINGLE_QUBIT | TWO_QUBIT | {MEASURE}


def rotation(name, degrees):
    t = np.deg2rad(degrees) / 2
    c, s = np.cos(t), np.sin(t)
    if name == "RX":
        return np.array([[c, -1j * s], [-1j * s, c]], dtype=complex)
    if name == "RY":
        return np.array([[c, -s], [s, c]], dtype=complex)
    if name == "RZ":
        return np.array([[np.exp(-1j * t), 0], [0, np.exp(1j * t)]], dtype=complex)
    raise ValueError(name)


def gate_matrix(name, param=None):
    """2x2 matrix of a single-qubit gate."""
    if name in FIXED:
        return FIXED[name]
    if name in ROTATIONS:
        return rotation(name, param)
    raise ValueError(f"No single-qubit matrix for gate {name}")
