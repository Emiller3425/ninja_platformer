import pygame

class UI:
    def __init__(self, game):
        self.game = game
        self.font = pygame.font.SysFont(None, 24)  # Use the default Pygame font with size 24

    def render(self, surf):
        self.render_player_health_bar(surf)

    def update(self):
        pass

    def render_player_health_bar(self, surf):
        player = self.game.player
        health_bar_width = 100
        health_bar_height = 10
        health_ratio = player.health / player.max_health
        pygame.draw.rect(surf, (255, 0, 0), (10, 10, health_bar_width, health_bar_height))
        pygame.draw.rect(surf, (0, 255, 0), (10, 10, health_bar_width * health_ratio, health_bar_height))
