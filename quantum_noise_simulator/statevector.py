"""Low-level statevector operations shared by the ideal and noisy simulators.
Qubit q is bit q of the basis-state index (index = sum bit_q * 2^q)."""
import numpy as np
from gates import gate_matrix

_cache = {}


def _indices(n, q):
    """(indices where bit q = 0, indices where bit q = 1) for n qubits."""
    key = (n, q)
    if key not in _cache:
        idx = np.arange(1 << n)
        i0 = idx[((idx >> q) & 1) == 0]
        _cache[key] = (i0, i0 | (1 << q))
    return _cache[key]


def new_state(n):
    state = np.zeros(1 << n, dtype=complex)
    state[0] = 1.0
    return state


def apply_single(state, matrix, q):
    v = state.reshape(-1, 2, 1 << q)
    state[:] = np.einsum("ij,ajb->aib", matrix, v).reshape(state.size)


def apply_cnot(state, control, target):
    n = int(np.log2(state.size))
    i0, i1 = _indices(n, control)          # control = 1 -> i1
    sel = i1[((i1 >> target) & 1) == 0]    # ... and target = 0
    partner = sel | (1 << target)
    a, b = state[sel].copy(), state[partner].copy()
    state[sel], state[partner] = b, a


def apply_op(state, op):
    if op.gate == "CNOT":
        apply_cnot(state, op.qubits[0], op.qubits[1])
    else:
        apply_single(state, gate_matrix(op.gate, op.param), op.qubits[0])


def normalize(state):
    norm = np.sqrt(np.sum(np.abs(state) ** 2))
    if norm > 0:
        state /= norm


def probabilities(state):
    return np.abs(state) ** 2


def outcome_keys(measured):
    """All bit-strings for the measured qubits in sorted order (first measured qubit on the left)."""
    m = len(measured)
    return [format(k, f"0{m}b") for k in range(1 << m)]


def index_to_key(n, measured):
    """Map every basis-state index to its measured-qubit bit-string."""
    return ["".join(str((i >> q) & 1) for q in measured) for i in range(1 << n)]
