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

    def read_can_data(self, timeout=0.1):
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
        # Send data to the forwarder (which binds to /tmp/dashboard.sock)
        while not self._stop_event.is_set():
            try:
                msg = json.dumps({
                    "rpm": self.data['can'].get('rpm', 0),
                    "speed": self.data['can'].get('speed', 0),
                    "gear": self.data['can'].get('gear', 1),
                    "lean_angle": self.data['imu'].get('lean_angle', 0.0),
                    "gps_lat": self.data['gps'].get('lat'),
                    "gps_lon": self.data['gps'].get('lon'),
                    "timestamp": time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
                })
                try:
                    # Always create a new socket for each sendto
                    with socket.socket(socket.AF_UNIX, socket.SOCK_DGRAM) as s:
                        s.connect(self.socket_path)
                        s.send(msg.encode())
                except Exception as e:
                    print(f"Failed to send to dashboard.sock: {e}")
            except Exception as e:
                print(f"Failed to broadcast data: {e}")
            await asyncio.sleep(interval)

    async def _forwarder_loop(self, interval=0.1):
        """
        Forward all messages received on /tmp/dashboard.sock to /tmp/dashboard_display.sock and /tmp/dashboard_debug.sock (if enabled).
        Only send to a destination if its socket file exists.
        """
        SRC = "/tmp/dashboard.sock"
        DESTS = ["/tmp/dashboard_display.sock"]
        if CONFIG.get("debug_socket_enabled", True):
            DESTS.append("/tmp/dashboard_debug.sock")
        import os
        if os.path.exists(SRC):
            os.remove(SRC)
        src_sock = socket.socket(socket.AF_UNIX, socket.SOCK_DGRAM)
        try:
            src_sock.bind(SRC)
        except OSError:
            os.remove(SRC)
            src_sock.bind(SRC)
        src_sock.setblocking(True)  # Blocking mode for thread executor
        print(f"Forwarder running: {SRC} -> {DESTS}")
        loop = asyncio.get_running_loop()
        while not self._stop_event.is_set():
            try:
                # Use run_in_executor to avoid blocking the event loop
                data, addr = await loop.run_in_executor(None, src_sock.recvfrom, 1024)
                for dest in DESTS:
                    if os.path.exists(dest):
                        try:
                            with socket.socket(socket.AF_UNIX, socket.SOCK_DGRAM) as out:
                                out.connect(dest)
                                out.send(data)
                        except Exception as e:
                            print(f"Forwarder failed to send to {dest}: {e}")
                    else:
                        print(f"Forwarder: destination socket {dest} does not exist, skipping.")
            except Exception as e:
                print(f"Forwarder error: {e}")

    async def start(self):
        self._stop_event.clear()
        # Start the forwarder loop first to ensure /tmp/dashboard.sock is bound
        forwarder_task = asyncio.create_task(self._forwarder_loop())
        # Wait a short moment to ensure the forwarder is ready
        await asyncio.sleep(0.2)
        await asyncio.gather(
            self._can_loop(),
            self._imu_loop(),
            self._gps_loop(),
            self._log_loop(),
            self._broadcast_loop(),
            forwarder_task
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