import asyncio
from sensors.can_reader import CANReader
from sensors.imu_reader import IMUReader
from sensors.gps_reader import GPSReader
from config import CONFIG
from storage import sqlite_logger

class DataAcquisition:
    def __init__(self):
        self.can_reader = CANReader(
            channel=CONFIG["can_interface"],
            bitrate=CONFIG["can_bitrate"],
            rpm_id=CONFIG["can_rpm_id"],
            speed_id=CONFIG["can_speed_id"],
            gear_id=CONFIG["can_gear_id"]
        )
        self.imu_reader = IMUReader(address=CONFIG["mpu_address"])
        self.gps_reader = GPSReader(device=CONFIG["gps_device"])
        self.data = {
            'can': {},
            'imu': {},
            'gps': {}
        }
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

    async def start(self):
        self._stop_event.clear()
        await asyncio.gather(
            self._can_loop(),
            self._imu_loop(),
            self._gps_loop(),
            self._log_loop()
        )

    def stop(self):
        self._stop_event.set()
        self.gps_reader.stop()

    def get_all_data(self):
        """
        Returns the latest combined data from CAN, IMU, and GPS as a dictionary.
        """
        return self.data.copy()

# Example usage:
# import asyncio
# daq = DataAcquisition()
# asyncio.create_task(daq.start())
# ...
# print(daq.get_all_data())
# daq.stop()