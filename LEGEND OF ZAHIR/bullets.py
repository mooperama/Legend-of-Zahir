import pygame
from config_settings import *

class Bullet(pygame.sprite.Sprite):
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
        
        self.rect = self.image.get_rect()
        self.rect.x = self.x
        self.rect.y = self.y
        self.image = pygame.transform.scale(self.img, (TILESIZE, TILESIZE))
        
        self.direction = direction
        self.speed = 5
        
        # Animation timing
        self.last_update = pygame.time.get_ticks()
        self.frame_rate = 100  # Milliseconds

    def update(self):
        # Animate the bullet
        self.animate()
        
        # Move the bullet
        self.rect.x += self.direction.x * self.speed
        self.rect.y += self.direction.y * self.speed

        # Check wall collisions
        if pygame.sprite.spritecollide(self, self.game.blocks, False):
            self.kill()

        # Remove if off screen
        if (self.rect.left > WIDTH or self.rect.right < 0 or 
            self.rect.top > HEIGHT or self.rect.bottom < 0):
            self.kill()

    def animate(self):
        now = pygame.time.get_ticks()
        if now - self.last_update > self.frame_rate:
            self.last_update = now
            self.animation_loop = (self.animation_loop + 1) % len(self.animation_list)
            self.image = self.animation_list[self.animation_loop]
            
            # If you want the bullet to rotate based on direction:
            angle = pygame.math.Vector2().angle_to(self.direction)
            self.image = pygame.transform.rotate(self.image, -angle - 90)