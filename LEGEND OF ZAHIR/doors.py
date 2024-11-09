import pygame

from config_settings import *

class Door(pygame.sprite.Sprite):
    def __init__(self, game, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.game = game
        
        # Create door appearance (2 tiles tall)
        self.image = pygame.Surface((TILESIZE, TILESIZE * 2))
        self.image.fill((139, 69, 19))  # Brown color
        
        # Add a border to make it more visible
        pygame.draw.rect(self.image, (101, 67, 33), self.image.get_rect(), 3)  # Darker brown border
        
        # Add inner details to make it look more like a door
        door_width = TILESIZE
        door_height = TILESIZE * 2
        
        # Add door panels
        panel_color = (165, 42, 42)  # Darker brown for panels
        panel_margin = 8
        panel_width = door_width - (panel_margin * 2)
        panel_height = (door_height - (panel_margin * 3)) // 2
        
        # Top panel
        pygame.draw.rect(self.image, panel_color, 
                        (panel_margin, panel_margin, 
                         panel_width, panel_height))
        
        # Bottom panel
        pygame.draw.rect(self.image, panel_color, 
                        (panel_margin, panel_margin * 2 + panel_height,
                         panel_width, panel_height))
        
        # Add doorknob
        knob_color = (218, 165, 32)  # Golden color
        knob_radius = 4
        knob_pos = (door_width - 12, door_height // 2)
        pygame.draw.circle(self.image, knob_color, knob_pos, knob_radius)
        
        # Position the door
        self.rect = self.image.get_rect()
        self.rect.x = x * TILESIZE
        self.rect.y = (y - 1) * TILESIZE  # Offset up by one tile
        
        # Set layer (ensure door appears at correct depth)
        self._layer = WALL_LAYER + 1  # Just in front of walls but behind player
        
        # Store original image for reference
        self.original_image = self.image.copy()
        
        # Animation variables
        self.is_opening = False
        self.open_progress = 0
        self.open_speed = 2
        self.fully_open = False

    def open_door(self):
        """Start door opening animation."""
        if not self.is_opening:
            self.is_opening = True
            self.open_progress = 0
            
    def update(self):
        """Update door state and animation."""
        if self.is_opening and not self.fully_open:
            # Increase open progress
            self.open_progress += self.open_speed
            
            if self.open_progress >= 100:
                self.fully_open = True
                self.open_progress = 100
            
            # Create opening animation effect
            # Scale the door to create a "opening" effect
            scale_factor = 1.0 - (self.open_progress / 200)  # Door gets narrower
            if scale_factor > 0:
                new_width = int(TILESIZE * scale_factor)
                if new_width > 0:
                    new_image = pygame.transform.scale(self.original_image, 
                                                     (new_width, TILESIZE * 2))
                    self.image = new_image
                    # Keep door centered while scaling
                    old_center = self.rect.center
                    self.rect = self.image.get_rect()
                    self.rect.center = old_center