# 📱 Yamaha R3 Custom Dashboard (Raspberry Pi 5)

A lightweight, high-performance custom dashboard for the 2023 Yamaha R3 motorcycle built on the Raspberry Pi 5. Includes street and track day modes with real-time display of RPM, speed, lap timing, racing line tracking, and more.

---

## 🧹 Features

The dashboard includes two selectable display modes, optimized for different riding scenarios. Tap the screen or use a GPIO button to switch between them.

### ✅ Standard Mode (Street)

* RPM, Speed, Gear, Fuel
* Lean Angle (MPU-6050)
* Camera Feed (Optional)
* Tire Pressure Monitoring (Planned)
* Apple CarPlay support (Planned)

### 🏎️ Track Mode (Optional Display)

* Minimal UI with RPM Bar + Speed + Gear
* Lap Timing with automatic detection via GPS
* Split Time Deltas at checkpoints
* Racing Line Tracker (GPS path overlay)
* Best Lap Comparison

---

## 🧱 System Architecture

The system is divided into two independent services for performance and modularity:

### 1️⃣ Data Acquisition Service

Handles all sensor input and logging:

* CAN bus (ECU data: RPM, speed, gear, etc.)
* GPS module (lap timing, path tracking)
* MPU-6050 (lean angle)
* Writes to a shared memory buffer and logs to SQLite

### 2️⃣ GUI Display Service

Reads data from the shared buffer and updates the on-screen dashboard:

* Pygame-based frontend
* Switchable modes: Street and Track
* Highly responsive UI running at 30–60 FPS

```plaintext
[ Yamaha R3 ECU ]
        ↓
[ CAN Bus HAT ]  [ GPS Module ] [ MPU-6050 IMU ]
        ↓               ↓             ↓
        └───────────────┬─────────────┘
                        ↓
      ┌────────────────────────────────────┐
      │     Data Acquisition Service       │
      │         (Python asyncio)           │
      └────────────────────────────────────┘
                 ↓                ↓
     ┌────────────────┐   ┌────────────────────┐
     │ GUI Display    │   │ SQLite Logger      │
     │ (Pygame HUD)   │   │ (Lap data, stats)  │
     └────────────────┘   └────────────────────┘
```

* **Communication**: Shared memory or IPC (e.g., Unix socket or multiprocessing Queue)

* **Isolation**: Services can run independently and restart without affecting each other

* **Backend**: Python with `asyncio` for concurrent CAN, GPS, IMU data polling

* **Frontend**: Pygame (for fast, minimal latency rendering at 30–60 FPS)

* **Data Sync**: Shared data buffer pattern

* **Data Logging**: SQLite database for laps, splits, GPS traces, lean angles

---

## 🛠 Hardware Required

* ✅ Raspberry Pi 5
* ✅ 5" HDMI Touch Display
* ✅ CAN Bus HAT (with MCP2515 or similar)
* ✅ GPS Module (5–10 Hz refresh recommended)
* ✅ MPU-6050 (for lean angle sensing)
* ✅ UPS HAT or power supply for Pi
* ✅ SSD Kit (for OS and data logging)

---

## 📦 Software Dependencies

Install these on Raspberry Pi OS Lite (recommended, no GUI):

```bash
sudo apt update && sudo apt install -y \
  python3 python3-pip python3-pygame \
  python3-can python3-serial gpsd gpsd-clients sqlite3

pip install mpu6050-raspberrypi
```

Optional (for data visualization):

```bash
pip install matplotlib opencv-python
```

---

## 🚀 How to Run

### Step 1: Clone the repository

```bash
git clone https://github.com/skywallkee/yamaha-r3-dashboard
cd yamaha-r3-dashboard
```

### Step 2: Run Services Individually

#### Start Data Acquisition:

```bash
python3 services/data_acquisition.py
```

#### Start GUI Display:

```bash
python3 services/display_gui.py
```

Optional: Use `systemd` to autostart both services on boot.

Tap the screen or use GPIO button to switch between Street / Track mode.

---

## 📂 File Structure

```plaintext
yamaha-r3-dashboard/
├── config.py               # Configuration for sensors & UI
├── data_acquisition.py     # Sensor polling and logging
├── display_gui.py          # Pygame-based dashboard display
├── sensors/                # CAN, GPS, IMU readers (async)
├── display/                # Display logic
│   ├── trackmode/          # Track mode: lap timer, GPS logger, comparison
│   └── streetmode/         # Street mode: default UI and logic
├── storage/                # SQLite DB helpers and models
├── utils/                  # Helper modules
├── data/                   # Logs, exports
└── assets/                 # UI icons, fonts
```

---

## 📌 Notes

* Use `sudo chrt -f 99 python3 main.py` for real-time thread priority
* Designed to run in KMS/DRM mode (no GUI desktop)
* All data reads use non-blocking async methods

---

See `SETUP.md` for wiring diagrams, power tips, CAN bus setup, and more.
