import pygame
import random
from scripts.projectiles import RedShuriken
from scripts.tilemap import Tilemap

class PhysicsEntity:
    def __init__(self, game, e_type, pos, size, health=100):
        self.game = game
        self.type = e_type
        self.pos = list(pos)
        self.size = size
        self.velocity = [0, 0]
        self.collisions = {'up': False, 'down': False, 'left': False, 'right': False}
        self.health = health
        self.max_health = health
        self.action = ''
        self.anim_offset = (0, 0)
        self.flip = False
        self.set_action('idle')
    
    def rect(self):
        return pygame.Rect(self.pos[0], self.pos[1], self.size[0], self.size[1])
    
    def set_action(self, action):
        if action != self.action:
            self.action = action
            self.animation = self.game.assets[self.type + '/' + self.action].copy()

    def update(self, tilemap, movement=(0,0)):
        self.collisions = {'up': False, 'down': False, 'left': False, 'right': False}

        frame_movement = [movement[0] + self.velocity[0], movement[1] + self.velocity[1]]

        self.pos[0] += frame_movement[0]
        entity_rect = self.rect()
        for rect in tilemap.physics_rects_around(self.pos):
            if entity_rect.colliderect(rect):
                if frame_movement[0] > 0:
                    entity_rect.right = rect.left
                    self.collisions['right'] = True
                if frame_movement[0] < 0:
                    entity_rect.left = rect.right
                    self.collisions['left'] = True
                self.pos[0] = entity_rect.x

        self.pos[1] += frame_movement[1]
        entity_rect = self.rect()
        for rect in tilemap.physics_rects_around(self.pos):
            if entity_rect.colliderect(rect):
                if frame_movement[1] > 0:
                    entity_rect.bottom = rect.top
                    self.collisions['down'] = True
                if frame_movement[1] < 0:
                    entity_rect.top = rect.bottom
                    self.collisions['up'] = True
                self.pos[1] = entity_rect.y
        
        if movement[0] > 0:
            self.flip = False
        if movement[0] < 0:
            self.flip = True

        if self.action != 'climb':
            self.velocity[1] = min(5, self.velocity[1] + 0.1) # gravity

        if self.collisions['down'] or self.collisions['up']:
            self.velocity[1] = 0
    
        self.animation.update()
    
    def render(self, surf, offset=(0,0)):
        surf.blit(pygame.transform.flip(self.animation.img(), self.flip, False), (self.pos[0] - offset[0] + self.anim_offset[0], self.pos[1] - offset[1] + self.anim_offset[1]))
        self.draw_health_bar(surf, offset)
    
    def draw_health_bar(self, surf, offset):
        if self.health < self.max_health:
            health_bar_width = self.size[0]
            health_bar_height = 4
            health_ratio = self.health / self.max_health
            pygame.draw.rect(surf, (255, 0, 0), (self.pos[0] - offset[0], self.pos[1] - offset[1] - 6, health_bar_width, health_bar_height))
            pygame.draw.rect(surf, (0, 255, 0), (self.pos[0] - offset[0], self.pos[1] - offset[1] - 6, health_bar_width * health_ratio, health_bar_height))

class Player(PhysicsEntity):
    def __init__(self, game, pos, size):
        super().__init__(game, 'player', pos, size)
        self.air_time = 0
    
    def update(self, tilemap, movement=(0,0)):

        super().update(tilemap, movement=movement)

        # handles climbing
        entity_rect = self.rect()
        for ladder in tilemap.ladders_around(self.pos):
            if entity_rect.colliderect(ladder):
                if self.action != 'climb':
                    self.velocity[1] = 0
                    self.set_action('climb')
                return

        self.air_time += 1
        if self.collisions['down']:
            self.air_time = 0
        
        if self.air_time > 4 and self.action != 'climb':
            self.set_action('jump')
        elif movement[0] != 0:
            self.set_action('run')
        else:
           self.set_action('idle')
    
    def take_damage(self, damage):
        self.health -= damage
        if self.health <= 0:
            self.health = 0  # Ensure health doesn't go below 0
            # Handle player death here (e.g., restart level, end game, etc.)
    
    # Override the render method and add custom offset for player sprite
    def render(self, surf, offset=(0,0)):
        surf.blit(pygame.transform.flip(self.animation.img(), self.flip, False), (self.pos[0] - offset[0] + self.anim_offset[0] - 5, self.pos[1] - offset[1] + self.anim_offset[1]))


class Enemy(PhysicsEntity):
    def __init__(self, game, pos, size, health=50):
        super().__init__(game, 'enemy', pos, size, health=health)
        self.set_action('idle')
        self.knockback = pygame.Vector2(0, 0)  # Initialize knockback vector
        self.dodge_cooldown = 0  # Cooldown for dodging
        self.attack_cooldown = 0  # Cooldown for attacking
        self.jump_cooldown = 0  # Cooldown for jumping
    
    def apply_knockback(self, knockback):
        self.knockback = knockback  # Apply knockback
    
    def take_damage(self, damage):
        self.health -= damage
        if self.health <= 0:
            self.game.enemies.remove(self)
    
    def check_ledge(self, tilemap):
        entity_rect = self.rect()
        if len(tilemap.physics_rects_around(self.pos)) < 3:
            return True  # There is a ledge
    
    def update(self, tilemap, movement=(0, 0)):
        if self.check_ledge(tilemap):
            movement = (0, 0)  # Stop movement if there's a ledge
            return
        
        player_pos = self.game.player.pos
        if player_pos[0] > self.pos[0]:
            movement = (1, 0)  # Move right
        elif player_pos[0] < self.pos[0]:
            movement = (-1, 0)  # Move left

        # Apply knockback to movement
        if self.knockback.length() > 0:
            movement = (movement[0] + self.knockback.x, movement[1] + self.knockback.y)
            self.knockback *= 0.9  # Dampen knockback over time
            if self.knockback.length() < 0.1:
                self.knockback = pygame.Vector2(0, 0)  # Stop knockback if it's very small

        super().update(tilemap, movement=movement)

    def render(self, surf, offset=(0, 0)):
        surf.blit(pygame.transform.flip(self.animation.img(), self.flip, False), 
                  (self.pos[0] - offset[0] + self.anim_offset[0] - 5, self.pos[1] - offset[1] + self.anim_offset[1]))
        self.draw_health_bar(surf, offset)
