import pygame
import os
from typing import Dict, Optional, Tuple
from enum import Enum

class CharacterPosition(Enum):
    """Possible positions for character sprites on screen."""
    LEFT = "left"
    CENTER = "center"
    RIGHT = "right"
    OFF_SCREEN = "off_screen"

class CharacterMood(Enum):
    """Available character moods/expressions."""
    NEUTRAL = "neutral"
    HAPPY = "happy"
    DETERMINED = "determined"
    SURPRISED = "surprised"
    ANGRY = "angry"
    PLEASED = "pleased"
    DEFEATED = "defeated"

class Character:
    """Represents a character in the visual novel scenes."""
    
    def __init__(self, name: str, base_path: str):
        """
        Initialize a character with their sprites.
        
        Args:
            name: Character's name
            base_path: Base path to character's sprite directory
        """
        self.name = name
        self.sprites: Dict[CharacterMood, Optional[pygame.Surface]] = {}
        self.current_position = CharacterPosition.OFF_SCREEN
        self.target_position = CharacterPosition.OFF_SCREEN
        self.current_mood = CharacterMood.NEUTRAL
        self.alpha = 255
        
        # Load all possible moods
        for mood in CharacterMood:
            sprite_path = os.path.join(base_path, f"{name.lower()}_{mood.value}.png")
            self.sprites[mood] = self._load_sprite(sprite_path)
            
    def _load_sprite(self, path: str) -> Optional[pygame.Surface]:
        """Load a sprite with error handling and placeholder generation."""
        try:
            sprite = pygame.image.load(path).convert_alpha()
            # Scale sprite if needed
            return pygame.transform.scale(sprite, (300, 600))  # Adjust size as needed
        except (pygame.error, FileNotFoundError):
            print(f"Warning: Could not load sprite {path}")
            # Create placeholder sprite
            sprite = pygame.Surface((300, 600), pygame.SRCALPHA)
            sprite.fill((100, 100, 100, 200))
            # Add text to identify the missing sprite
            font = pygame.font.Font(None, 36)
            text = font.render(f"Missing: {os.path.basename(path)}", True, (255, 255, 255))
            text_rect = text.get_rect(center=(150, 300))
            sprite.blit(text, text_rect)
            return sprite

class VisualNovelAssets:
    """Manages all visual novel assets and rendering."""
    
    def __init__(self, screen: pygame.Surface):
        """
        Initialize the visual novel assets manager.
        
        Args:
            screen: Pygame surface to render on
        """
        self.screen = screen
        self.width = screen.get_width()
        self.height = screen.get_height()
        
        # Initialize position coordinates
        self.positions = {
            CharacterPosition.LEFT: (self.width * 0.2, self.height * 0.5),
            CharacterPosition.CENTER: (self.width * 0.5, self.height * 0.5),
            CharacterPosition.RIGHT: (self.width * 0.8, self.height * 0.5),
            CharacterPosition.OFF_SCREEN: (-300, self.height * 0.5)
        }
        
        # Load characters
        self.characters: Dict[str, Character] = self._init_characters()
        
        # Load backgrounds
        self.backgrounds = self._load_backgrounds()
        
        # Current state
        self.current_background = None
        self.transition_alpha = 0
        self.is_transitioning = False
        
    def _init_characters(self) -> Dict[str, Character]:
        """Initialize all game characters."""
        base_path = "LEGEND OF ZAHIR/visual_novel_assets"
        return {
            "Zahir": Character("Zahir", base_path),
            "Spirit": Character("Spirit", base_path),
            "Boss": Character("Boss", base_path),
            "Narrator": Character("Narrator", base_path)
        }
    
    def _load_backgrounds(self) -> Dict[str, Optional[pygame.Surface]]:
        """Load all background images."""
        backgrounds_path = "LEGEND OF ZAHIR/visual_novel_assets/backgrounds"
        backgrounds = {}
        
        # List of expected backgrounds
        expected_bgs = ["intro", "dungeon", "trial", "boss_room", "victory"]
        
        for bg_name in expected_bgs:
            path = os.path.join(backgrounds_path, f"{bg_name}.png")
            try:
                bg = pygame.image.load(path).convert()
                backgrounds[bg_name] = pygame.transform.scale(bg, (self.width, self.height))
            except (pygame.error, FileNotFoundError):
                print(f"Warning: Could not load background {path}")
                # Create placeholder background
                bg = pygame.Surface((self.width, self.height))
                bg.fill((50, 50, 50))
                font = pygame.font.Font(None, 48)
                text = font.render(f"Missing Background: {bg_name}", True, (255, 255, 255))
                text_rect = text.get_rect(center=(self.width/2, self.height/2))
                bg.blit(text, text_rect)
                backgrounds[bg_name] = bg
                
        return backgrounds
    
    def set_character_mood(self, character_name: str, mood: CharacterMood):
        """Set a character's mood/expression."""
        if character_name in self.characters:
            self.characters[character_name].current_mood = mood
    
    def move_character(self, character_name: str, position: CharacterPosition):
        """Move a character to a new position."""
        if character_name in self.characters:
            self.characters[character_name].target_position = position
    
    def set_background(self, background_name: str):
        """Set the current background with transition."""
        if background_name in self.backgrounds:
            self.current_background = self.backgrounds[background_name]
            self.is_transitioning = True
            self.transition_alpha = 0
    
    def update(self):
        """Update animations and transitions."""
        # Update character positions
        for character in self.characters.values():
            if character.target_position != character.current_position:
                # Implement smooth movement here
                character.current_position = character.target_position
        
        # Update transitions
        if self.is_transitioning:
            self.transition_alpha = min(255, self.transition_alpha + 5)
            if self.transition_alpha >= 255:
                self.is_transitioning = False
    
    def draw(self):
        """Draw the current visual novel scene."""
        # Draw background
        if self.current_background:
            self.screen.blit(self.current_background, (0, 0))
        
        # Draw characters
        for character in self.characters.values():
            if character.current_position != CharacterPosition.OFF_SCREEN:
                sprite = character.sprites[character.current_mood]
                if sprite:
                    pos = self.positions[character.current_position]
                    sprite_rect = sprite.get_rect(midbottom=pos)
                    self.screen.blit(sprite, sprite_rect)
        
        # Draw transition overlay
        if self.is_transitioning:
            overlay = pygame.Surface((self.width, self.height))
            overlay.fill((0, 0, 0))
            overlay.set_alpha(self.transition_alpha)
            self.screen.blit(overlay, (0, 0))

# Example usage:
def create_scene(screen: pygame.Surface, scene_data: Dict):
    """
    Create a visual novel scene from scene data.
    
    Args:
        screen: Pygame surface to render on
        scene_data: Dictionary containing scene information
    """
    assets = VisualNovelAssets(screen)
    
    # Set background
    assets.set_background(scene_data.get("background", "default"))
    
    # Position characters
    for char_data in scene_data.get("characters", []):
        name = char_data["name"]
        position = CharacterPosition[char_data.get("position", "OFF_SCREEN")]
        mood = CharacterMood[char_data.get("mood", "NEUTRAL")]
        
        assets.move_character(name, position)
        assets.set_character_mood(name, mood)
    
    return assets