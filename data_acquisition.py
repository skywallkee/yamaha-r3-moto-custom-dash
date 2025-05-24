import asyncio
from sensors.can_reader import CANReader
from sensors.imu_reader import IMUReader
from sensors.gps_reader import GPSReader

class DataAcquisition:
    def __init__(self):
        self.can_reader = CANReader()
        self.imu_reader = IMUReader()
        self.gps_reader = GPSReader()
        self.data = {
            'can': {},
            'imu': {},
            'gps': {}
        }
        self._stop_event = asyncio.Event()

    async def _can_loop(self, interval=0.1):
        while not self._stop_event.is_set():
            self.data['can'] = self.can_reader.read_can_data(timeout=0.05)
            await asyncio.sleep(interval)

    async def _imu_loop(self, interval=0.1):
        while not self._stop_event.is_set():
            self.data['imu'] = self.imu_reader.get_all_data()
            await asyncio.sleep(interval)

    async def _gps_loop(self, interval=0.5):
        while not self._stop_event.is_set():
            self.data['gps'] = self.gps_reader.get_gps_data()
            await asyncio.sleep(interval)

    async def start(self):
        self._stop_event.clear()
        await asyncio.gather(
            self._can_loop(),
            self._imu_loop(),
            self._gps_loop()
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