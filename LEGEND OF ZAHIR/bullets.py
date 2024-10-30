import pygame
from config_settings import *

class Bullet(pygame.sprite.Sprite):
    """
    Bullet class representing projectiles fired by the player.
    """

    def __init__(self, game, x, y, direction):
        """
        Initialize the Bullet object.
        
        Args:
        game (Game): The main game object.
        x (int): Initial x-coordinate of the bullet.
        y (int): Initial y-coordinate of the bullet.
        direction (pygame.math.Vector2): Direction vector of the bullet's movement.
        """
        self.game = game
        self._layer = PLAYER_LAYER
        self.groups = self.game.allsprites, self.game.bullets
        pygame.sprite.Sprite.__init__(self, self.groups)

        self.x = x
        self.y = y
        self.width = BULLETSIZE
        self.height = BULLETSIZE

        self.image = pygame.Surface([self.width, self.height])
        self.image.fill(WHITE)

        self.rect = self.image.get_rect()
        self.rect.x = self.x
        self.rect.y = self.y

        self.direction = direction
        self.speed = 5

    def update(self):
        """
        Update the bullet's position and check for collisions.
        """
        # Move the bullet
        self.rect.x += self.direction.x * self.speed
        self.rect.y += self.direction.y * self.speed

        # Check for collision with walls
        if pygame.sprite.spritecollide(self, self.game.blocks, False):
            self.kill()  # Remove the bullet if it hits a wall

        # Remove the bullet if it goes off-screen
        if self.rect.left > WIDTH or self.rect.right < 0 or self.rect.top > HEIGHT or self.rect.bottom < 0:
            self.kill()