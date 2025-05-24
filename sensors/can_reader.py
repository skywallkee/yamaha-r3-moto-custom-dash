import can
from typing import Dict, Optional

class CANReader:
    def __init__(self, channel: str = 'can0', bustype: str = 'socketcan', bitrate: int = 500000,
                 rpm_id: int = 0x100, speed_id: int = 0x101, gear_id: int = 0x102):
        """
        Initialize CAN bus interface. Default values provided, can be overridden on init.
        CAN IDs can be passed as arguments.
        """
        self.bus = can.interface.Bus(channel=channel, bustype=bustype, bitrate=bitrate)
        self.RPM_CAN_ID = rpm_id
        self.SPEED_CAN_ID = speed_id
        self.GEAR_CAN_ID = gear_id

    def read_can_data(self, timeout: float = 1.0) -> Dict[str, Optional[int]]:
        """
        Reads CAN messages for RPM, Speed, and GEAR. Returns a dictionary with the latest values.
        Timeout is in seconds.
        """
        result = {'rpm': None, 'speed': None, 'gear': None}

        end_time = can.util.time.time() + timeout
        
        while can.util.time.time() < end_time:
            msg = self.bus.recv(timeout=0.1)
            if msg is None:
                continue
            if msg.arbitration_id == self.RPM_CAN_ID:
                # Example: RPM is in bytes 0-1, big endian
                result['rpm'] = int.from_bytes(msg.data[0:2], byteorder='big')
            elif msg.arbitration_id == self.SPEED_CAN_ID:
                # Example: Speed is in byte 0
                result['speed'] = msg.data[0]
            elif msg.arbitration_id == self.GEAR_CAN_ID:
                # Example: Gear is in byte 0
                result['gear'] = msg.data[0]
            # If all values are read, break early
            if all(v is not None for v in result.values()):
                break
        return result

# Example usage:
# can_reader = CANReader()
# data = can_reader.read_can_data()
# print(data)  # {'rpm': 1234, 'speed': 56, 'gear': 3}