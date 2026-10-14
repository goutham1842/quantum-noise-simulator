"""Module 5 - Noise Manager: selects the noise type, sets probability/strength,
manages the noise parameters and sends the configuration to Noise Injection."""
from dataclasses import dataclass

NOISE_TYPES = ["Bit Flip", "Phase Flip", "Depolarizing", "Amplitude Damping", "Phase Damping", "Readout Error"]

PARAM_NAME = {
    "Bit Flip": "p (flip probability)",
    "Phase Flip": "p (phase-flip probability)",
    "Depolarizing": "p (depolarizing probability)",
    "Amplitude Damping": "gamma (damping probability)",
    "Phase Damping": "lambda (dephasing strength)",
    "Readout Error": "p (readout flip probability)",
}
WHERE = {t: "after every gate, on each qubit it touches" for t in NOISE_TYPES}
WHERE["Readout Error"] = "at measurement (classical readout bit flip)"


@dataclass
class NoiseConfig:
    noise_type: str = "Bit Flip"
    strength: float = 0.1
    shots: int = 1000
    seed: int = 42

    @property
    def param_name(self):
        return PARAM_NAME[self.noise_type]

    @property
    def where(self):
        return WHERE[self.noise_type]

    def to_dict(self):
        return {"type": self.noise_type, "param_name": self.param_name, "strength": self.strength,
                "where": self.where, "shots": self.shots, "seed": self.seed}


class NoiseManager:
    def __init__(self):
        self._cfg = NoiseConfig()

    def select_noise_model(self, noise_type):
        if noise_type not in NOISE_TYPES:
            raise ValueError(f"Unknown noise type: {noise_type}")
        self._cfg.noise_type = noise_type
        return self

    def set_noise_probability(self, p):
        p = float(p)
        if not 0.0 <= p <= 1.0:
            raise ValueError("Noise strength must be between 0 and 1")
        self._cfg.strength = p
        return self

    def set_shots(self, shots):
        self._cfg.shots = max(10, min(20000, int(shots)))
        return self

    def set_seed(self, seed):
        self._cfg.seed = int(seed)
        return self

    def build_config(self):
        """The configuration object that is sent to the Noise Injection module."""
        return NoiseConfig(**vars(self._cfg))
