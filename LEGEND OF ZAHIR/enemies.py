import pygame
from config_settings import *
import random

class Enemy(pygame.sprite.Sprite):
    """
    Represents an enemy in the game.

    This class handles the enemy's movement, animation, collision detection,
    and interaction with the player and game environment.
    """

    def __init__(self, game, x, y):
        """
        Initialize the enemy.

        Args:
            game (Game): The main game object.
            x (int): The x-coordinate of the enemy's starting position in tiles.
            y (int): The y-coordinate of the enemy's starting position in tiles.
        """
        self.game = game
        self._layer = ENEMY_LAYER
        self.groups = self.game.all_sprites, self.game.enemies
        pygame.sprite.Sprite.__init__(self, self.groups)

        self.x = x * TILESIZE
        self.y = y * TILESIZE
        self.width = TILESIZE
        self.height = TILESIZE

        self.x_change = 0
        self.y_change = 0

        self.health = ENEMY_HEALTH

        self.facing = random.choice(['left', 'right'])
        self.animation_loop = 1
        self.last_update = pygame.time.get_ticks()

        self.sprite_sheet = pygame.image.load('skeleton_strip.png')
        self.load_animations()
        
        self.image = self.game.enemy_spritesheet.get_sprite(1, 0, 15, 15) 
        self.rect = self.image.get_rect()
        self.rect.x = self.x
        self.rect.y = self.y   

        self.animations = {
            'left': [self.game.enemy_spritesheet.get_sprite(1, 0, 15, 15)],
            'right': [self.game.enemy_spritesheet.get_sprite(1, 0, 15, 15)]
        }
        
        self.img = self.animations['right'][0]  
        self.image = pygame.transform.scale(self.img, (TILESIZE, TILESIZE))
        
        for direction in self.animations:
            self.animations[direction] = [pygame.transform.scale(img, (TILESIZE, TILESIZE)) 
                for img in self.animations[direction]]

    def load_animations(self):
        """
        Load and prepare animation frames from the sprite sheet.
        """
        self.animations = {
            'left': [], 'right': []
        }
        
        sprite_width = self.sprite_sheet.get_width() // 3
        sprite_height = self.sprite_sheet.get_height() // 4

        for row, direction in enumerate(['left', 'right']):
            for col in range(3):
                x = col * sprite_width
                y = row * sprite_height
                sprite = self.sprite_sheet.subsurface(pygame.Rect(x, y, sprite_width, sprite_height))
                scaled_sprite = pygame.transform.scale(sprite, (TILESIZE, TILESIZE))
                self.animations[direction].append(scaled_sprite)

    def update(self):
        """
        Update the enemy's state each frame.
        """
        self.movement()
        self.check_collisions()
        self.animate()
        self.check_bullet_collision()

    def movement(self):
        """
        Calculate and set the enemy's movement towards the player.
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

        if self.x_change > 0:
            self.facing = 'right'
        elif self.x_change < 0:
            self.facing = 'left'

    def check_collisions(self):
        """
        Check for collisions with blocks and adjust position accordingly.
        """
        self.rect.x += self.x_change
        x_collision = pygame.sprite.spritecollide(self, self.game.blocks, False)
        if x_collision:
            if self.x_change > 0:
                self.rect.right = x_collision[0].rect.left
            elif self.x_change < 0:
                self.rect.left = x_collision[0].rect.right
            self.x_change = 0

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
        Check for collisions with player bullets and take damage if hit.
        """
        bullet_hits = pygame.sprite.spritecollide(self, self.game.bullets, True)
        for bullet in bullet_hits:
            self.take_damage(self.game.player.attack_power)

    def take_damage(self, amount):
        """
        Reduce the enemy's health and handle defeat if health reaches zero.

        Args:
            amount (int): The amount of damage to be dealt to the enemy.
        """
        self.health -= amount
        if self.health <= 0:
            self.kill()
            self.game.player.gain_experience(EXP_YIELD)
            self.game.player.knowledge_points += KP_YIELD

    @classmethod
    def create_random(cls, game):
        """
        Class method to create an enemy at a random position within the game's playable area.

        Args:
            game (Game): The main game object.

        Returns:
            Enemy: A new Enemy instance at a random valid position.

        Raises:
            ValueError: If no valid positions are found for enemy spawn.
        """
        map_height = len(TILEMAP)
        map_width = len(TILEMAP[0])

        valid_positions = [
            (x, y)
            for y in range(map_height)
            for x in range(map_width)
            if TILEMAP[y][x] == "."
        ]

        if not valid_positions:
            raise ValueError("No valid positions found for enemy spawn")

        x, y = random.choice(valid_positions)
        return cls(game, x, y)

    def animate(self):
        """
        Handle the enemy's animation based on its current state and facing direction.
        """
        now = pygame.time.get_ticks()
        if now - self.last_update > 200:
            self.last_update = now
            self.animation_loop = (self.animation_loop + 1) % len(self.animations[self.facing])
            self.image = self.animations[self.facing][self.animation_loop]
            self.rect = self.image.get_rect(center=self.rect.center)

        if self.x_change == 0 and self.y_change == 0:
            self.image = self.animations[self.facing][0]
            self.rect = self.image.get_rect(center=self.rect.center)