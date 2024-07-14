import pygame
import random
from scripts.projectiles import RedShuriken
from scripts.tilemap import Tilemap

# Base class for all entities that have physics properties
class PhysicsEntity:
    def __init__(self, game, e_type, pos, size, health=100):
        self.game = game  # Reference to the game instance
        self.type = e_type  # Type of the entity (e.g., player, enemy)
        self.pos = list(pos)  # Position of the entity
        self.size = size  # Size of the entity
        self.velocity = [0, 0]  # Velocity of the entity
        self.collisions = {'up': False, 'down': False, 'left': False, 'right': False}  # Collision flags
        self.health = health  # Current health of the entity
        self.max_health = health  # Maximum health of the entity
        self.action = ''  # Current action/animation of the entity
        self.anim_offset = (0, 0)  # Offset for the animation
        self.flip = False  # Flag for flipping the sprite horizontally
        self.set_action('idle')  # Set the initial action to 'idle'
    
    # Get the rectangle representing the entity's position and size
    def rect(self):
        return pygame.Rect(self.pos[0], self.pos[1], self.size[0], self.size[1])
    
    # Set the current action/animation of the entity
    def set_action(self, action):
        if action != self.action:
            self.action = action
            self.animation = self.game.assets[self.type + '/' + self.action].copy()

    # Update the entity's position and handle collisions
    def update(self, tilemap, movement=(0,0)):
        self.collisions = {'up': False, 'down': False, 'left': False, 'right': False}  # Reset collision flags
        frame_movement = [movement[0] + self.velocity[0], movement[1] + self.velocity[1]]  # Calculate frame movement

        if self.velocity[0] != 0:  # Dampen horizontal velocity over time
            self.velocity[0] *= 0.9

        # Update horizontal position and check for collisions
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

        # Update vertical position and check for collisions
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
        
        # Update flip flag based on movement direction
        if movement[0] > 0:
            self.flip = False
        if movement[0] < 0:
            self.flip = True

        # Apply gravity if not climbing
        if self.action != 'climb':
            self.velocity[1] = min(5, self.velocity[1] + 0.1)

        # Reset vertical velocity on collision with ground or ceiling
        if self.collisions['down'] or self.collisions['up']:
            self.velocity[1] = 0
    
        self.animation.update()  # Update animation
    
    # Render the entity on the screen
    def render(self, surf, offset=(0,0)):
        surf.blit(pygame.transform.flip(self.animation.img(), self.flip, False), 
                  (self.pos[0] - offset[0] + self.anim_offset[0], 
                   self.pos[1] - offset[1] + self.anim_offset[1]))
        self.draw_health_bar(surf, offset)  # Draw health bar
    
    # Draw the health bar above the entity
    def draw_health_bar(self, surf, offset):
        if self.health < self.max_health:
            health_bar_width = self.size[0]
            health_bar_height = 4
            health_ratio = self.health / self.max_health
            pygame.draw.rect(surf, (255, 0, 0), 
                             (self.pos[0] - offset[0], self.pos[1] - offset[1] - 6, 
                              health_bar_width, health_bar_height))
            pygame.draw.rect(surf, (0, 255, 0), 
                             (self.pos[0] - offset[0], self.pos[1] - offset[1] - 6, 
                              health_bar_width * health_ratio, health_bar_height))

# Class for the player character, inherits from PhysicsEntity
class Player(PhysicsEntity):
    def __init__(self, game, pos, size):
        super().__init__(game, 'player', pos, size)
        self.air_time = 0  # Time the player has been in the air
    
    def update(self, tilemap, movement=(0,0)):
        super().update(tilemap, movement=movement)  # Update position and handle collisions

        # Handle climbing
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
        
        # Set appropriate action based on state
        if self.air_time > 4 and self.action != 'climb':
            self.set_action('jump')
        elif movement[0] != 0:
            self.set_action('run')
        else:
           self.set_action('idle')
    
    # Handle taking damage and apply knockback
    def take_damage(self, damage, knockback):
        self.health -= damage
        self.velocity = [knockback[0], knockback[1]]
        if self.health <= 0:
            self.health = 0  # Ensure health doesn't go below 0
            # Handle player death here (e.g., restart level, end game, etc.)
    
    # Override the render method and add custom offset for player sprite
    def render(self, surf, offset=(0,0)):
        surf.blit(pygame.transform.flip(self.animation.img(), self.flip, False), 
                  (self.pos[0] - offset[0] + self.anim_offset[0] - 5, 
                   self.pos[1] - offset[1] + self.anim_offset[1]))

# Class for enemy characters, inherits from PhysicsEntity
class Enemy(PhysicsEntity):
    def __init__(self, game, pos, size, health=50):
        super().__init__(game, 'enemy', pos, size, health=health)
        self.set_action('idle')  # Set initial action to 'idle'
        self.knockback = pygame.Vector2(0, 0)  # Initialize knockback vector
        self.dodge_cooldown = 0  # Cooldown for dodging
        self.attack_cooldown = 0  # Cooldown for attacking
        self.jump_cooldown = 0  # Cooldown for jumping
    
    def apply_knockback(self, knockback):
        self.knockback = knockback  # Apply knockback
    
    def take_damage(self, damage):
        self.health -= damage
        if self.health <= 0:
            self.game.enemies.remove(self)  # Remove enemy if health drops to 0
    
    def update(self, tilemap, movement=(0, 0)):
        # Move towards the player
        player_pos = self.game.player.pos
        if player_pos[0] > self.pos[0]:
            movement = (0.5, 0)  # Move right
        elif player_pos[0] < self.pos[0]:
            movement = (-0.5, 0)  # Move left

        # Apply knockback to movement
        if self.knockback.length() > 0:
            movement = (movement[0] + self.knockback.x, movement[1] + self.knockback.y)
            self.knockback *= 0.9  # Dampen knockback over time
            if self.knockback.length() < 0.1:
                self.knockback = pygame.Vector2(0, 0)  # Stop knockback if it's very small
                
        next_pos = [self.pos[0] + movement[0], self.pos[1] + self.size[1]]
        on_ground = False
        for rect in tilemap.physics_rects_around(next_pos):
            if pygame.Rect(next_pos[0], next_pos[1], self.size[0], 1).colliderect(rect):
                on_ground = True
                break

        # Prevent movement in the direction of the ledge
        if not on_ground and self.knockback == (0, 0):
            movement = (0, movement[1]) if movement[0] != 0 else movement

        # Check for collision with the player
        if self.rect().colliderect(self.game.player.rect()):
            knockback = [movement[0] * 6, -1]  # Set knockback vector
            self.game.player.take_damage(5, knockback)  # Apply damage and knockback to the player
            if movement[0] > 0:  # Enemy moving right
                self.pos[0] = self.game.player.rect().left - self.size[0]
            else:  # Enemy moving left
                self.pos[0] = self.game.player.rect().right

        super().update(tilemap, movement=movement)  # Update position and handle collisions

        if movement[0] != 0:
            self.set_action('run')
        elif movement[1] != 0:
            self.set_action('idle')
        else:
            self.set_action('idle')

    def render(self, surf, offset=(0, 0)):
        surf.blit(pygame.transform.flip(self.animation.img(), self.flip, False), 
                  (self.pos[0] - offset[0] + self.anim_offset[0] - 5, 
                   self.pos[1] - offset[1] + self.anim_offset[1]))
        self.draw_health_bar(surf, offset)  # Draw health bar
