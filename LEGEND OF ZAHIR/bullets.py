import pygame
from config_settings import *

class AmmoSystem:
    """Manages the player's ammunition and magazine system."""
    def __init__(self):
        self.magazine_size = 10
        self.current_ammo = self.magazine_size
        self.reloading = False
        self.reload_time = 2000  # 2 seconds
        self.reload_start = 0
        
    def can_shoot(self):
        """Check if player can shoot."""
        return self.current_ammo > 0 and not self.reloading
        
    def shoot(self):
        """Use one bullet."""
        if self.can_shoot():
            self.current_ammo -= 1
            return True
        return False
            
    def start_reload(self):
        """Start the reload process."""
        if not self.reloading and self.current_ammo < self.magazine_size:
            self.reloading = True
            self.reload_start = pygame.time.get_ticks()
            return True
        return False
            
    def update(self):
        """Update reload progress."""
        if self.reloading:
            current_time = pygame.time.get_ticks()
            if current_time - self.reload_start >= self.reload_time:
                self.current_ammo = self.magazine_size
                self.reloading = False

class Bullet(pygame.sprite.Sprite):
    def __init__(self, game, x, y, direction):
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
            scaled_size = (32, 32)
            self.original_image = pygame.transform.scale(self.original_image, scaled_size)
        except pygame.error as e:
            print(f"Couldn't load bullet image: {e}")
            self.original_image = pygame.Surface((BULLETSIZE, BULLETSIZE))
            self.original_image.fill((255, 165, 0))
        
        self.image = self.original_image
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        
        self.direction = direction
        self.speed = 8
        
        self.last_update = pygame.time.get_ticks()
        self.frame_rate = 50
        self.angle = 0

    def update(self):
        self.rect.x += self.direction.x * self.speed
        self.rect.y += self.direction.y * self.speed

        target_angle = pygame.math.Vector2().angle_to(self.direction)
        self.image = pygame.transform.rotate(self.original_image, -target_angle - 90)
        self.rect = self.image.get_rect(center=self.rect.center)

        if pygame.sprite.spritecollide(self, self.game.blocks, False):
            self.kill()

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