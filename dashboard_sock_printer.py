import socket
import os

SOCKET_PATH = "/tmp/dashboard.sock"

if os.path.exists(SOCKET_PATH):
    os.remove(SOCKET_PATH)

sock = socket.socket(socket.AF_UNIX, socket.SOCK_DGRAM)
sock.bind(SOCKET_PATH)  # Bind directly to /tmp/dashboard.sock

print(f"Listening for messages on {SOCKET_PATH}...")

while True:
    data, _ = sock.recvfrom(1024)
    print(data.decode())