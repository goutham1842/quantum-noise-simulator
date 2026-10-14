"""Result Analyzer: compares Ideal vs Noisy results.
  Error rate   = total variation distance = 1/2 * sum |P_ideal - P_noisy|
  Success rate = 1 - error rate
  Fidelity     = (sum sqrt(P_ideal * P_noisy)) ^ 2
"""
import math
from noise_manager import NOISE_TYPES, NoiseConfig
from noisy_simulator import NoisySimulator


def analyze(ideal_probs, noisy_probs):
    keys = sorted(ideal_probs)
    tvd = 0.5 * sum(abs(ideal_probs[k] - noisy_probs[k]) for k in keys)
    bc = sum(math.sqrt(ideal_probs[k] * noisy_probs[k]) for k in keys)
    return {"error": tvd, "success": 1 - tvd, "fidelity": bc * bc}


def noise_sweep(circuit, cfg, ideal_probs, shots=400, points=11):
    """Noise impact: fidelity and error rate for strength 0..100% (selected noise type)."""
    sim = NoisySimulator(cfg)
    xs, fid, err = [], [], []
    for i in range(points):
        p = i / (points - 1)
        r = sim.run(circuit, shots=shots, seed=cfg.seed + i, strength=p)
        a = analyze(ideal_probs, r["probs"])
        xs.append(p); fid.append(a["fidelity"]); err.append(a["error"])
    return {"xs": xs, "fidelity": fid, "error": err}


def compare_noise_types(circuit, cfg, ideal_probs, shots=1000):
    """Error comparison: error rate of every noise type at the selected strength."""
    sim = NoisySimulator(cfg)
    out = []
    for t in NOISE_TYPES:
        r = sim.run(circuit, shots=shots, seed=cfg.seed + 99, noise_type=t)
        out.append({"n": t, "v": analyze(ideal_probs, r["probs"])["error"]})
    return out


def pct(x):
    s = f"{x * 100:.1f}"
    return (s[:-2] if s.endswith(".0") else s) + "%"


def build_report(circuit, cfg, ideal, noisy, a):
    gates = ", ".join(circuit.op_name(o) for o in circuit.gate_ops())
    L = ["QUANTUM NOISE SIMULATOR - FINAL REPORT", "=" * 44, "",
         f"Qubits: {circuit.n}   Gates: {gates}",
         "Measured: " + ", ".join(f"q{q}" for q in ideal["measured"]), "",
         f"Noise: {cfg.noise_type}   Strength: {pct(cfg.strength)}   Shots: {cfg.shots}   Seed: {cfg.seed}",
         f"Noise events injected: {noisy['log']['events']}", "",
         "Outcome   Ideal     Noisy     Change"]
    for k in sorted(ideal["probs"]):
        d = noisy["probs"][k] - ideal["probs"][k]
        L.append(f"{k:<10}{pct(ideal['probs'][k]):<10}{pct(noisy['probs'][k]):<10}{d * 100:+.1f}%")
    L += ["", f"Error rate  : {pct(a['error'])}", f"Success rate: {pct(a['success'])}",
          f"Fidelity    : {a['fidelity']:.4f}", "",
          "Definitions:",
          "  Error rate   = total variation distance = 1/2 * sum|P_ideal - P_noisy|",
          "  Success rate = 1 - error rate",
          "  Fidelity     = (sum sqrt(P_ideal * P_noisy))^2",
          "  Noise is simulated per shot with Monte-Carlo trajectories on a statevector (Python / numpy).",
          "  Outcome labels list the lowest measured qubit on the left."]
    return "\n".join(L)
