import pygame
import pygame.gfxdraw 
import os
import math  # Import math module for rotation calculations
from scripts.entities import Enemy, Boss

class UI:
    def __init__(self, game):
        self.game = game
        self.font = pygame.font.SysFont(None, 24)  # Use the default Pygame font with size 24

        # Load the shuriken image
        self.shuriken_image = pygame.image.load('graphics/animations_spritesheet/player/projectiles/shuriken/0.png').convert_alpha()

        # Load the enemy and boss images
        # self.enemy_image = pygame.image.load('graphics/animations_spritesheet/enemy/0.png').convert_alpha()
        # self.boss_image = pygame.image.load('graphics/animations_spritesheet/boss/0.png').convert_alpha()

        # Start time to track when the game starts
        self.start_time = pygame.time.get_ticks()
        
        # Durations in seconds
        self.display_duration = 5  # Time to display the control guide before starting to fade out
        self.fade_duration = 5  # Duration of the fade-out effect

    def render(self, surf):
        self.render_player_health_bar(surf)
        self.render_shuriken_cooldown(surf)
        # self.render_control_guide(surf)
        # self.render_enemy_counter(surf)
        # self.render_boss_counter(surf)

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

    def render_shuriken_cooldown(self, surf):
        player = self.game.player
        cooldown_time = player.shuriken_cooldown / 60  # Convert frames to seconds (assuming 60 FPS)
        max_cooldown = 1.0  # 1 second cooldown

        # Position the shuriken cooldown UI to the right of the health bar
        health_bar_x = 10
        health_bar_width = 100
        center = (health_bar_x + health_bar_width + 10, 15)  # Adjust the y-position if needed
        radius = 6  # Radius of the circle

        if player.shuriken_cooldown > 0:
            # Create a surface with per-pixel alpha
            cooldown_surface = pygame.Surface((radius * 2, radius * 2), pygame.SRCALPHA)

            # Draw the dark grey circle background with alpha
            pygame.draw.circle(cooldown_surface, (250, 250, 250, 0), (radius, radius), radius)  # Alpha set to 0 (transparent)

            # Calculate the filled angle
            filled_angle = (cooldown_time / max_cooldown) * 2 * math.pi

            # Draw the filled arc as a polygon (a pie shape)
            points = [(radius, radius)]  # Start at the center of the circle
            points.extend([
                (radius + radius * math.cos(math.pi * 1.5 + angle),
                radius + radius * math.sin(math.pi * 1.5 + angle))
                for angle in [filled_angle * i / 20 for i in range(21)]
            ])

            # Ensure the polygon correctly closes the segment
            if filled_angle < 2 * math.pi:
                points.append((radius, radius))
            
            if player.shuriken_cooldown > 2:
                pygame.draw.polygon(cooldown_surface, (30, 30, 30, 150), points)

                # Blit the cooldown surface onto the main surface
                surf.blit(cooldown_surface, (center[0] - radius, center[1] - radius))

                # Draw the shuriken image in the center
                shuriken_rect = self.shuriken_image.get_rect(center=center)
                surf.blit(self.shuriken_image, shuriken_rect)
            else:
                shuriken_rect = self.shuriken_image.get_rect(center=center)
                surf.blit(self.shuriken_image, shuriken_rect)

    # def render_control_guide(self, surf):
    #     # Example control guide rendering
    #     guide_text = "Press W to jump, A/D to move, and SPACE to attack"
    #     guide_surface = self.font.render(guide_text, True, (255, 255, 255))
    #     surf.blit(guide_surface, (10, 50))

    # def render_enemy_counter(self, surf):
    #     # Example enemy counter rendering
    #     enemy_count = len(self.game.enemies)
    #     enemy_text = f"Enemies: {enemy_count}"
    #     enemy_surface = self.font.render(enemy_text, True, (255, 255, 255))
    #     surf.blit(enemy_surface, (10, 70))
    #     surf.blit(self.enemy_image, (120, 70))

    # def render_boss_counter(self, surf):
    #     # Example boss counter rendering
    #     boss_count = len(self.game.bosses)
    #     boss_text = f"Bosses: {boss_count}"
    #     boss_surface = self.font.render(boss_text, True, (255, 255, 255))
    #     surf.blit(boss_surface, (10, 90))
    #     surf.blit(self.boss_image, (120, 90))
