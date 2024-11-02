import pygame
from config_settings import *

class Bullet(pygame.sprite.Sprite):
    """
    Bullet class representing projectiles fired by the player.
    
    Attributes:
        game: Reference to the main game instance
        x, y: Starting position of the bullet
        direction: Vector2 indicating bullet's direction
    """
    def __init__(self, game, x, y, direction):
        # Sprite group setup
        self._layer = PLAYER_LAYER
        self.groups = game.allsprites, game.bullets
        pygame.sprite.Sprite.__init__(self, self.groups)
        
        self.game = game
        self.x = x
        self.y = y
        self.width = BULLETSIZE
        self.height = BULLETSIZE
        
        # Load bullet image
        try:
            self.original_image = pygame.image.load('LEGEND OF ZAHIR/fireball.png').convert_alpha()
            # Scale the image to desired size (adjust size as needed)
            scaled_size = (32, 32)  # or use BULLETSIZE for both dimensions
            self.original_image = pygame.transform.scale(self.original_image, scaled_size)
        except pygame.error as e:
            print(f"Couldn't load bullet image: {e}")
            # Create a fallback surface if image loading fails
            self.original_image = pygame.Surface((BULLETSIZE, BULLETSIZE))
            self.original_image.fill((255, 165, 0))  # Orange color as fallback
        
        # Set initial image and create rect
        self.image = self.original_image
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)  # Center the bullet at spawn position
        
        # Movement attributes
        self.direction = direction
        self.speed = 8  # Adjust speed as needed
        
        # Animation timing
        self.last_update = pygame.time.get_ticks()
        self.frame_rate = 50  # Milliseconds between frame updates
        self.angle = 0  # Track current rotation angle

    def update(self):
        """Update bullet position and check for collisions."""
        # Move the bullet
        self.rect.x += self.direction.x * self.speed
        self.rect.y += self.direction.y * self.speed

        # Rotate bullet to face direction of travel
        target_angle = pygame.math.Vector2().angle_to(self.direction)
        self.image = pygame.transform.rotate(self.original_image, -target_angle - 90)
        # Keep the bullet centered after rotation
        self.rect = self.image.get_rect(center=self.rect.center)

        # Check wall collisions
        if pygame.sprite.spritecollide(self, self.game.blocks, False):
            self.kill()

        # Remove if off screen
        if (self.rect.left > WIDTH or self.rect.right < 0 or 
            self.rect.top > HEIGHT or self.rect.bottom < 0):
            self.kill()

    def animate(self):
        """
        Animate the bullet (if using animation frames).
        Currently just handles rotation, but can be expanded for frame animation.
        """
        now = pygame.time.get_ticks()
        if now - self.last_update > self.frame_rate:
            self.last_update = now
            
            # Update rotation to match direction
            target_angle = pygame.math.Vector2().angle_to(self.direction)
            if target_angle != self.angle:
                self.angle = target_angle
                self.image = pygame.transform.rotate(self.original_image, -self.angle - 90)
                self.rect = self.image.get_rect(center=self.rect.center)