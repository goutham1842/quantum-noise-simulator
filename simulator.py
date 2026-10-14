"""Pipeline controller: Builder -> Validation -> Ideal -> Noise Manager -> Noise Injection
-> Noisy Simulator -> Result Analyzer -> Visualization data -> Final report."""
from circuit_builder import QuantumCircuit
from validation import validate_circuit
from ideal_simulator import IdealSimulator
from noise_manager import NoiseManager
from noise_injection import injection_plan
from noisy_simulator import NoisySimulator
from analyzer import analyze, noise_sweep, compare_noise_types, build_report


def run_pipeline(circuit, noise_type, strength, shots=1000, seed=42, extras=True):
    valid, checks = validate_circuit(circuit)
    if not valid:
        return {"ok": False, "checks": checks}

    ideal = IdealSimulator().run(circuit, shots, seed)                       # Module 4

    cfg = (NoiseManager().select_noise_model(noise_type)                     # Module 5
           .set_noise_probability(strength).set_shots(shots).set_seed(seed).build_config())
    plan = injection_plan(circuit, cfg)                                      # Module 6
    noisy = NoisySimulator(cfg).run(circuit)                                 # Module 7

    analysis = analyze(ideal["probs"], noisy["probs"])                       # Result Analyzer
    out = {
        "ok": True, "checks": checks,
        "ideal": ideal, "manager": cfg.to_dict(),
        "injection": {"rows": plan, "readout": noise_type == "Readout Error"},
        "noisy": noisy, "analysis": analysis,
        "report": build_report(circuit, cfg, ideal, noisy, analysis),
    }
    if extras:                                                               # Visualization data
        out["sweep"] = noise_sweep(circuit, cfg, ideal["probs"], shots=min(cfg.shots, 400))
        out["compare"] = compare_noise_types(circuit, cfg, ideal["probs"], shots=min(cfg.shots, 1000))
    return out


def run_from_payload(payload):
    """Used by the web server: payload is the JSON sent by the page."""
    circuit = QuantumCircuit.from_dict(int(payload.get("n_qubits", 1)), payload.get("ops", []), payload.get("init"))
    noise = payload.get("noise", {})
    return run_pipeline(circuit, noise.get("type", "Bit Flip"), float(noise.get("strength", 0.1)),
                        int(payload.get("shots", 1000)), int(payload.get("seed", 42)))
