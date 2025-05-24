import pygame
from config import CONFIG

pygame.init()
screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
clock = pygame.time.Clock()
font = pygame.font.SysFont(None, 36)

show_fps = CONFIG.get("show_fps", True)
target_fps = CONFIG.get("display_fps", 60)

running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
            running = False

    screen.fill((0, 0, 0))

    if show_fps:
        fps = int(clock.get_fps())
        fps_text = font.render(f"FPS: {fps}", True, (0, 255, 0))
        screen.blit(fps_text, (20, 20))

    pygame.display.flip()
    clock.tick(target_fps)

pygame.quit()