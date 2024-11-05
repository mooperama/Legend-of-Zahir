import pygame
from config_settings import WIDTH, HEIGHT, TILESIZE
from sprites import Spritesheet

class Background:
    def __init__(self, game):
        """
        Initialize the background system with tiled dungeon floor pattern
        
        Args:
            game: The main game instance
        """
        self.game = game
        self.tile_width = 29
        self.tile_height = 29

        # Calculate number of tiles needed to cover screen
        self.tiles_x = WIDTH // self.tile_width + 1
        self.tiles_y = HEIGHT // self.tile_height + 1
        
        # Create the background surface
        self.surface = pygame.Surface((WIDTH, HEIGHT))
        
        # Get floor tile from dungeon spritesheet (using specific tile coordinates)
        self.spritesheet = Spritesheet('LEGEND OF ZAHIR/assets/graphics/tilesets/floor tile.PNG')
        # Extract floor tile - adjust coordinates based on your spritesheet
        self.floor_tile = self.spritesheet.get_sprite(0,0,29,29)
        
        # Create the tiled background
        self.create_background()
        
    def create_background(self):
        """Create the tiled background pattern"""
        for y in range(self.tiles_y):
            for x in range(self.tiles_x):
                # Draw the floor tile at each position
                self.surface.blit(self.floor_tile, 
                                (x * self.tile_width, y * self.tile_height))
        
        # Add a slight darkening overlay for dungeon atmosphere
        overlay = pygame.Surface((WIDTH, HEIGHT))
        overlay.fill((20, 20, 30))  # Dark blue-ish tint
        overlay.set_alpha(40)  # Subtle overlay
        self.surface.blit(overlay, (0, 0))
        
    def draw(self, screen):
        """
        Draw the background to the screen
        
        Args:
            screen: The pygame display surface
        """
        screen.blit(self.surface, (0, 0))