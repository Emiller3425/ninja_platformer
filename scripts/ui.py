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

        # # Load the control guide images
        # self.arrow_keys_image = pygame.image.load('graphics/spritesheet_images/arrow_keys.png').convert_alpha()
        # self.space_bar_image = pygame.image.load('graphics/spritesheet_images/space_bar.png').convert_alpha()

        # Start time to track when the game starts
        self.start_time = pygame.time.get_ticks()
        
        # Durations in seconds
        self.display_duration = 5  # Time to display the control guide before starting to fade out
        self.fade_duration = 5  # Duration of the fade-out effect

    def render(self, surf):
        self.render_player_health_bar(surf)
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

    # def render_control_guide(self, surf):
    #     current_time = pygame.time.get_ticks()
    #     elapsed_time = (current_time - self.start_time) / 1000  # Convert milliseconds to seconds

    #     if elapsed_time <= self.display_duration + self.fade_duration:
    #         # Calculate the alpha (transparency) based on the elapsed time for fade-out effect
    #         if elapsed_time <= self.display_duration:
    #             alpha = 255  # Fully opaque
    #         else:
    #             fade_elapsed_time = elapsed_time - self.display_duration
    #             alpha = max(0, 255 - int(255 * (fade_elapsed_time / self.fade_duration)))

    #         # Create a surface to hold the control guide with alpha support
    #         control_guide_surf = pygame.Surface(surf.get_size(), pygame.SRCALPHA)
    #         control_guide_surf.fill((0, 0, 0, 0))  # Fill with transparent color

    #         # Set the alpha value
    #         arrow_keys_img = self.arrow_keys_image.copy()
    #         arrow_keys_img.set_alpha(alpha)
    #         space_bar_img = self.space_bar_image.copy()
    #         space_bar_img.set_alpha(alpha)

    #         # Define positions
    #         arrow_keys_pos = (surf.get_width() // 2 - arrow_keys_img.get_width() // 2, surf.get_height() // 2 - 60)
    #         space_bar_pos = (surf.get_width() // 2 - space_bar_img.get_width() // 2, surf.get_height() // 2 + 10)

    #         # Render text
    #         move_text = self.font.render("Move", True, (255, 255, 255))
    #         attack_text = self.font.render("Attack", True, (255, 255, 255))
    #         move_text.set_alpha(alpha)
    #         attack_text.set_alpha(alpha)

    #         # Blit images and text onto the control guide surface
    #         control_guide_surf.blit(arrow_keys_img, arrow_keys_pos)
    #         control_guide_surf.blit(space_bar_img, space_bar_pos)
    #         control_guide_surf.blit(move_text, (arrow_keys_pos[0] + arrow_keys_img.get_width() // 2 - move_text.get_width() // 2, arrow_keys_pos[1] - 30))
    #         control_guide_surf.blit(attack_text, (space_bar_pos[0] + space_bar_img.get_width() // 2 - attack_text.get_width() // 2, space_bar_pos[1] + space_bar_img.get_height() + 10))

    #         # Blit the control guide surface onto the main surface
    #         surf.blit(control_guide_surf, (0, 0))

    # def render_enemy_counter(self, surf):
    #     enemy_count = sum(isinstance(enemy, Enemy) for enemy in self.game.enemies)
    #     text = self.font.render(f"x {enemy_count}", True, (255, 255, 255))
    #     surf.blit(self.enemy_image, (10, 30))
    #     surf.blit(text, (40, 30))

    # def render_boss_counter(self, surf):
    #     boss_count = sum(isinstance(enemy, Boss) for enemy in self.game.enemies)
    #     text = self.font.render(f"x {boss_count}", True, (255, 255, 255))
    #     surf.blit(self.boss_image, (10, 60))
    #     surf.blit(text, (40, 60))
