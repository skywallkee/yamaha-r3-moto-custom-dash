CONFIG = {
    # CAN bus settings
    "can_interface": "can0",
    "can_bitrate": 500000,
    "can_rpm_id": 0x100,
    "can_speed_id": 0x101,
    "can_gear_id": 0x102,
    "can_poll_interval_ms": 200,
    "can_enabled": False,  # Disable CAN for WSL/dev

    # IMU (MPU6050) settings
    "mpu_address": 0x68,
    "imu_poll_interval_ms": 200,
    "imu_enabled": False,  # Disable IMU for WSL/dev

    # GPS settings
    "gps_device": "/dev/serial0",
    "gps_poll_interval_ms": 1000,

    # Logging settings
    "logging_enabled": True,
}