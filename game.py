import pygame
import sys
import random
import math
from scripts.entities import PhysicsEntity, Player, Enemy
from scripts.utils import *
from scripts.tilemap import Tilemap
from scripts.clouds import Clouds
from scripts.particle import Particle
from scripts.projectiles import Projectile, Shuriken
from scripts.ui import UI

class Game:
    def __init__(self):
        pygame.init()

        pygame.display.set_caption("Ninja Platformer")
        self.screen = pygame.display.set_mode((640, 480))
        self.display = pygame.Surface((320, 240))

        self.clock = pygame.time.Clock()

        self.movement = [False, False]

        self.assets = {
            'grass': load_images('spritesheet_images/grass'),
            'player': load_images('animations_spritesheet/player'),
            'exclamation': load_image('spritesheet_images/exclamation.png'),
            'player/idle': Animation(load_images('animations_spritesheet/player/idle'), img_dur=10),
            'player/jump': Animation(load_images('animations_spritesheet/player/jump')),
            'player/run': Animation(load_images('animations_spritesheet/player/run'), img_dur=8),
            'player/climb': Animation(load_images('animations_spritesheet/player/climb'), img_dur=10),
            'enemy': load_images('animations_spritesheet/enemy'),
            'enemy/idle': Animation(load_images('animations_spritesheet/enemy/idle'), img_dur=10),
            'enemy/run': Animation(load_images('animations_spritesheet/enemy/run'), img_dur=8),
            'background': load_image('spritesheet_images/sky/0.png'),
            'decor': load_images('spritesheet_images/decor'),
            'tree': load_images('spritesheet_images/tree'),
            'ladder': load_images('spritesheet_images/ladder'),
            'clouds': load_images('spritesheet_images/cloud'),
            'projectiles/shuriken': Animation(load_images('animations_spritesheet/player/projectiles/shuriken'), img_dur=3),
            'projectiles/red_shuriken': Animation(load_images('animations_spritesheet/enemy/projectiles/red_shuriken'), img_dur=3),
            'particle/leaf': Animation(load_images('animations_spritesheet/particles/leaf'), img_dur=20, loop=False),
        }
 
        self.clouds = Clouds(load_images('spritesheet_images/cloud'), count=16)

        self.tilemap = Tilemap(self, tile_size=16)
        self.tilemap.load('level1')

        self.player = Player(self, (self.tilemap.player_position[0]*self.tilemap.tile_size, self.tilemap.player_position[1]*self.tilemap.tile_size), (6, 16))

        self.enemies = []
        for pos in self.tilemap.enemy_positions:
            self.enemies.append(Enemy(self, (pos[0]*self.tilemap.tile_size, pos[1]*self.tilemap.tile_size), (6, 16)))

        # Leaf spawners for particles
        self.leaf_spawners = []
        for tree in self.tilemap.extract([('tree', 0), ('tree', 1)], keep=True):
            self.leaf_spawners.append(pygame.Rect(tree['pos'][0], tree['pos'][1], 23, 13))

        self.ladders = []
        for ladder in self.tilemap.extract([('ladder', 0)], keep=True):
            self.ladders.append(pygame.Rect(ladder['pos'][0], ladder['pos'][1], 16, 16))

        # particles
        self.particles = []

        # projectiles
        self.projectiles = []

        self.scroll = [self.tilemap.player_position[0]*self.tilemap.tile_size, self.tilemap.player_position[1]*self.tilemap.tile_size]

        # Initialize the UI
        self.ui = UI(self)

    def run(self):
        while True:
            self.display.blit(self.assets['background'], (0, 0))

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
                if particle.type == 'leaf':
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
                    if event.key == pygame.K_SPACE:
                        if self.player.flip:
                            self.projectiles.append(Shuriken(self, self.player.rect().center, velocity=[-2, 0]))
                        else:
                            self.projectiles.append(Shuriken(self, self.player.rect().center, velocity=[2, 0]))
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

Game().run()
