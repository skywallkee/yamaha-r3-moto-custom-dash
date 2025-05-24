import pygame

def draw_speed_display(screen, speed, pos=(50, 180), font_size=72):
    """
    Draws the speed value on the screen.
    :param screen: pygame surface
    :param speed: current speed value
    :param pos: (x, y) position
    :param font_size: font size for display
    """
    font = pygame.font.SysFont(None, font_size, bold=True)
    text = font.render(f"{speed} km/h", True, (0, 200, 255))
    screen.blit(text, pos)
