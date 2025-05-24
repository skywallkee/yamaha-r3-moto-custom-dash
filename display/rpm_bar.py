import pygame

def draw_rpm_bar(screen, rpm, max_rpm=16000, pos=(50, 100), size=(600, 40)):
    """
    Draws an RPM bar on the screen.
    :param screen: pygame surface
    :param rpm: current RPM value
    :param max_rpm: maximum RPM value
    :param pos: (x, y) position
    :param size: (width, height)
    """
    x, y = pos
    width, height = size
    # Draw background
    pygame.draw.rect(screen, (50, 50, 50), (x, y, width, height), border_radius=8)
    # Calculate fill
    fill_width = int(width * min(rpm / max_rpm, 1.0))
    # Color changes as RPM increases
    if rpm < max_rpm * 0.7:
        color = (0, 200, 0)
    elif rpm < max_rpm * 0.9:
        color = (255, 200, 0)
    else:
        color = (255, 0, 0)
    pygame.draw.rect(screen, color, (x, y, fill_width, height), border_radius=8)
    # Draw RPM text
    font = pygame.font.SysFont(None, 32)
    text = font.render(f"RPM: {rpm}", True, (255, 255, 255))
    screen.blit(text, (x + width + 20, y))
