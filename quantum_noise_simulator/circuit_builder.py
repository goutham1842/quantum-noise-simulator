"""Module 2 - Quantum Circuit Builder: creates the circuit from what the user selected."""
from dataclasses import dataclass, field
from typing import List, Optional


@dataclass
class Op:
    id: int
    gate: str
    qubits: List[int]
    col: int
    param: Optional[float] = None


class QuantumCircuit:
    def __init__(self, n_qubits: int):
        self.n = n_qubits
        self.ops: List[Op] = []
        self._next_id = 1

    # ---- building -------------------------------------------------
    def add_gate(self, gate, *qubits, col=None, param=None, op_id=None):
        gate = str(gate).upper()
        qubits = list(qubits)
        if col is None:  # place after the last gate on those wires
            used = [o.col for o in self.ops if set(o.qubits) & set(qubits)]
            col = (max(used) + 1) if used else 0
        oid = op_id if op_id is not None else self._next_id
        self._next_id = max(self._next_id, oid + 1)
        self.ops.append(Op(oid, gate, qubits, col, param))
        return self

    def h(self, q): return self.add_gate("H", q)
    def x(self, q): return self.add_gate("X", q)
    def y(self, q): return self.add_gate("Y", q)
    def z(self, q): return self.add_gate("Z", q)
    def rx(self, q, deg): return self.add_gate("RX", q, param=deg)
    def ry(self, q, deg): return self.add_gate("RY", q, param=deg)
    def rz(self, q, deg): return self.add_gate("RZ", q, param=deg)
    def cnot(self, c, t): return self.add_gate("CNOT", c, t)
    def measure(self, q): return self.add_gate("M", q)

    def measure_all(self):
        col = max((o.col for o in self.ops), default=-1) + 1
        done = {o.qubits[0] for o in self.ops if o.gate == "M"}
        for q in range(self.n):
            if q not in done:
                self.add_gate("M", q, col=col)
        return self

    @classmethod
    def from_dict(cls, n_qubits, ops):
        """Build from the JSON sent by the web page: [{id, gate, qubits, col, param}, ...]"""
        c = cls(n_qubits)
        for o in ops:
            c.add_gate(o.get("gate", ""), *o.get("qubits", []), col=o.get("col", 0),
                       param=o.get("param"), op_id=o.get("id"))
        return c

    # ---- views used by the simulators -------------------------------
    def gate_ops(self):
        """Gates (no measurements) in execution order."""
        return sorted((o for o in self.ops if o.gate != "M"), key=lambda o: (o.col, o.id))

    def measured_qubits(self):
        return sorted(o.qubits[0] for o in self.ops if o.gate == "M")

    @staticmethod
    def op_name(o):
        if o.gate == "CNOT":
            return f"CNOT(c=q{o.qubits[0]}, t=q{o.qubits[1]})"
        p = f"({o.param:g} deg)" if o.param is not None else ""
        return f"{o.gate}{p}(q{o.qubits[0]})"

    def draw(self):
        cols = max((o.col for o in self.ops), default=-1) + 1
        rows = []
        for q in range(self.n):
            line = f"q{q}: "
            for c in range(cols):
                cell = "--"
                for o in self.ops:
                    if o.col == c and q in o.qubits:
                        if o.gate == "CNOT":
                            cell = "*" if q == o.qubits[0] else "X"
                        else:
                            cell = o.gate
                line += f"-[{cell}]".ljust(6, "-")
            rows.append(line)
        return "\n".join(rows)
