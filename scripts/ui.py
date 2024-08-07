import pygame
import os
from scripts.entities import Enemy, Boss  # Add this line to import Enemy and Boss classes

class UI:
    def __init__(self, game):
        self.game = game
        self.font = pygame.font.SysFont(None, 24)  # Use the default Pygame font with size 24

        # Load the enemy and boss images
        self.enemy_image = pygame.image.load('graphics/animations_spritesheet/enemy/0.png').convert_alpha()
        self.boss_image = pygame.image.load('graphics/animations_spritesheet/boss/0.png').convert_alpha()

    def render(self, surf):
        self.render_player_health_bar(surf)
        self.render_enemy_counter(surf)
        self.render_boss_counter(surf)

    def update(self):
        pass

    def render_player_health_bar(self, surf):
        player = self.game.player
        health_bar_width = 100
        health_bar_height = 10
        health_ratio = player.health / player.max_health
        health_bar_x = 10
        health_bar_y = 10

        # Draw the black border rectangle
        border_thickness = 2
        pygame.draw.rect(surf, (0, 0, 0), (health_bar_x - border_thickness, health_bar_y - border_thickness, health_bar_width + 2 * border_thickness, health_bar_height + 2 * border_thickness))

        # Draw the red background rectangle
        pygame.draw.rect(surf, (255, 0, 0), (health_bar_x, health_bar_y, health_bar_width, health_bar_height))

        # Draw the green health bar
        pygame.draw.rect(surf, (0, 255, 0), (health_bar_x, health_bar_y, health_bar_width * health_ratio, health_bar_height))

    def render_enemy_counter(self, surf):
        enemy_count = sum(isinstance(enemy, Enemy) for enemy in self.game.enemies)
        text = self.font.render(f"x {enemy_count}", True, (255, 255, 255))
        surf.blit(self.enemy_image, (10, 30))
        surf.blit(text, (40, 30))

    def render_boss_counter(self, surf):
        boss_count = sum(isinstance(enemy, Boss) for enemy in self.game.enemies)
        text = self.font.render(f"x {boss_count}", True, (255, 255, 255))
        surf.blit(self.boss_image, (10, 60))
        surf.blit(text, (40, 60))
