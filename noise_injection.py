"""Module 6 - Noise Injection: applies the configured noise model during simulation.
Noise is simulated per shot as a random trajectory on the statevector (Monte-Carlo):

  Bit Flip           X with probability p
  Phase Flip         Z with probability p
  Depolarizing       X, Y or Z (each p/3) with total probability p
  Amplitude Damping  quantum-jump trajectory: |1> -> |0> with probability gamma * P(|1>)
                     (otherwise the |1> amplitude is shrunk by sqrt(1-gamma) and renormalised)
  Phase Damping      Z with probability (1 - sqrt(1 - lambda)) / 2
  Readout Error      each measured bit flips with probability p (applied at measurement)
"""
import numpy as np
from gates import X, Y, Z
from statevector import apply_single, normalize, _indices
import math


def inject_noise(state, qubit, noise_type, p, rng):
    """Inject one noise channel on one qubit. Returns True if an error event happened."""
    if noise_type == "Bit Flip":
        if rng.random() < p:
            apply_single(state, X, qubit); return True
    elif noise_type == "Phase Flip":
        if rng.random() < p:
            apply_single(state, Z, qubit); return True
    elif noise_type == "Depolarizing":
        if rng.random() < p:
            apply_single(state, (X, Y, Z)[rng.integers(3)], qubit); return True
    elif noise_type == "Phase Damping":
        if rng.random() < (1 - math.sqrt(1 - p)) / 2:
            apply_single(state, Z, qubit); return True
    elif noise_type == "Amplitude Damping":
        n = int(np.log2(state.size))
        i0, i1 = _indices(n, qubit)
        p1 = float(np.sum(np.abs(state[i1]) ** 2))
        if rng.random() < p * p1:          # jump: |1> -> |0>
            state[i0] = state[i1]
            state[i1] = 0
            normalize(state)
            return True
        state[i1] *= math.sqrt(1 - p)      # no jump: damp the |1> amplitude
        normalize(state)
    return False


def flip_readout(bits, p, rng):
    """Readout error: flip each measured bit with probability p. Returns (bits, flips)."""
    out, flips = [], []
    for b in bits:
        if rng.random() < p:
            out.append(1 - b); flips.append(True)
        else:
            out.append(b); flips.append(False)
    return out, flips


def injection_plan(circuit, cfg):
    """Where noise will be injected (shown in the Noise Injection panel)."""
    rows = []
    if cfg.noise_type == "Readout Error":
        for o in circuit.ops:
            if o.gate == "M":
                rows.append({"id": f"m{o.id}", "step": o.col + 1, "name": f"M(q{o.qubits[0]})",
                             "where": "Readout bit flip at measurement", "qubit": o.qubits[0]})
    else:
        for o in circuit.gate_ops():
            qs = " & ".join(f"q{q}" for q in o.qubits)
            rows.append({"id": str(o.id), "step": o.col + 1, "name": circuit.op_name(o),
                         "where": f"{cfg.noise_type} on {qs}", "qubit": o.qubits[0]})
    return rows
