import pygame
from config_settings import *
import os

class Spritesheet:
    def __init__(self, file):
        self.sheet = pygame.image.load(file).convert()
    
    def get_sprite(self, x, y, width, height):
        sprite = pygame.Surface([width, height])
        sprite.blit(self.sheet, (0,0), (x, y, width, height))
        sprite.set_colorkey(BLACK)
        return sprite

def flip(sprites):
    """
    Flip a list of sprite images horizontally.
    
    Args:
    sprites (list): List of pygame.Surface objects representing sprite frames.
    
    Returns:
    list: List of horizontally flipped sprite frames.
    """
    return [pygame.transform.flip(sprite, True, False) for sprite in sprites]

class Block(pygame.sprite.Sprite):
    """
    Block class representing wall or obstacle sprites in the game.
    """

    def __init__(self, game, x, y):
        """
        Initialize a Block object.

        Args:
        game (Game): The main game object.
        x (int): The x-coordinate of the block in tile units.
        y (int): The y-coordinate of the block in tile units.
        """
        self.game = game
        self._layer = BLOCK_LAYER
        self.groups = self.game.allsprites, self.game.blocks
        pygame.sprite.Sprite.__init__(self, self.groups)

        # Convert tile coordinates to pixel coordinates
        self.x = x * TILESIZE
        self.y = y * TILESIZE
        self.width = TILESIZE
        self.height = TILESIZE

        # Load and scale the wall image
        try:
            self.image = pygame.image.load('LEGEND OF ZAHIR/assets/graphics/tilesets/brick wall tile.png').convert_alpha()
            self.image = pygame.transform.scale(self.image, (TILESIZE, TILESIZE))
        except pygame.error:
            # Fallback if image loading fails
            self.image = pygame.Surface([TILESIZE, TILESIZE])
            self.image.fill((100, 100, 100))  # Grey color as fallback

        # Set up collision rectangle
        self.rect = self.image.get_rect()
        self.rect.x = self.x
        self.rect.y = self.y