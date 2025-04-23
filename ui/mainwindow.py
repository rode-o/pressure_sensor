from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QLabel, QPushButton, QLineEdit,
    QVBoxLayout, QHBoxLayout, QFileDialog, QInputDialog, QMessageBox
)
from PyQt6.QtCore import pyqtSignal, QSettings
from serial.tools import list_ports
from core.datasample import DataSample
import pathlib


class MainWindow(QMainWindow):
    # signals listened to in MainController
    open_clicked  = pyqtSignal(str)             # port name
    start_clicked = pyqtSignal()
    stop_clicked  = pyqtSignal()
    root_changed  = pyqtSignal(pathlib.Path)    # directory
    name_changed  = pyqtSignal(str)             # test name

    # ──────────────────────────── init ─────────────────────────────
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Pressure Logger (PyQt6)")
        self._settings = QSettings("RodePeters", "PressureLogger")
        self._build_ui()
        self._restore_settings()

    # ─────────────────────────── build UI ──────────────────────────
    def _build_ui(self):
        central = QWidget(self)
        vbox    = QVBoxLayout(central)

        # ---- Data root row ----
        root_row = QHBoxLayout()
        self._le_root = QLineEdit()
        self._btn_root = QPushButton("Choose Data Root…")
        root_row.addWidget(QLabel("Data root:"))
        root_row.addWidget(self._le_root, stretch=1)
        root_row.addWidget(self._btn_root)
        vbox.addLayout(root_row)

        # ---- Test name row ----
        name_row = QHBoxLayout()
        self._le_name = QLineEdit()
        name_row.addWidget(QLabel("Test name:"))
        name_row.addWidget(self._le_name, stretch=1)
        vbox.addLayout(name_row)

        # ---- Live reading labels ----
        self._lbl_psi = QLabel("PSI: —")
        self._lbl_kpa = QLabel("kPa: —")
        for lbl in (self._lbl_psi, self._lbl_kpa):
            f = lbl.font(); f.setPointSize(14); f.setBold(True); lbl.setFont(f)
            vbox.addWidget(lbl)

        # ---- Control buttons ----
        self._btn_open  = QPushButton("Open Port")
        self._btn_start = QPushButton("Start")
        self._btn_stop  = QPushButton("Stop")
        self._btn_start.setEnabled(False)
        self._btn_stop.setEnabled(False)

        hbox = QHBoxLayout()
        for b in (self._btn_open, self._btn_start, self._btn_stop):
            hbox.addWidget(b)
        vbox.addLayout(hbox)
        self.setCentralWidget(central)

        # wiring
        self._btn_root.clicked.connect(self._choose_root)
        self._le_root.textChanged.connect(self._on_root_changed)
        self._le_name.textChanged.connect(self._on_name_changed)
        self._btn_open.clicked.connect(self._choose_port)

        self._btn_start.clicked.connect(
            lambda: (
                self.start_clicked.emit(),
                self._btn_start.setEnabled(False),
                self._btn_stop.setEnabled(True)
            )
        )
        self._btn_stop.clicked.connect(
            lambda: (
                self.stop_clicked.emit(),
                self._btn_start.setEnabled(True),
                self._btn_stop.setEnabled(False)
            )
        )

    # ─────────────────────── settings helpers ─────────────────────
    def _restore_settings(self):
        root = self._settings.value("data_root", str(pathlib.Path.home()))
        name = self._settings.value("test_name", "test1")
        self._le_root.setText(root)
        self._le_name.setText(name)
        # inform controller of initial values
        self.root_changed.emit(pathlib.Path(root))
        self.name_changed.emit(name)

    def _save_setting(self, key: str, value):
        self._settings.setValue(key, value)

    # ─────────────────────── accessors for controller ──────────────
    def current_root(self):
        txt = self._le_root.text().strip()
        return pathlib.Path(txt) if txt else None

    def current_name(self):
        txt = self._le_name.text().strip()
        return txt or None

    # ─────────────────────────── slots & helpers ───────────────────
    def _on_root_changed(self, txt: str):
        if txt:
            self.root_changed.emit(pathlib.Path(txt))
            self._save_setting("data_root", txt)

    def _on_name_changed(self, txt: str):
        self.name_changed.emit(txt)
        self._save_setting("test_name", txt)

    def _choose_root(self):
        dir_path = QFileDialog.getExistingDirectory(self, "Select Data Root")
        if dir_path:
            self._le_root.setText(dir_path)  # triggers _on_root_changed

    def _choose_port(self):
        ports = [p.device for p in list_ports.comports()]
        port, ok = QInputDialog.getItem(
            self, "Select Port", "Serial Port:", ports, 0, False
        )
        if ok and port:
            self.open_clicked.emit(port)

    # controller‑triggered UI updates
    def on_port_opened(self, *_):
        self._btn_start.setEnabled(True)
        self.show_status("Port opened.")

    def update_reading(self, sample: DataSample):
        self._lbl_psi.setText(f"PSI: {sample.psi:.3f}")
        self._lbl_kpa.setText(f"kPa: {sample.kpa:.3f}")

    def show_error(self, msg: str):
        QMessageBox.critical(self, "Error", msg)

    def show_status(self, msg: str):
        self.statusBar().showMessage(msg, 4000)
