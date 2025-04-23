from dataclasses import dataclass, field
from time import time


@dataclass
class DataSample:
    counts: int          # 24‑bit raw value from sensor
    psi: float           # pounds per square inch
    kpa: float           # kilopascals
    # timestamp in epoch‑milliseconds; evaluated **each time** a sample is created
    ts_ms: int = field(default_factory=lambda: int(time() * 1_000))
