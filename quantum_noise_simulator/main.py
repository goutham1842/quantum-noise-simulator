"""Command-line demo (no website): shows how noise changes the results.
Run:  python main.py      -> prints results and saves results/final_report.txt
"""
import os
import sys
from circuit_builder import QuantumCircuit
from simulator import run_pipeline
from analyzer import pct

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "results")
os.makedirs(OUT, exist_ok=True)
report = []


def scenario(name, circuit, noise, p, shots=1000):
    r = run_pipeline(circuit, noise, p, shots, seed=42, extras=False)
    a = r["analysis"]
    lines = [f"=== {name} ===", circuit.draw(), f"Noise: {noise}, strength {pct(p)}, shots {shots}",
             f"Noise events injected: {r['noisy']['log']['events']}",
             "Outcome   Ideal     Noisy"]
    for k in sorted(r["ideal"]["probs"]):
        lines.append(f"{k:<10}{pct(r['ideal']['probs'][k]):<10}{pct(r['noisy']['probs'][k])}")
    lines.append(f"Error rate {pct(a['error'])} | Success rate {pct(a['success'])} | Fidelity {a['fidelity']:.3f}\n")
    block = "\n".join(lines)
    print(block)
    report.append(block)


project = QuantumCircuit(2); project.h(0).x(1).x(0).h(1).measure_all()
xgate = QuantumCircuit(1); xgate.x(0).measure_all()
bell = QuantumCircuit(2); bell.h(0).cnot(0, 1).measure_all()

scenario("1. X gate, Bit Flip (ideal is always 1)", xgate, "Bit Flip", 0.10)
scenario("2. Project circuit, Bit Flip (no visible change: states are |+> and |->)", project, "Bit Flip", 0.10)
scenario("3. Project circuit, Amplitude Damping", project, "Amplitude Damping", 0.30)
scenario("4. Bell state, Depolarizing", bell, "Depolarizing", 0.20)
scenario("5. Bell state, Amplitude Damping", bell, "Amplitude Damping", 0.20)
scenario("6. Bell state, Readout Error", bell, "Readout Error", 0.10)

with open(os.path.join(OUT, "final_report.txt"), "w", encoding="utf-8") as f:
    f.write("\n".join(report))
print("Saved", os.path.join(OUT, "final_report.txt"))
