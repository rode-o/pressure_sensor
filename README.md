# Pressure Sensor Desktop Logger

A minimal **PyQt 6** desktop application — plus companion **Arduino firmware** — for streaming, visualising, and logging data from a SparkFun **Qwiic MicroPressure (MPR‑series) sensor**.

---

## ✨ Key Features

| Feature | Description |
|---------|-------------|
| **Live read‑out** | GUI shows raw counts, PSI, and kPa in real time as data arrive over the serial port. |
| **One‑click recording** | Start / Stop buttons log each session to a time‑stamped CSV file for later analysis. |
| **Pre‑built Windows app** | Portable `PressureLogger.exe` in `dist/` — double‑click to run, no Python install required. |
| **Open firmware** | `hardware/mpr_firmware/mpr_firmware.ino` drives the sensor and emits a parse‑friendly line every 500 ms. |

---

## 🚀 Quick Start (from source)

```bash
# 1 Clone
git clone https://github.com/rode-o/pressure_sensor.git
cd pressure_sensor

# 2 Install dependencies (Python ≥ 3.11)
pip install -r requirements.txt        # PyQt6 · pyserial · etc.

# 3 Run the app
python main.py
```

1. Choose a **Data root** folder and **Test name**.  
2. Select the COM port for the microcontroller running `mpr_firmware.ino`.  
3. Click **Open**, then **Start** to stream; **Stop** writes the CSV.

---

## 🔧 Firmware Upload

1. Open `hardware/mpr_firmware/mpr_firmware.ino` in Arduino IDE or VS Code.  
2. Select any 3 V‑capable board (e.g., Nano Every) and flash.  
3. The sketch auto‑detects the sensor at I²C `0x18` and prints lines like

```
counts=0x4A72A1 | P=10.2356 PSI (70.569 kPa)
```

If you use another pressure range, update `COUNTS_MIN`, `COUNTS_MAX`, and `PSI_MAX` in the sketch **and** adjust the scaling in `core/pressuresensor.py`.

---

## 🗂 Repository Layout

```
controller/        Qt signal‑slot glue
core/              Data model, serial parser, CSV recorder
ui/                Designer‑generated widgets
hardware/          Arduino firmware
dist/              Pre‑built Windows release
build/             PyInstaller artefacts (ignored by .gitignore)
```

---

## 🛣 Roadmap

* Real‑time Matplotlib / pyqtgraph plot  
* Cross‑platform builds (macOS `.app`, Linux AppImage)  
* Temperature compensation & unit selection  
* GitHub Actions CI release pipeline  

---

**Early‑release notice:** APIs and file formats may change without notice. Contributions and issue reports are welcome!
