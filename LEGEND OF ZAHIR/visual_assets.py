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

class SpriteType(Enum):
    """Available sprite types."""
    VN1 = "VN1"
    VN2 = "VN2"
    VN3 = "VN3"
    VN4 = "VN4"
    VN5 = "VN5"
    VN6 = "VN6"
    VN7 = "VN7"
    VN8 = "VN8"
    VN9 = "VN9"
    VN10 = "VN10"
    VN11 = "VN11"
    VN12 = "VN12"
    VN13 = "Language man NPC sheet"
    VN14 = "Time man NPC sheet"
    map = "Map NPC"
    Boss = "boss spritesheet"
    Boss1 = "BOSS"
    Boss2 = "Boss3"
    Boss4 = "Boss4"
    Boss5 = "Boss5"
    temp1 = "temp1"
    boss_room = "boss_room"

class Character:
    """Represents a character in the visual novel scenes."""
    
    def __init__(self, name: str, base_path: str, sprite_type: SpriteType):
        """
        Initialize a character with their sprite.
        
        Args:
            name: Character's name
            base_path: Base path to sprites directory
            sprite_type: Type of sprite to use for this character
        """
        self.name = name
        self.sprite_type = sprite_type
        self.current_position = CharacterPosition.OFF_SCREEN
        self.target_position = CharacterPosition.OFF_SCREEN
        self.alpha = 255
        
        # Load sprite
        self.sprite = self._load_sprite(os.path.join(base_path, f"{sprite_type.value}.png"))
            
    def _load_sprite(self, path: str) -> Optional[pygame.Surface]:
        """Load a sprite with error handling and placeholder generation."""
        PIXEL_ART_SIZE = (512, 512)  # Doubled from 256x256
        try:
            sprite = pygame.image.load(path).convert_alpha()
            return pygame.transform.scale(sprite, PIXEL_ART_SIZE)
        except (pygame.error, FileNotFoundError):
            print(f"Warning: Could not load sprite {path}")
            sprite = pygame.Surface(PIXEL_ART_SIZE, pygame.SRCALPHA)
            sprite.fill((100, 100, 100, 200))
            font = pygame.font.Font(None, PIXEL_ART_SIZE[0] // 5)
            text = font.render(f"Missing: {os.path.basename(path)}", True, (255, 255, 255))
            text_rect = text.get_rect(center=(PIXEL_ART_SIZE[0]/2, PIXEL_ART_SIZE[1]/2))
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
            CharacterPosition.LEFT: (self.width * 0.25, self.height * 0.35),
            CharacterPosition.CENTER: (self.width * 0.5 , self.height * 0.35),
            CharacterPosition.RIGHT: (self.width * 0.75, self.height * 0.35),
            CharacterPosition.OFF_SCREEN: (-64, self.height * 0.5)
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
            "VN1": Character("VN1", base_path, SpriteType.VN1),
            "VN2": Character("VN2", base_path, SpriteType.VN2),
            "VN3": Character("VN3", base_path, SpriteType.VN3),
            "VN4": Character("VN4", base_path, SpriteType.VN4),
            "VN5": Character("VN5", base_path, SpriteType.VN5),
            "VN6": Character("VN6", base_path, SpriteType.VN6),
            "VN7": Character("VN7", base_path, SpriteType.VN7),
            "VN8": Character("VN8", base_path, SpriteType.VN8),
            "VN9": Character("VN9", base_path, SpriteType.VN9),
            "VN10": Character("VN10", base_path, SpriteType.VN10),
            "VN11": Character("VN11", base_path, SpriteType.VN11),
            "VN12": Character("VN12", base_path, SpriteType.VN12),
            "VN13": Character("Language man NPC sheet", base_path, SpriteType.VN13),
            "VN14": Character("Time man NPC sheet", base_path, SpriteType.VN14),
            "map": Character("Map NPC", base_path, SpriteType.map),
            "Boss": Character("boss spritesheet", base_path, SpriteType.Boss),
            "Boss1": Character("BOSS", base_path, SpriteType.Boss1),
            "Boss2": Character("Boss3", base_path, SpriteType.Boss2),
            "Boss4": Character("Boss4", base_path, SpriteType.Boss4),
            "Boss5": Character("Boss5", base_path, SpriteType.Boss5),
            "temp1": Character("temp1", base_path, SpriteType.temp1),
            "boss_room": Character("boss_room", base_path, SpriteType.boss_room)
            }  
    def _load_backgrounds(self) -> Dict[str, Optional[pygame.Surface]]:
        """Load all background images."""
        current_dir = os.path.dirname(os.path.abspath(__file__))
        backgrounds_path = os.path.join(current_dir, "LEGEND OF ZAHIR", "visual_novel_assets", "backgrounds")
        print(f"Looking for backgrounds in: {backgrounds_path}")
        
        backgrounds = {"boss_room"}
        
        # List background directory contents
        try:
            bg_files = [f for f in os.listdir(backgrounds_path) if f.endswith('.png')]
            print(f"Found background files: {bg_files}")
            
            for bg_file in bg_files:
                bg_name = os.path.splitext(bg_file)[0]
                path = os.path.join(backgrounds_path, bg_file)
                try:
                    bg = pygame.image.load(path).convert()
                    print(f"Successfully loaded: {bg_name}")
                    backgrounds[bg_name] = pygame.transform.scale(bg, (self.width, self.height))
                except (pygame.error, FileNotFoundError) as e:
                    print(f"Error loading {path}: {str(e)}")
                    
        except OSError as e:
            print(f"Error reading backgrounds directory: {str(e)}")
            
        if not backgrounds:
            # Create a default background if none were loaded
            bg = pygame.Surface((self.width, self.height))
            bg.fill((50, 50, 50))
            backgrounds["default"] = bg
            
        return backgrounds
    
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
                if character.sprite:
                    pos = self.positions[character.current_position]
                    sprite_rect = character.sprite.get_rect(center=pos)
                    self.screen.blit(character.sprite, sprite_rect)
        
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
        assets.move_character(name, position)
    
    return assets