"""Module 7 - Noisy Simulator: runs the circuit WITH the selected noise for the chosen number of shots."""
import numpy as np
from statevector import new_state, apply_op, probabilities, outcome_keys, index_to_key
from noise_injection import inject_noise, flip_readout


class NoisySimulator:
    def __init__(self, config):
        self.cfg = config

    def run(self, circuit, shots=None, seed=None, noise_type=None, strength=None):
        cfg = self.cfg
        shots = shots or cfg.shots
        seed = cfg.seed if seed is None else seed
        ntype = noise_type or cfg.noise_type
        p = cfg.strength if strength is None else strength

        measured = circuit.measured_qubits()
        keys = outcome_keys(measured)
        counts = {k: 0 for k in keys}
        key_of = index_to_key(circuit.n, measured)
        ops = circuit.gate_ops()
        rng = np.random.default_rng(seed + 7919)
        log = {"events": 0, "per_qubit": [0] * circuit.n, "per_gate": {str(o.id): 0 for o in ops}}

        for _ in range(shots):
            state = new_state(circuit.n)
            for op in ops:
                apply_op(state, op)
                if ntype != "Readout Error":              # gate noise: after every gate, on every qubit it touches
                    for q in op.qubits:
                        if inject_noise(state, q, ntype, p, rng):
                            log["events"] += 1
                            log["per_qubit"][q] += 1
                            log["per_gate"][str(op.id)] += 1
            probs = probabilities(state)
            idx = int(np.searchsorted(np.cumsum(probs), rng.random() * probs.sum()))
            idx = min(idx, len(probs) - 1)
            if ntype == "Readout Error":                  # measurement noise: flip classical bits
                bits = [(idx >> q) & 1 for q in measured]
                bits, flips = flip_readout(bits, p, rng)
                for q, f in zip(measured, flips):
                    if f:
                        log["events"] += 1
                        log["per_qubit"][q] += 1
                counts["".join(map(str, bits))] += 1
            else:
                counts[key_of[idx]] += 1

        return {"counts": counts, "probs": {k: v / shots for k, v in counts.items()},
                "shots": shots, "log": log, "measured": measured}
