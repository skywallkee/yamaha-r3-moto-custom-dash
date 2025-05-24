from mpu6050 import mpu6050
import math

class IMUReader:
    def __init__(self, address=0x68):
        self.sensor = mpu6050(address)

    def get_accel_data(self):
        return self.sensor.get_accel_data()

    def get_gyro_data(self):
        return self.sensor.get_gyro_data()

    def get_lean_angle(self):
        accel = self.get_accel_data()
        # Calculate lean angle (roll) in degrees
        x = accel['x']
        y = accel['y']
        z = accel['z']
        # Prevent division by zero
        z = z if z != 0 else 0.0001  # Avoid division by zero

        # Roll angle calculation
        roll = math.atan2(y, z) * 180 / math.pi
        return roll

    def get_all_data(self):
        accel = self.get_accel_data()
        gyro = self.get_gyro_data()
        lean_angle = self.get_lean_angle()
        return {
            'lean_angle': lean_angle,
            'acceleration': accel,
            'gyroscope': gyro
        }

# Example usage:
# imu = IMUReader()
# data = imu.get_all_data()
# print(f"Lean Angle: {data['lean_angle']:.2f} degrees")
# print(f"Acceleration: {data['acceleration']}")
# print(f"Gyroscope: {data['gyroscope']}")