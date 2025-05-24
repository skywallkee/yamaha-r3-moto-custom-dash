import asyncio
import socket
import json
import time
import random
from sensors.can_reader import CANReader
from sensors.imu_reader import IMUReader
from sensors.gps_reader import GPSReader
from config import CONFIG
from storage import sqlite_logger

class MockCANReader:
    def __init__(self):
        self.rpm = 8000
        self.speed = 100
        self.gear = 3
        self.rpm_direction = 1
        self.speed_direction = 1
        self.last_update = time.time()
        self.next_update = self.last_update + random.uniform(0.1, 1.0)

    def read_can_data(self, timeout=1.0):
        now = time.time()
        if now >= self.next_update:
            # RPM oscillates between 4000 and 12000
            if self.rpm >= 12000:
                self.rpm_direction = -1
            elif self.rpm <= 4000:
                self.rpm_direction = 1
            self.rpm += 1000 * self.rpm_direction

            # Speed oscillates between 0 and 200
            if self.speed >= 200:
                self.speed_direction = -1
            elif self.speed <= 0:
                self.speed_direction = 1
            self.speed += 10 * self.speed_direction

            # Gear cycles 1-6
            self.gear = self.gear + 1 if self.gear < 6 else 1
            self.last_update = now
            self.next_update = now + random.uniform(0.1, 1.0)
        return {
            'rpm': self.rpm,
            'speed': self.speed,
            'gear': self.gear
        }

class MockIMUReader:
    def get_accel_data(self):
        return {'x': 0.0, 'y': 0.0, 'z': 9.8}
    def get_gyro_data(self):
        return {'x': 0.0, 'y': 0.0, 'z': 0.0}
    def get_lean_angle(self):
        return 0.0
    def get_all_data(self):
        return {
            'lean_angle': self.get_lean_angle(),
            'acceleration': self.get_accel_data(),
            'gyroscope': self.get_gyro_data()
        }

class DataAcquisition:
    def __init__(self):
        if CONFIG.get("can_enabled", True):
            self.can_reader = CANReader(
                channel=CONFIG["can_interface"],
                bitrate=CONFIG["can_bitrate"],
                rpm_id=CONFIG["can_rpm_id"],
                speed_id=CONFIG["can_speed_id"],
                gear_id=CONFIG["can_gear_id"]
            )
        else:
            self.can_reader = MockCANReader()
        if CONFIG.get("imu_enabled", True):
            self.imu_reader = IMUReader(address=CONFIG["mpu_address"])
        else:
            self.imu_reader = MockIMUReader()
        self.gps_reader = GPSReader(device=CONFIG["gps_device"])
        self.data = {
            'can': {},
            'imu': {},
            'gps': {}
        }
        self.sock = socket.socket(socket.AF_UNIX, socket.SOCK_DGRAM)
        self.socket_path = "/tmp/dashboard.sock"
        self._stop_event = asyncio.Event()

    async def _can_loop(self, interval=None):
        interval = interval or CONFIG["can_poll_interval_ms"] / 1000.0
        while not self._stop_event.is_set():
            self.data['can'] = self.can_reader.read_can_data(timeout=interval/2)
            await asyncio.sleep(interval)

    async def _imu_loop(self, interval=None):
        interval = interval or CONFIG["imu_poll_interval_ms"] / 1000.0
        while not self._stop_event.is_set():
            self.data['imu'] = self.imu_reader.get_all_data()
            await asyncio.sleep(interval)

    async def _gps_loop(self, interval=None):
        interval = interval or CONFIG["gps_poll_interval_ms"] / 1000.0
        while not self._stop_event.is_set():
            self.data['gps'] = self.gps_reader.get_gps_data()
            await asyncio.sleep(interval)

    async def _log_loop(self, interval=1.0):
        while not self._stop_event.is_set():
            if not CONFIG.get("logging_enabled", True):
                await asyncio.sleep(interval)
                continue
            can = self.data['can']
            imu = self.data['imu']
            # Log only if we have meaningful data
            if all(k in can for k in ('rpm', 'speed', 'gear')) and 'lean_angle' in imu:
                await asyncio.to_thread(
                    sqlite_logger.log_sensor_data,
                    can.get('rpm'),
                    can.get('speed'),
                    can.get('gear'),
                    imu.get('lean_angle')
                )
            gps = self.data['gps']
            # Optionally log GPS points if you have a lap_id (add logic as needed)
            # await asyncio.to_thread(sqlite_logger.log_gps_point, lap_id, timestamp, gps.get('lat'), gps.get('lon'))
            await asyncio.sleep(interval)

    async def _broadcast_loop(self, interval=0.1):
        while not self._stop_event.is_set():
            try:
                msg = json.dumps({
                    "rpm": self.data['can'].get('rpm', 0),
                    "speed": self.data['can'].get('speed', 0),
                    "gear": self.data['can'].get('gear', 1)
                })
                self.sock.sendto(msg.encode(), self.socket_path)
            except Exception:
                pass
            await asyncio.sleep(interval)

    async def start(self):
        self._stop_event.clear()
        await asyncio.gather(
            self._can_loop(),
            self._imu_loop(),
            self._gps_loop(),
            self._log_loop(),
            self._broadcast_loop()  # Add broadcast loop
        )

    def stop(self):
        self._stop_event.set()
        self.gps_reader.stop()

    def get_all_data(self):
        """
        Returns the latest combined data from CAN, IMU, and GPS as a dictionary.
        """
        return self.data.copy()


if __name__ == "__main__":
    daq = DataAcquisition()
    asyncio.run(daq.start())