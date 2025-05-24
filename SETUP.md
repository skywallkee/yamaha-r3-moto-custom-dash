# ⚙️ SETUP.md – Yamaha R3 Custom Dashboard

This guide helps you wire, configure, and optimize your Raspberry Pi 5-based dashboard for real-time performance on your Yamaha R3 motorcycle.

---

## 🔌 Hardware Wiring Instructions

### CAN Bus (ECU → Pi)

* Use a CAN Bus HAT (e.g., MCP2515 SPI HAT)
* Connect:

  * `CAN_H` to bike CAN high
  * `CAN_L` to bike CAN low
  * SPI pins (MISO/MOSI/SCLK/CE0) to Pi
* Termination resistor (120Ω) may be needed

### GPS Module

* Most use UART or USB
* If UART:

  * Connect TX → GPIO15 (RX)
  * RX → GPIO14 (TX)
  * Enable UART in `raspi-config`

### MPU-6050 (Gyroscope + Accelerometer)

* Uses I2C
* Connect:

  * VCC → 3.3V or 5V
  * GND → GND
  * SDA → GPIO2 (SDA)
  * SCL → GPIO3 (SCL)
* Enable I2C with:

  ```bash
  sudo raspi-config # → Interface Options → I2C → Enable
  ```

### Touchscreen Display

* Connect via HDMI and USB
* Set display rotation via `/boot/config.txt` if needed

### UPS HAT

* Stack on top of Pi
* Ensure proper shutdown script for power loss (optional)

---

## ⚙️ System Setup Tips

### 1. Run Without Desktop (No GUI)

* Use Raspberry Pi OS Lite (headless setup)
* Run Pygame directly on framebuffer with no X server

### 2. Boost Performance

* Disable HDMI sleep:

  ```bash
  sudo nano /boot/config.txt
  # Add:
  hdmi_blanking=1
  ```
* Add real-time priority:

  ```bash
  sudo apt install util-linux
  sudo chrt -f 99 python3 main.py
  ```

### 3. Autostart on Boot with systemd

Create a service file `/etc/systemd/system/dashboard-acquisition.service`:

```ini
[Unit]
Description=Yamaha R3 Data Acquisition
After=network.target

[Service]
ExecStart=/usr/bin/python3 /home/pi/yamaha-r3-dashboard/services/data_acquisition.py
Restart=always
User=pi

[Install]
WantedBy=multi-user.target
```

Create a second service file `/etc/systemd/system/dashboard-gui.service`:

```ini
[Unit]
Description=Yamaha R3 GUI Display
After=network.target

[Service]
ExecStart=/usr/bin/python3 /home/pi/yamaha-r3-dashboard/services/display_gui.py
Restart=always
User=pi

[Install]
WantedBy=multi-user.target
```

Then enable both:

```bash
sudo systemctl enable dashboard-acquisition
sudo systemctl enable dashboard-gui
```

---

## 🧪 Test Each Module Individually

### CAN Bus Test:

```bash
sudo ip link set can0 up type can bitrate 500000
candump can0
```

### GPS Test:

```bash
cgps -s
```

### MPU-6050 Test:

Run test script from `mpu6050` Python package.

---

## 📸 (Optional) Camera Integration

* Use Pi Camera or USB webcam
* Stream with OpenCV or `ffmpeg`
* Embed in Pygame display with OpenCV frame conversion

---

## 📍 Track Mode – GPS Checkpoints

1. Ride a lap and record GPS coordinates
2. Define a start/finish zone (rectangle or circle)
3. Add manual checkpoints for splits
4. Lap timer logic triggers when crossing zones in sequence

---

## 🧼 Maintenance

* Reboot Pi occasionally
* Check CAN connector integrity regularly
* Backup lap data and logs as needed

---

Happy racing! 🏁
