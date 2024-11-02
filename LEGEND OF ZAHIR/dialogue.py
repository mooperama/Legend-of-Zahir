import pygame
from typing import List, Dict, Optional
import sys
import os

# Add the project root to Python path to enable imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from visual_assets import VisualNovelAssets, CharacterPosition, CharacterMood

class DialogueSystem:
    def __init__(self, screen, clock):
        self.screen = screen
        self.clock = clock
        self.font = pygame.font.Font(None, 32)
        
        # Initialize visual novel assets
        self.visual_assets = VisualNovelAssets(screen)
        
        # Adjusted dialogue box dimensions
        self.box_width = 800  # Increased width
        self.box_height = 200  # Increased height
        self.padding = 30  # Increased padding
        self.line_spacing = 40  # Increased line spacing
        self.max_chars_per_line = 60  # Reduced characters per line for better readability
        
        # Create dialogue box surface
        self.dialogue_box = pygame.Surface((self.box_width, self.box_height))
        self.dialogue_box.set_alpha(230)
        
        # Border settings
        self.border_color = (200, 200, 200)
        self.border_width = 3
        
        self.dialogue_speed = 2  # Characters per frame
        self.current_text = ""
        self.target_text = ""
        self.text_counter = 0
        self.dialogue_active = False
        self.wrapped_lines = []
        self.current_line_index = 0
        self.current_sequence = []
        
        # Story dialogue sequences
        self.dialogue_sequences = {
            'intro': [
                "In a world where knowledge is power, an ancient being known as Uhand guards powerful orbs of wisdom.",
                "You are Zahir, a scholar-warrior seeking these orbs not for power, but to preserve knowledge for future generations.",
                "Enter Uhand's lair, where both combat skills and intellectual prowess will be tested..."
            ],
            'after_tutorial': [
                "The shadows retreat as you master the basic arts of combat.",
                "But greater challenges lie ahead...",
                "The first trial awaits - the Chamber of Memory."
            ],
            'after_memory': [
                "The ancient candles flicker with approval as you complete the Color Trial.",
                "The first orb of knowledge pulses with a gentle blue light.",
                "Its power flows into you, but three more still remain hidden in the darkness..."
            ],
            'after_timezone': [
                "As the Timeline Challenge concludes, time itself seems to bend around you.",
                "The second orb thrums with temporal energy.",
                "Its golden light merges with the blue, strengthening your resolve..."
            ],
            'after_language': [
                "The shadow creatures' whispers fade as you master their ancient tongue.",
                "The third orb gleams with ethereal purple light.",
                "Its wisdom joins with the others, but one final challenge remains..."
            ],
            'after_continent': [
                "The world's geography yields its secrets to your understanding.",
                "The fourth orb shimmers with emerald radiance.",
                "With all four orbs in your possession, only Uhand stands between you and your destiny..."
            ],
            'before_boss': [
                "The chamber trembles as Uhand emerges from the shadows.",
                "'So, young seeker, you have gathered the orbs. But are you truly worthy of their power?'",
                "Prepare yourself, Zahir. The final test begins..."
            ],
            'victory': [
                "As Uhand falls, a profound realization washes over you.",
                "The true knowledge was not in the orbs themselves, but in the journey to obtain them.",
                "The dark lair transforms, becoming a beacon of learning for future generations.",
                "You, Zahir, are now the guardian of wisdom, tasked with preserving these teachings for ages to come."
            ]
        }
        # Test the text wrapping with the longest dialogue line
        longest_line = max([line for sequence in self.dialogue_sequences.values() for line in sequence], 
                          key=len)
        test_wrap = self.wrap_text(longest_line)
        if len(test_wrap) > 3:  # If any text needs more than 3 lines
            self.max_chars_per_line = len(longest_line) // 2  # Adjust chars per line

    def wrap_text(self, text: str) -> List[str]:
        """Wrap text to fit within the dialogue box with improved word wrapping."""
        words = text.split()
        lines = []
        current_line = []
        current_length = 0

        for word in words:
            word_length = len(word)
            # Account for space between words
            space_length = 1 if current_line else 0
            
            if current_length + word_length + space_length <= self.max_chars_per_line:
                current_line.append(word)
                current_length += word_length + space_length
            else:
                if current_line:  # Only append if there are words in the current line
                    lines.append(' '.join(current_line))
                current_line = [word]
                current_length = word_length

        if current_line:  # Don't forget to append the last line
            lines.append(' '.join(current_line))
            
        return lines

    def draw(self):
        """Draw the dialogue scene with improved text positioning."""
        if not self.dialogue_active:
            return

        # Clear the screen first
        self.screen.fill((0, 0, 0))

        # Update and draw visual novel assets
        self.visual_assets.update()
        self.visual_assets.draw()

        # Calculate dialogue box position (moved up slightly)
        box_rect = self.dialogue_box.get_rect(center=(self.screen.get_width() // 2, 
                                                     self.screen.get_height() - 120))

        # Draw semi-transparent dialogue box
        self.dialogue_box.fill((20, 20, 20))
        self.screen.blit(self.dialogue_box, box_rect)
        pygame.draw.rect(self.screen, self.border_color, box_rect, self.border_width)

        # Draw text with improved positioning
        current_wrapped = []
        current_text = self.target_text[:int(self.text_counter)]
        if current_text:
            current_wrapped = self.wrap_text(current_text)

        # Calculate starting Y position to center text vertically in the box
        total_text_height = len(current_wrapped) * self.line_spacing
        start_y = box_rect.top + (self.box_height - total_text_height) // 2

        # Draw each line of text
        for i, line in enumerate(current_wrapped):
            text_surface = self.font.render(line, True, (255, 255, 255))
            text_rect = text_surface.get_rect()
            text_rect.x = box_rect.left + self.padding
            text_rect.y = start_y + (i * self.line_spacing)
            self.screen.blit(text_surface, text_rect)

        # Draw continue prompt in bottom right corner with proper padding
        if self.text_counter >= len(self.target_text):
            prompt = self.font.render("Press SPACE to continue...", True, (200, 200, 200))
            prompt_rect = prompt.get_rect(bottomright=(box_rect.right - self.padding,
                                                     box_rect.bottom - self.padding))
            self.screen.blit(prompt, prompt_rect)

    def start_dialogue(self, sequence_key: str):
            """Start a specific dialogue sequence."""
            if sequence_key in self.dialogue_sequences:
                # Setup the scene first
                self.setup_scene(sequence_key)
                
                self.current_sequence = self.dialogue_sequences[sequence_key]
                self.current_line_index = 0
                self.target_text = self.current_sequence[0]
                self.wrapped_lines = self.wrap_text(self.target_text)
                self.current_text = ""
                self.text_counter = 0
                self.dialogue_active = True
                return True
            return False

    def update_text(self):
        """Update the currently displaying text."""
        if self.text_counter < len(self.target_text):
            self.text_counter += self.dialogue_speed
            self.current_text = self.target_text[:int(self.text_counter)]

    def setup_scene(self, sequence_key: str):
        """Setup the visual novel scene for a dialogue sequence."""
        # Set background based on sequence
        background_mapping = {
            'intro': 'intro',
            'after_tutorial': 'dungeon',
            'after_memory': 'trial',
            'after_timezone': 'trial',
            'after_language': 'trial',
            'after_continent': 'trial',
            'before_boss': 'boss_room',
            'victory': 'victory'
        }
        
        # Set the background
        background = background_mapping.get(sequence_key, 'dungeon')
        self.visual_assets.set_background(background)
        
        # Clear all characters first by moving them off screen
        for char_name in self.visual_assets.characters:
            self.visual_assets.move_character(char_name, CharacterPosition.OFF_SCREEN)
        
        # Setup characters based on sequence
        if sequence_key == 'intro':
            self.visual_assets.move_character('Narrator', CharacterPosition.CENTER)
            self.visual_assets.set_character_mood('Narrator', CharacterMood.NEUTRAL)
        
        elif sequence_key == 'after_tutorial':
            self.visual_assets.move_character('Zahir', CharacterPosition.CENTER)
            self.visual_assets.set_character_mood('Zahir', CharacterMood.DETERMINED)
        
        elif sequence_key == 'after_memory':
            self.visual_assets.move_character('Spirit', CharacterPosition.LEFT)
            self.visual_assets.move_character('Zahir', CharacterPosition.RIGHT)
            self.visual_assets.set_character_mood('Spirit', CharacterMood.PLEASED)
            self.visual_assets.set_character_mood('Zahir', CharacterMood.HAPPY)
        
        elif sequence_key == 'before_boss':
            self.visual_assets.move_character('Boss', CharacterPosition.LEFT)
            self.visual_assets.move_character('Zahir', CharacterPosition.RIGHT)
            self.visual_assets.set_character_mood('Boss', CharacterMood.ANGRY)
            self.visual_assets.set_character_mood('Zahir', CharacterMood.DETERMINED)
        
        elif sequence_key == 'victory':
            self.visual_assets.move_character('Zahir', CharacterPosition.CENTER)
            self.visual_assets.set_character_mood('Zahir', CharacterMood.HAPPY)

    def show_dialogue(self, sequence_key: str):
        """Show a complete dialogue sequence and wait for completion."""
        if not self.start_dialogue(sequence_key):  # Changed from self.show_dialogue to self.start_dialogue
            return False
        
        running = True
        while running and self.dialogue_active:
            self.update_text()
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return False
                if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                    if self.text_counter < len(self.target_text):
                        self.text_counter = len(self.target_text)
                    else:
                        self.current_line_index += 1
                        if self.current_line_index < len(self.current_sequence):
                            self.target_text = self.current_sequence[self.current_line_index]
                            self.wrapped_lines = self.wrap_text(self.target_text)
                            self.current_text = ""
                            self.text_counter = 0
                        else:
                            self.dialogue_active = False
                            running = False
            
            self.draw()
            pygame.display.flip()
            self.clock.tick(60)
        
        return True