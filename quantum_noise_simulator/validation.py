"""Module 3 - Circuit Validation: checks the circuit before it is simulated.
Checks: empty circuit, invalid qubit, invalid gate parameter, incorrect gate connection, measurement."""
import math
from gates import ALL_GATES, ROTATIONS, SINGLE_QUBIT, TWO_QUBIT


def validate_circuit(circuit):
    """Returns (is_valid, checks). Each check: {ok, label, detail, final?}."""
    ops = circuit.ops
    n = circuit.n
    checks = []

    # 1. empty circuit
    checks.append({"ok": any(o.gate != "M" for o in ops), "label": "Circuit is not empty",
                   "detail": "Add at least one gate."})

    # 2. invalid qubit
    bad_q = [o for o in ops if any((not isinstance(q, int)) or q < 0 or q >= n for q in o.qubits)]
    checks.append({"ok": not bad_q, "label": "All qubit indices are valid",
                   "detail": f"A gate uses a qubit outside 0..{n - 1}."})

    # 3. invalid gate / parameter
    problem = ""
    for o in ops:
        if o.gate not in ALL_GATES:
            problem = f"Unknown gate '{o.gate}'."
        elif o.gate in TWO_QUBIT and len(o.qubits) != 2:
            problem = "CNOT needs exactly two qubits."
        elif (o.gate in SINGLE_QUBIT or o.gate == "M") and len(o.qubits) != 1:
            problem = f"{o.gate} needs exactly one qubit."
        elif o.gate in ROTATIONS and (o.param is None or not isinstance(o.param, (int, float))
                                      or not math.isfinite(o.param)):
            problem = f"{o.gate} needs a numeric angle."
        if problem:
            break
    checks.append({"ok": not problem, "label": "Gate parameters are valid", "detail": problem})

    # 4. incorrect gate connection
    why = ""
    seen = set()
    for o in ops:
        if o.gate == "CNOT" and len(o.qubits) == 2 and o.qubits[0] == o.qubits[1]:
            why = "CNOT control equals target."
        for q in o.qubits:
            if (q, o.col) in seen:
                why = "Two gates use the same wire in the same step."
            seen.add((q, o.col))
    for m in (o for o in ops if o.gate == "M" and o.qubits):
        if any(o.gate != "M" and m.qubits[0] in o.qubits and o.col > m.col for o in ops):
            why = f"A gate is placed after the measurement on q{m.qubits[0]}."
    checks.append({"ok": not why, "label": "Gate connections are correct", "detail": why})

    # 5. measurement
    measured = [o.qubits[0] for o in ops if o.gate == "M" and o.qubits]
    if not measured:
        detail, ok = "Add a measurement (use Measure All).", False
    elif len(set(measured)) != len(measured):
        detail, ok = "A qubit is measured more than once.", False
    else:
        detail, ok = "", True
    checks.append({"ok": ok, "label": "Measurement is present", "detail": detail})

    valid = all(c["ok"] for c in checks)
    checks.append({"ok": valid, "final": True, "detail": "",
                   "label": "VALID circuit - ready to simulate" if valid
                   else "INVALID circuit - fix the issues above"})
    return valid, checks
