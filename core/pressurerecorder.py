from PyQt6.QtCore import QObject, pyqtSignal
from .datasample import DataSample
import csv, datetime


class PressureRecorder(QObject):
    """
    Buffers DataSample objects during acquisition and writes a rich CSV
    when save_csv() is called.
    """

    saved = pyqtSignal(str)   # Emits filename on success
    error = pyqtSignal(str)   # Emits error string on failure

    def __init__(self):
        super().__init__()
        self._buf: list[DataSample] = []

    # ------------------------------------------------------
    # slots
    def add_sample(self, sample: DataSample):
        """Append one sample to the in‑memory buffer."""
        self._buf.append(sample)

    def save_csv(self, path: str):
        """Write the buffered data to *path* with extra time & bar columns."""
        if not self._buf:
            self.error.emit("No samples to save.")
            return

        t0_ms = self._buf[0].ts_ms       # first‑sample time for relative calc

        try:
            with open(path, "w", newline="") as f:
                w = csv.writer(f)
                # header
                w.writerow(
                    [
                        "t_abs_ms", "t_abs_s", "t_iso",
                        "t_rel_s", "t_rel_min",
                        "counts", "psi", "kpa", "bar"
                    ]
                )

                for s in self._buf:
                    t_rel_ms  = s.ts_ms - t0_ms
                    t_rel_s   = t_rel_ms / 1000.0
                    t_rel_min = t_rel_s / 60.0
                    t_abs_s   = s.ts_ms / 1000.0
                    t_iso     = datetime.datetime.fromtimestamp(
                        t_abs_s
                    ).isoformat(timespec="milliseconds")
                    bar       = s.kpa / 100.0

                    w.writerow(
                        [
                            s.ts_ms,
                            f"{t_abs_s:.3f}",
                            t_iso,
                            f"{t_rel_s:.3f}",
                            f"{t_rel_min:.3f}",
                            s.counts,
                            f"{s.psi:.4f}",
                            f"{s.kpa:.3f}",
                            f"{bar:.3f}",
                        ]
                    )

                f.flush()    # ensure fully written before we emit
            self.saved.emit(f"Saved → {path}")
        except OSError as e:
            self.error.emit(str(e))
