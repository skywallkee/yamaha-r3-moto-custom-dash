import pygame

def draw_gear_indicator(screen, gear, pos=(700, 100), size=80):
    """
    Draws the gear indicator on the screen.
    :param screen: pygame surface
    :param gear: current gear value (int or str)
    :param pos: (x, y) position
    :param size: diameter of the indicator
    """
    x, y = pos
    pygame.draw.circle(screen, (30, 30, 30), (x, y), size // 2)
    font = pygame.font.SysFont(None, size, bold=True)
    text = font.render(str(gear), True, (255, 255, 0))
    text_rect = text.get_rect(center=(x, y))
    screen.blit(text, text_rect)
