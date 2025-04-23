from PyQt6.QtCore import QObject, pyqtSignal
import serial, re, binascii
from .datasample import DataSample

# ------------- regex used to parse a line -------------------
_LINE_RE = re.compile(
    r"counts=0x([0-9A-Fa-f]+).*?P=([\d.]+).*?\(\s*([\d.]+)\s*kPa",
    re.ASCII,
)

class PressureSensor(QObject):
    new_sample = pyqtSignal(DataSample)
    opened     = pyqtSignal(str)
    closed     = pyqtSignal()
    error      = pyqtSignal(str)

    def __init__(self, port: str, baud: int = 115200):
        super().__init__()
        self._port = port
        self._baud = baud
        self._ser  = None
        self._running = False

    # ----------------------------------------------------------
    def start(self):
        print(f"[sensor] THREAD started, trying {self._port} @ {self._baud}")
        try:
            self._ser = serial.Serial(self._port, self._baud, timeout=1.0)
        except serial.SerialException as e:
            self.error.emit(str(e))
            print(f"[sensor] ERROR opening port → {e}")
            return

        print(f"[sensor] Port {self._port} opened OK")
        self.opened.emit(self._port)
        self._running = True

        while self._running:
            try:
                raw = self._ser.readline()
            except serial.SerialException as e:
                self.error.emit(str(e))
                print(f"[sensor] SerialException while reading → {e}")
                break

            if not raw:
                continue

            # show exactly what arrived
            print(f"[sensor] RAW: {binascii.hexlify(raw)}")

            # decode & normalise NBSP
            line = raw.decode(errors="ignore").strip().replace("\u00A0", " ")
            print(f"[sensor] TXT: {line}")

            m = _LINE_RE.search(line)
            if not m:
                print("[sensor]  ✗  regex did NOT match")
                continue

            counts = int(m.group(1), 16)
            psi    = float(m.group(2))
            kpa    = float(m.group(3))
            print(f"[sensor]  ✓  match → counts={counts}  psi={psi}  kPa={kpa}")

            self.new_sample.emit(DataSample(counts, psi, kpa))

        self._cleanup()
        print("[sensor] THREAD exiting")

    def stop(self):
        print("[sensor] stop() called")
        self._running = False

    # ----------------------------------------------------------
    def _cleanup(self):
        if self._ser and self._ser.is_open:
            self._ser.close()
        self.closed.emit()
