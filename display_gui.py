import pygame
from config import CONFIG
from display.rpm_bar import draw_rpm_bar
from display.speed_display import draw_speed_display
from display.gear_indicator import draw_gear_indicator
import socket
import json
import threading
import os

pygame.init()
screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
clock = pygame.time.Clock()
font = pygame.font.SysFont(None, 36)

show_fps = CONFIG.get("show_fps", True)
target_fps = CONFIG.get("display_fps", 60)

# Set up Unix socket for receiving data
SOCKET_PATH = "/tmp/dashboard.sock"
if os.path.exists(SOCKET_PATH):
    os.remove(SOCKET_PATH)

sock = socket.socket(socket.AF_UNIX, socket.SOCK_DGRAM)
try:
    sock.bind(SOCKET_PATH)
except OSError:
    # If already bound, try to remove and re-bind
    os.remove(SOCKET_PATH)
    sock.bind(SOCKET_PATH)

# Shared data for live updates
live_data = {"rpm": 0, "speed": 0, "gear": 1}

def socket_listener():
    while True:
        try:
            data, _ = sock.recvfrom(1024)
            msg = json.loads(data.decode())
            # Update only if keys exist
            for k in ("rpm", "speed", "gear"):
                if k in msg:
                    live_data[k] = msg[k]
        except Exception:
            continue

# Start socket listener in a background thread
threading.Thread(target=socket_listener, daemon=True).start()

running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
            running = False

    screen.fill((0, 0, 0))

    # Draw live sensor data
    draw_rpm_bar(screen, live_data["rpm"])
    draw_speed_display(screen, live_data["speed"])
    draw_gear_indicator(screen, live_data["gear"])

    if show_fps:
        fps = int(clock.get_fps())
        fps_text = font.render(f"FPS: {fps}", True, (0, 255, 0))
        screen.blit(fps_text, (20, 20))

    pygame.display.flip()
    clock.tick(target_fps)

pygame.quit()