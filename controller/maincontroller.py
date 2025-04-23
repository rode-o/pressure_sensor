from PyQt6.QtCore import QObject, QThread
from core.pressuresensor import PressureSensor
from core.pressurerecorder import PressureRecorder
from ui.mainwindow import MainWindow
import pathlib, datetime


class MainController(QObject):
    """Glue logic between UI and sensor/recorder."""

    def __init__(self, view: MainWindow):
        super().__init__()
        self._view = view
        self._recorder = PressureRecorder()

        # pull persisted values immediately
        self._data_root: pathlib.Path | None = view.current_root()
        self._test_name: str | None = view.current_name()

        self._sensor = None
        self._thread = None

        # ---- UI → controller ----
        view.root_changed.connect(self._set_root)
        view.name_changed.connect(self._set_name)
        view.open_clicked.connect(self._open_port)
        view.start_clicked.connect(self._start)
        view.stop_clicked.connect(self._stop)

        # ---- recorder → UI ----
        self._recorder.saved.connect(view.show_status)
        self._recorder.error.connect(view.show_error)

    # ---------- configuration slots ----------
    def _set_root(self, path: pathlib.Path):
        self._data_root = path

    def _set_name(self, name: str):
        self._test_name = name.strip()

    # ---------- main workflow ----------
    def _open_port(self, port: str):
        if not (self._data_root and self._test_name):
            self._view.show_error("Please set both Data root and Test name first.")
            return

        self._sensor = PressureSensor(port)
        self._thread = QThread(objectName=f"SensorThread-{port}")
        self._sensor.moveToThread(self._thread)

        # sensor → UI / recorder
        self._sensor.opened.connect(self._view.on_port_opened)
        self._sensor.new_sample.connect(self._view.update_reading)
        self._sensor.new_sample.connect(self._recorder.add_sample)
        self._sensor.error.connect(self._view.show_error)

        self._thread.started.connect(self._sensor.start)
        self._sensor.closed.connect(self._thread.quit)

        self._thread.start()

    def _start(self):
        self._view.show_status("Streaming…")

    def _stop(self):
        if not self._sensor:
            return
        self._sensor.stop()
        self._thread.quit()
        self._thread.wait(2000)
        self._view.show_status("Stopped")

        ts = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        file_path = self._data_root / f"{self._test_name}_{ts}.csv"
        self._recorder.save_csv(str(file_path))

    # ---------- clean‑up ----------
    def __del__(self):
        if self._sensor:
            self._sensor.stop()
        if self._thread and self._thread.isRunning():
            self._thread.quit()
            self._thread.wait(1000)
