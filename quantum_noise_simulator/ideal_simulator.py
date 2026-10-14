"""Module 4 - Ideal Simulator: runs the validated circuit with NO noise (baseline result)."""
import numpy as np
from statevector import new_state, apply_op, probabilities, outcome_keys, index_to_key


class IdealSimulator:
    def run(self, circuit, shots=1000, seed=42):
        measured = circuit.measured_qubits()
        state = new_state(circuit.n)
        for op in circuit.gate_ops():
            apply_op(state, op)

        # exact probabilities of the measured qubits
        keys = outcome_keys(measured)
        probs = {k: 0.0 for k in keys}
        for idx, p in zip(index_to_key(circuit.n, measured), probabilities(state)):
            probs[idx] += float(p)

        # sample the requested number of shots
        rng = np.random.default_rng(seed)
        draws = rng.choice(len(keys), size=shots, p=np.array([probs[k] for k in keys]) / sum(probs.values()))
        counts = {k: int(np.sum(draws == i)) for i, k in enumerate(keys)}
        return {"probs": probs, "counts": counts, "measured": measured}
