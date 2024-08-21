# /// script
# dependencies = [
#  "pytmx",
# ]
# ///
import pygame
import sys
import random
import math
from scripts.entities import PhysicsEntity, Player, Enemy, Boss
from scripts.utils import *
from scripts.tilemap import Tilemap
from scripts.clouds import Clouds
from scripts.particle import Particle, SkullParticle
from scripts.projectiles import Projectile, Shuriken
from scripts.ui import UI
import asyncio


class Game:
    def __init__(self):
        pygame.init()
        pygame.mixer.init()

        pygame.display.set_caption("Ninja Platformer")
        self.screen = pygame.display.set_mode((640, 480))
        self.display = pygame.Surface((320, 240))

        self.clock = pygame.time.Clock()
        self.show_start_screen = True
        self.show_level_selector = False
        self.current_level = None
        self.is_paused = False  # New attribute to track if the game is paused
        self.levels = {
            'level1': {'completed': False, 'tilemap': 'level1', 'background': 'background1'},
            'level2': {'completed': False, 'tilemap': 'level2', 'background': 'background2'},
            'level3': {'completed': False, 'tilemap': 'level3', 'background': 'background3'}
        }

        self.movement = [False, False]

        self.assets = {
            'grass': load_images('spritesheet_images/grass'),
            'player': load_images('animations_spritesheet/player'),
            'exclamation': load_image('spritesheet_images/exclamation.png'),
            'skull': load_image('spritesheet_images/skull.png'),
            'player/idle': Animation(load_images('animations_spritesheet/player/idle'), img_dur=10),
            'player/jump': Animation(load_images('animations_spritesheet/player/jump')),
            'player/run': Animation(load_images('animations_spritesheet/player/run'), img_dur=8),
            'player/climb': Animation(load_images('animations_spritesheet/player/climb'), img_dur=10),
            'enemy': load_images('animations_spritesheet/enemy'),
            'enemy/idle': Animation(load_images('animations_spritesheet/enemy/idle'), img_dur=10),
            'enemy/run': Animation(load_images('animations_spritesheet/enemy/run'), img_dur=8),
            'background1': load_image('spritesheet_images/sky/0.png'),
            'background2': load_image('spritesheet_images/sky/1.png'),
            'background3': load_image('spritesheet_images/sky/2.png'),
            'decor': load_images('spritesheet_images/decor'),
            'tree': load_images('spritesheet_images/tree'),
            'ladder': load_images('spritesheet_images/ladder'),
            'clouds': load_images('spritesheet_images/cloud'),
            'projectiles/shuriken': Animation(load_images('animations_spritesheet/player/projectiles/shuriken'), img_dur=3),
            'projectiles/red_shuriken': Animation(load_images('animations_spritesheet/enemy/projectiles/red_shuriken'), img_dur=3),
            'particle/leaf': Animation(load_images('animations_spritesheet/particles/leaf'), img_dur=20, loop=False),
            'boss': load_images('animations_spritesheet/boss'),
            'boss/idle': Animation(load_images('animations_spritesheet/boss/idle'), img_dur=10),
            'boss/run': Animation(load_images('animations_spritesheet/boss/run'), img_dur=6),
            'checkmark': load_image('spritesheet_images/checkmark.png'),  # Load the checkmark image
        }

        self.audio = {
            'climbing': pygame.mixer.Sound('audio/climbing.ogg'),
            'death': pygame.mixer.Sound('audio/death.ogg'),
            'shuriken_throw': pygame.mixer.Sound('audio/shuriken_throw.ogg'),
            'damage': pygame.mixer.Sound('audio/damage.ogg'),
            'walking': pygame.mixer.Sound('audio/walking.ogg'),
            'beat': pygame.mixer.Sound('audio/beat.ogg'),
        }

        self.music = {
            'beat': pygame.mixer.Sound('audio/beat.ogg'),
        }

        self.clouds = Clouds(load_images('spritesheet_images/cloud'), count=16)

        # Initialize the UI
        self.ui = UI(self)

    def load_level(self, level_name):
        self.tilemap = Tilemap(self, tile_size=16)
        self.tilemap.load(self.levels[level_name]['tilemap'])

        self.player = Player(self, (self.tilemap.player_position[0] * self.tilemap.tile_size, self.tilemap.player_position[1] * self.tilemap.tile_size), (6, 16))

        self.enemies = []
        for pos in self.tilemap.enemy_positions:
            self.enemies.append(Enemy(self, (pos[0] * self.tilemap.tile_size, pos[1] * self.tilemap.tile_size), (6, 16)))

        for pos in self.tilemap.boss_positions:
            self.enemies.append(Boss(self, (pos[0] * self.tilemap.tile_size,
                                        pos[1] * self.tilemap.tile_size),  # offset boss to be on the ground
                                        (14, 31)))

        self.leaf_spawners = []
        for tree in self.tilemap.extract([('tree', 0), ('tree', 1)], keep=True):
            self.leaf_spawners.append(pygame.Rect(tree['pos'][0], tree['pos'][1], 23, 13))

        self.ladders = []
        for ladder in self.tilemap.extract([('ladder', 0)], keep=True):
            self.ladders.append(pygame.Rect(ladder['pos'][0], ladder['pos'][1], 16, 16))

        self.particles = []
        self.projectiles = []
        self.scroll = [self.tilemap.player_position[0] * self.tilemap.tile_size, self.tilemap.player_position[1] * self.tilemap.tile_size]

        # Set the current background based on the level
        self.current_background = self.assets[self.levels[level_name]['background']]

    async def iris_out_and_reset(self):
        max_radius = max(self.screen.get_width(), self.screen.get_height())
        radius = max_radius
        screen_center = (self.display.get_width() // 2, self.display.get_height() // 2)

        while (radius > 0):
            self.display.blit(self.current_background, (0, 0))
            render_scroll = (int(self.scroll[0]), int(self.scroll[1]))

            # Render everything
            self.tilemap.render(self.display, offset=render_scroll)
            self.player.render(self.display, offset=render_scroll)

            for enemy in self.enemies:
                enemy.render(self.display, offset=render_scroll)

            for particle in self.particles.copy():
                particle.render(self.display, offset=render_scroll)

            for projectile in self.projectiles.copy():
                projectile.render(self.display, offset=render_scroll)

            # Render UI
            self.ui.render(self.display)

            # Draw the iris-out effect
            surface = pygame.Surface(self.display.get_size())
            surface.fill((0, 0, 0))
            pygame.draw.circle(surface, (255, 255, 255), screen_center, radius)
            surface.set_colorkey((255, 255, 255))
            self.display.blit(surface, (0, 0))

            radius -= 12    # Increase the decrement to make the effect go faster

            self.screen.blit(pygame.transform.scale(self.display, self.screen.get_size()), (0, 0))
            pygame.display.update()
            self.clock.tick(60)

            await asyncio.sleep(0)

        # Reset the level
        self.load_level(self.current_level)

    async def run(self):
        while True:
            if (self.show_start_screen):
                self.music['beat'].stop()
                self.show_start_screen_screen()
            elif (self.show_level_selector):
                self.music['beat'].stop()
                self.show_level_selector_screen()
            elif (self.player.dead):
                self.music['beat'].stop()
                await self.iris_out_and_reset()
            elif self.is_paused:
                self.music['beat'].stop()
                self.show_pause_menu()
            else:
                self.music['beat'].set_volume(0.3)
                self.music['beat'].play(-1)
                self.main()
            await asyncio.sleep(0)
       
    def show_start_screen_screen(self):
        self.screen.fill((0, 0, 0))
        font = pygame.font.SysFont(None, 74)
        title_text = font.render("Ninja Platformer", True, (255, 255, 255))
        self.screen.blit(title_text, (self.screen.get_width() // 2 - title_text.get_width() // 2, 100))

        start_font = pygame.font.SysFont(None, 48)
        start_text = start_font.render("Click to Start", True, (255, 255, 255))
        self.screen.blit(start_text, (self.screen.get_width() // 2 - start_text.get_width() // 2, 300))

        pygame.display.update()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                self.show_start_screen = False
                self.show_level_selector = True

    def show_level_selector_screen(self):
        self.screen.fill((0, 0, 0))
        font = pygame.font.SysFont(None, 48)
        title_text = font.render("Select Level", True, (255, 255, 255))
        self.screen.blit(title_text, (self.screen.get_width() // 2 - title_text.get_width() // 2, 50))

        level_buttons = [
            ("Level 1", 1),
            ("Level 2", 2),
            ("Level 3", 3)
        ]

        for idx, (level_name, level_num) in enumerate(level_buttons):
            if level_num == 1 or self.levels[f'level{level_num-1}']['completed']:
                color = (255, 255, 255)
            else:
                color = (100, 100, 100)

            level_text = font.render(level_name, True, color)
            rect = level_text.get_rect(center=(self.screen.get_width() // 2, 150 + idx * 100))
            self.screen.blit(level_text, rect)

            # Draw the green checkmark if the level is completed
            if self.levels[f'level{level_num}']['completed']:
                checkmark_pos = (rect.right + 20, rect.centery - 5)  # Position the checkmark to the right of the level text
                self.screen.blit(self.assets['checkmark'], checkmark_pos)

        pygame.display.update()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                for idx, (level_name, level_num) in enumerate(level_buttons):
                    if level_num == 1 or self.levels[f'level{level_num-1}']['completed']:
                        rect = pygame.Rect(self.screen.get_width() // 2 - 100, 150 + idx * 100 - 20, 200, 40)
                        if rect.collidepoint(event.pos):
                            self.load_level(f'level{level_num}')
                            self.current_level = f'level{level_num}'
                            self.show_level_selector = False

    def show_pause_menu(self):
        # Dim the background
        self.movement = [False, False]
        overlay = pygame.Surface(self.screen.get_size())
        overlay.fill((150, 150, 150))
        overlay.set_alpha(2)  # Transparency level (0 = fully transparent, 255 = fully opaque)
        self.screen.blit(overlay, (0, 0))

        # Calculate the position and size of the pause menu
        menu_width = self.screen.get_width() // 2
        menu_height = self.screen.get_height() // 2
        menu_x = (self.screen.get_width() - menu_width) // 2
        menu_y = (self.screen.get_height() - menu_height) // 2

        # Draw the white menu background with a black border
        menu_rect = pygame.Rect(menu_x, menu_y, menu_width, menu_height)
        pygame.draw.rect(self.screen, (255, 255, 255), menu_rect)  # White background
        pygame.draw.rect(self.screen, (0, 0, 0), menu_rect, 5)  # Black border with thickness 5

        # Render the "Paused" text
        font = pygame.font.SysFont(None, 74)
        pause_text = font.render("Paused", True, (0, 0, 0))
        pause_text_rect = pause_text.get_rect(center=(menu_rect.centerx, menu_rect.y + 50))
        self.screen.blit(pause_text, pause_text_rect)

        # Draw the "Resume" and "Return to Menu" options
        option_font = pygame.font.SysFont(None, 48)
        resume_text = option_font.render("Resume", True, (0, 0, 0))
        menu_text = option_font.render("Main Menu", True, (0, 0, 0))

        resume_rect = resume_text.get_rect(center=(menu_rect.centerx, menu_rect.centery))
        menu_rect_text = menu_text.get_rect(center=(menu_rect.centerx, menu_rect.centery + 60))

        self.screen.blit(resume_text, resume_rect)
        self.screen.blit(menu_text, menu_rect_text)

        pygame.display.update()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.is_paused = False  # Unpause the game
            if event.type == pygame.MOUSEBUTTONDOWN:
                if resume_rect.collidepoint(event.pos):
                    self.is_paused = False  # Unpause the game
                elif menu_rect_text.collidepoint(event.pos):
                    self.show_level_selector = True
                    self.is_paused = False  # Go back to the level selector


    def check_level_completion(self):
        if not any(isinstance(enemy, (Enemy, Boss)) for enemy in self.enemies):
            self.levels[self.current_level]['completed'] = True
            self.movement = [False, False]
            self.show_level_selector = True
            self.current_level = None

    def main(self):

        self.display.blit(self.current_background, (0, 0))
        self.audio['shuriken_throw'].set_volume(0.5)

        self.scroll[0] += (self.player.rect().centerx - self.display.get_width() / 2 - self.scroll[0]) / 30
        self.scroll[1] += (self.player.rect().centery - self.display.get_height() / 2 - self.scroll[1]) / 30
        render_scroll = (int(self.scroll[0]), int(self.scroll[1]))

        # Create leaf particles
        for rect in self.leaf_spawners:
            if random.random() * 49999 < rect.width * rect.height:
                pos = (rect.x + random.random() * rect.width, rect.y + random.random() * rect.height)
                self.particles.append(Particle(self, 'leaf', pos, velocity=[-0.15, 0.3], frame=random.randint(0, 10)))

        # Update and render clouds
        self.clouds.update()
        self.clouds.render(self.display, offset=render_scroll)

        # Render tilemap
        self.tilemap.render(self.display, offset=render_scroll)

        # Update and render player
        self.player.update(self.tilemap, (self.movement[1] - self.movement[0], 0))
        self.player.render(self.display, offset=render_scroll)

        for enemy in self.enemies:
            enemy.update(self.tilemap)
            enemy.render(self.display, offset=render_scroll)

        # animate and render particles
        for particle in self.particles.copy():
            kill = particle.update()
            particle.render(self.display, offset=render_scroll)
            if isinstance(particle, Particle) and particle.type == 'leaf':
                particle.pos[0] += math.sin(particle.animation_frame * 0.035) * 0.3
                particle.pos[1] += math.sin(particle.animation_frame * 0.035) * 0.3
            if kill:
                self.particles.remove(particle)

        # animate and render projectiles
        for projectile in self.projectiles.copy():
            kill = projectile.update()
            projectile.render(self.display, offset=render_scroll)
            if kill:
                self.projectiles.remove(projectile)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT:
                    self.movement[0] = True
                if event.key == pygame.K_RIGHT:
                    self.movement[1] = True
                if event.key == pygame.K_UP:
                    if self.player.action == 'climb':
                        self.player.velocity[1] = -1
                    elif event.key == pygame.K_UP and self.player.action != 'jump':
                        self.player.velocity[1] = -3
                if event.key == pygame.K_DOWN:
                    if self.player.action == 'climb':
                        self.player.velocity[1] = 1
                if event.key == pygame.K_SPACE and self.player.shuriken_cooldown == 0:
                    if self.player.flip:
                        self.projectiles.append(Shuriken(self, self.player.rect().center, velocity=[-2, 0]))
                        self.player.throw_shuriken()
                    else:
                        self.projectiles.append(Shuriken(self, self.player.rect().center, velocity=[2, 0]))
                        self.player.throw_shuriken()
                if event.key == pygame.K_ESCAPE:
                    self.is_paused = not self.is_paused  # Toggle pause state

            if event.type == pygame.KEYUP:
                if event.key == pygame.K_LEFT:
                    self.movement[0] = False
                if event.key == pygame.K_RIGHT:
                    self.movement[1] = False
                if (event.key == pygame.K_UP or event.key == pygame.K_DOWN) and self.player.action == 'climb':
                    self.player.velocity[1] = 0

        # Handles climbing without additional key events for when the player is jumping up or falling down towards a ladder and holding keys down
        self.keys = pygame.key.get_pressed()
        if self.keys[pygame.K_UP] and self.player.action == 'climb':
            self.player.velocity[1] = -1
        if self.keys[pygame.K_DOWN] and self.player.action == 'climb':
            self.player.velocity[1] = 1

        # Render the UI
        self.ui.render(self.display)

        self.screen.blit(pygame.transform.scale(self.display, self.screen.get_size()), (0, 0))
        pygame.display.update()
        self.clock.tick(60)

        self.check_level_completion()

asyncio.run(Game().run())
