import pygame
from config_settings import *
import random

class Enemy(pygame.sprite.Sprite):
    """
    Enemy class representing hostile entities in the game.
    
    The Enemy class handles all aspects of enemy behavior including movement,
    animations, collisions, and combat. Enemies will pursue the player and can be
    damaged by player attacks.
    
    Attributes:
        game (Game): Reference to the main game instance
        _layer (int): Rendering layer for sprite groups
        groups (tuple): Sprite groups this enemy belongs to
        x (int): Current x position in pixels
        y (int): Current y position in pixels
        width (int): Enemy width in pixels
        height (int): Enemy height in pixels
        x_change (float): Current horizontal movement
        y_change (float): Current vertical movement
        health (int): Current health points
        facing (str): Current facing direction ('left' or 'right')
        animation_loop (int): Current frame in animation sequence
        last_update (int): Timestamp of last animation update
    """

    def __init__(self, game, x, y):
        """
        Initialize a new enemy instance.
        
        Args:
            game (Game): Reference to the main game instance
            x (int): Starting x-coordinate in tile units
            y (int): Starting y-coordinate in tile units
            
        The enemy is initialized with default health, random facing direction,
        and loads its sprite animations from the sprite sheet.
        """
        self.game = game
        self._layer = ENEMY_LAYER
        self.groups = self.game.allsprites, self.game.enemies
        pygame.sprite.Sprite.__init__(self, self.groups)

        # Position and dimensions
        self.x = x * TILESIZE
        self.y = y * TILESIZE
        self.width = TILESIZE
        self.height = TILESIZE

        # Movement variables
        self.x_change = 0
        self.y_change = 0

        # Combat attributes
        self.health = ENEMY_HEALTH

        # Animation attributes
        self.facing = random.choice(['left', 'right'])
        self.animation_loop = 1
        self.last_update = pygame.time.get_ticks()

        # Load and set up sprites
        self.sprite_sheet = pygame.image.load('LEGEND OF ZAHIR/skeleton_strip.png')
        self.load_animations()
        
        # Set up initial image and rect
        self.image = self.game.enemy_spritesheet.get_sprite(1, 0, 15, 15) 
        self.rect = self.image.get_rect()
        self.rect.x = self.x
        self.rect.y = self.y   

        # Initialize animation dictionaries
        self.animations = {
            'down': [self.game.enemy_spritesheet.get_sprite(0, 0, 16, 16),
                    self.game.enemy_spritesheet.get_sprite(16, 0, 16, 16),
                    self.game.enemy_spritesheet.get_sprite(32, 0, 16, 16)],
            
            'up': [self.game.enemy_spritesheet.get_sprite(0, 16, 16, 16),
                self.game.enemy_spritesheet.get_sprite(16, 16, 16, 16),
                self.game.enemy_spritesheet.get_sprite(32, 16, 16, 16)],
            
            'left': [self.game.enemy_spritesheet.get_sprite(0, 32, 16, 16),
                    self.game.enemy_spritesheet.get_sprite(16, 34, 16, 16),
                    self.game.enemy_spritesheet.get_sprite(32, 34, 16, 16)],
            
            'right': [self.game.enemy_spritesheet.get_sprite(0, 48, 16, 16),
                    self.game.enemy_spritesheet.get_sprite(16, 50, 16, 16),
                    self.game.enemy_spritesheet.get_sprite(32, 50, 16, 16)]
        }
        # Scale initial image
        self.img = self.animations['down'][0]  
        self.image = pygame.transform.scale(self.img, (TILESIZE, TILESIZE))
        
        # Scale all animation frames
        for direction in self.animations:
            self.animations[direction] = [
                pygame.transform.scale(img, (TILESIZE, TILESIZE)) 
                for img in self.animations[direction]
            ]

    def load_animations(self):
        """
        Load animation frames from the sprite sheet.
        
        Divides the sprite sheet into individual frames and creates
        separate animation sequences for left and right facing directions.
        Each frame is scaled to match the tile size.
        """
        self.animations = {
            'down':[],
            'up':[],
            'left': [], 
            'right': [],
        }
        
        sprite_width = self.sprite_sheet.get_width() // 3
        sprite_height = self.sprite_sheet.get_height() // 4

        for row, direction in enumerate(['down','up','left', 'right']):
            for col in range(3):
                x = col * sprite_width
                y = row * sprite_height
                sprite = self.sprite_sheet.subsurface(pygame.Rect(x, y, sprite_width, sprite_height))
                scaled_sprite = pygame.transform.scale(sprite, (TILESIZE, TILESIZE))
                self.animations[direction].append(scaled_sprite)

    def update(self):
        """
        Update the enemy's state for the current frame.
        
        Handles movement, collisions, animations, and combat checks.
        This method is called every frame while the enemy exists.
        """
        self.movement()
        self.check_collisions()
        self.animate()
        self.check_bullet_collision()

    def movement(self):
        """
        Calculate and apply enemy movement towards the player.
        
        Uses simple path finding to move towards the player's current position.
        Movement speed is normalized so diagonal movement isn't faster.
        Updates facing direction based on movement.
        """
        dx = self.game.player.rect.x - self.rect.x
        dy = self.game.player.rect.y - self.rect.y
        dist = max(abs(dx), abs(dy))
        
        if dist != 0:
            self.x_change = (dx / dist) * ENEMY_SPEED
            self.y_change = (dy / dist) * ENEMY_SPEED
        else:
            self.x_change = 0
            self.y_change = 0

        # Update facing direction
        if self.y_change > 0:
            self.facing = 'up'
        elif self.y_change < 0:
            self.facing = 'down'
        elif self.x_change > 0:
            self.facing = 'right'
        elif self.x_change < 0:
            self.facing = 'left'

    def check_collisions(self):
        """
        Check and handle collisions with blocks in the game world.
        
        Performs separate checks for horizontal and vertical movement
        to allow sliding along walls. Updates position only if no
        collision would occur.
        """
        # Horizontal collision check
        self.rect.x += self.x_change
        x_collision = pygame.sprite.spritecollide(self, self.game.blocks, False)
        if x_collision:
            if self.x_change > 0:
                self.rect.right = x_collision[0].rect.left
            elif self.x_change < 0:
                self.rect.left = x_collision[0].rect.right
            self.x_change = 0

        # Vertical collision check
        self.rect.y += self.y_change
        y_collision = pygame.sprite.spritecollide(self, self.game.blocks, False)
        if y_collision:
            if self.y_change > 0:
                self.rect.bottom = y_collision[0].rect.top
            elif self.y_change < 0:
                self.rect.top = y_collision[0].rect.bottom
            self.y_change = 0

    def check_bullet_collision(self):
        """
        Check for collisions with player bullets and handle damage.
        
        If a bullet hits the enemy, it takes damage based on the
        player's attack power and grants experience points if defeated.
        """
        bullet_hits = pygame.sprite.spritecollide(self, self.game.bullets, True)
        for bullet in bullet_hits:
            self.take_damage(self.game.player.attack_power)

    def take_damage(self, amount):
        """
        Handle the enemy taking damage and potentially being defeated.
        
        Args:
            amount (int): Amount of damage to apply to the enemy
            
        If health reaches zero, the enemy is removed and rewards are given
        to the player.
        """
        self.health -= amount
        if self.health <= 0:
            self.kill()

    @classmethod
    def create_random(cls, game):
        map_height = len(TILEMAP)
        map_width = len(TILEMAP[0])
        min_distance = 5
        
        # Explicitly set boundaries to avoid wall tiles
        left_bound = 1
        right_bound = map_width - 2
        top_bound = 1
        bottom_bound = map_height - 2
        
        # Debug print
        print(f"Spawn boundaries: {left_bound}-{right_bound} x {top_bound}-{bottom_bound}")
        
        valid_positions = []
        for y in range(top_bound, bottom_bound + 1):
            for x in range(left_bound, right_bound + 1):
                # Extra validation to ensure position is within map
                if not (0 <= x < map_width and 0 <= y < map_height):
                    continue
                    
                if TILEMAP[y][x] not in [".", "E", "P"]:
                    continue
                    
                # Get player position in tile coordinates
                player_tile_x = game.player.rect.x // TILESIZE
                player_tile_y = game.player.rect.y // TILESIZE
                
                # Calculate distance from player
                dx = x - player_tile_x
                dy = y - player_tile_y
                distance = (dx * dx + dy * dy) ** 0.5
                
                if distance < min_distance:
                    continue
                    
                # Verify the position is clear
                temp_rect = pygame.Rect(x * TILESIZE, y * TILESIZE, TILESIZE, TILESIZE)
                collision = any(sprite.rect.colliderect(temp_rect) for sprite in game.allsprites)
                
                if not collision:
                    valid_positions.append((x, y))
        
        if not valid_positions:
            raise ValueError("No valid positions found for enemy spawn")
            
        # Print chosen position for debugging
        x, y = random.choice(valid_positions)
        print(f"Spawning enemy at tile position: {x},{y}")
        
        return cls(game, x, y)

    def animate(self):
        """
        Handle the enemy's animation state and frame updates.
        
        Updates the animation frame every 200ms and handles
        idle animations when the enemy is not moving.
        """
        now = pygame.time.get_ticks()
        if now - self.last_update > 200:  # Animation frame rate
            self.last_update = now
            self.animation_loop = (self.animation_loop + 1) % len(self.animations[self.facing])
            self.image = self.animations[self.facing][self.animation_loop]
            self.rect = self.image.get_rect(center=self.rect.center)

        # Reset to idle frame when not moving
        if self.x_change == 0 and self.y_change == 0:
            self.image = self.animations[self.facing][0]
            self.rect = self.image.get_rect(center=self.rect.center)