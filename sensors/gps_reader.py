import threading
import time
from typing import Optional, Dict

class GPSReader:
    """
    Generic GPS reader for Raspberry Pi. Uses 'gpsd' via the 'gps' library if available, but can be extended for other modules.
    """
    def __init__(self, device: str = '/dev/serial0'):
        self.device = device
        try:
            import gps
            self.gps = gps
            self.session = gps.gps(mode=gps.WATCH_ENABLE)
            self.backend = 'gpsd'
        except ImportError:
            self.gps = None
            self.session = None
            self.backend = None
            # Could add other backends here (e.g., serial, pynmea2, etc.)
        self.data = {'lat': None, 'lon': None, 'alt': None, 'speed': None, 'fix_time': None}
        self._stop_event = threading.Event()
        self._thread = threading.Thread(target=self._update_loop, daemon=True)
        self._thread.start()

    def _update_loop(self):
        while not self._stop_event.is_set():
            if self.backend == 'gpsd' and self.session:
                try:
                    report = self.session.next()
                    if report['class'] == 'TPV':
                        self.data['lat'] = getattr(report, 'lat', None)
                        self.data['lon'] = getattr(report, 'lon', None)
                        self.data['alt'] = getattr(report, 'alt', None)
                        self.data['speed'] = getattr(report, 'speed', None)
                        self.data['fix_time'] = getattr(report, 'time', None)
                except Exception:
                    pass
            time.sleep(0.5)

    def get_gps_data(self) -> Dict[str, Optional[float]]:
        """
        Returns the latest GPS data as a dictionary: lat, lon, alt, speed, fix_time.
        If no data is available, values will be None.
        """
        return self.data.copy()

    def stop(self):
        self._stop_event.set()
        self._thread.join()

# Example usage:
# gps_reader = GPSReader()
# time.sleep(2)  # Wait for initial data
# print(gps_reader.get_gps_data())
# gps_reader.stop()