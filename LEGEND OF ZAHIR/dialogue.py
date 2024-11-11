import pygame
from typing import List, Dict, Optional
import sys
import os

# Add the project root to Python path to enable imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from visual_assets import VisualNovelAssets, CharacterPosition, SpriteType

class DialogueSystem:
    def __init__(self, screen, clock):
        self.screen = screen
        self.clock = clock
        self.font = pygame.font.Font(None, 32)
        
        # Initialize visual novel assets
        self.visual_assets = VisualNovelAssets(screen)
        
        # Adjusted dialogue box dimensions
        self.box_width = 800
        self.box_height = 200
        self.padding = 30
        self.line_spacing = 40
        self.max_chars_per_line = 60
        
        # Create dialogue box surface
        self.dialogue_box = pygame.Surface((self.box_width, self.box_height))
        self.dialogue_box.set_alpha(230)
        
        # Border settings
        self.border_color = (200, 200, 200)
        self.border_width = 3
        
        self.dialogue_speed = 2
        self.current_text = ""
        self.target_text = ""
        self.text_counter = 0
        self.dialogue_active = False
        self.wrapped_lines = []
        self.current_line_index = 0
        self.current_sequence = []
        
        # Initialize dialogue sequences with your existing dialogue_sequences dictionary
        self.dialogue_sequences = {
    'intro': 
    [
        {
            'text': "In an age where knowledge is condemned as dangerous, you stand before the entrance of Vitano's Sanctuary. Within these halls, the last remnants of ancient wisdom lie protected by their eternal guardian.",
            'characters': [
                {'name': 'VN1', 'position': 'CENTER'}
            ]
    
        },
        {
            'text': "You are Zahir, last apprentice of the hidden Scholar's Academy. Your quest is noble - to preserve knowledge not for power, but to reignite the light of learning in a darkened world.",
            'characters': [
                {'name': 'VN2', 'position': 'CENTER'},
            ]
        },
        {
            'text': "The great doors of the sanctuary creak open. Vitano's presence fills the air with electric anticipation. Your trials await, young seeker...",
            'transition': 'fade',
            'background': 'backgrounds',
            'characters': [
                {'name': 'VN3', 'position': 'CENTER'},
            ]
        }
    ],

    'after_tutorial': [
        {
            'text': "The ancient training grounds hum with approval as you demonstrate your basic combat forms. These halls remember countless seekers before you.",
            'characters': [
                {'name': 'VN4', 'position': 'CENTER'}
            ]
        },
        {
            'text': "But physical prowess alone will not unlock the secrets of Vitano's trials. Mind and body must work as one.",
            'characters': [
                {'name': 'VN4', 'position': 'CENTER'},
            ]
        },
        {
            'text': "Before you stands the Chamber of Memory, where patterns of color dance in eternal sequence. The first Orb pulses gently within, waiting for one who understands its rhythm.",
            'characters': [
                {'name': 'VN5', 'position': 'CENTER'}
            ]
        }
    ],

    'after_memory': [
        {
            'text': "The Chamber of Memory recognizes your mastery of patterns. The ancient runes glow with approval as the first trial concludes.",
            'characters': [
                {'name': 'VN5', 'position': 'CENTER'}
            ]
        },
        {
            'text': "The Orb of Sequential Thought resonates with blue light, its knowledge flowing into you. You begin to understand how patterns shape our understanding of the world.",
            'transition': "fade",
            'characters': [
                {'name': 'VN6', 'position': 'CENTER'}
            ]
        },
        {
            'text': "But this is just the beginning. Three more Orbs await, each holding fundamental truths about our world that must be preserved.",
            'transition': 'fade',
            'characters': [
                {'name': 'VN7', 'position': 'LEFT'},
                {'name': 'VN8', 'position': 'CENTER'},
                {'name': 'VN9', 'position': 'RIGHT'}
            ]
        }
    ],

    'after_timezone': [
        {
            'text': "Within the Temporal Sanctum, you have proven your understanding of how time flows differently across our world. The sundials and celestial maps around you glow with approval.",
            'characters': [
                {'name': 'temp1', 'position': 'CENTER'}
            ]
        },
        {
            'text': "The Orb of Temporal Wisdom pulses with golden light, sharing its knowledge of time's eternal dance across the globe.",
            'characters': [
                {'name': 'VN7', 'position': 'CENTER'}
            ]
        },
        {
            'text': "As this knowledge merges with your consciousness, you begin to grasp how time connects all peoples across vast distances.",
            'characters': [
                {'name': 'VN13', 'position': 'CENTER'}
            ]
        }
    ],

    'after_language': [
        {
            'text': "The Linguistics Chamber echoes with the whispers of a thousand tongues. Your mastery of these ancient forms of communication has awakened something deep within its walls.",
            'characters': [
                {'name': 'VN1', 'position': 'CENTER'}
            ]
        },
        {
            'text': "The Orb of Universal Speech bathes the chamber in ethereal purple light. Its power allows you to understand how language bridges the gaps between cultures and minds.",
            'characters': [
                {'name': 'VN8', 'position': 'CENTER'}
            ]
        },
        {
            'text': "With each orb's power, you feel your consciousness expanding. But the final trial still awaits - the test of earthly knowledge itself.",
            'characters': [
                {'name': 'VN14', 'position': 'CENTER'}
            ]
        }
    ],

    'after_continent': [
        {
            'text': "The Geographic Nexus responds to your understanding of our world's physical form. Ancient maps spring to life around you, their boundaries glowing with validated truth.",
            'characters': [
                {'name': 'map', 'position': 'CENTER'}
            ]
        },
        {
            'text': "The Orb of Terrestrial Knowledge radiates emerald light, completing the quartet of fundamental wisdom. Its power shows you how the physical world shapes the destiny of all who dwell within it.",
            'characters': [
                {'name': 'VN9', 'position': 'CENTER'}
            ]
        },
        {
            'text': "With all four Orbs resonating in harmony, Vitano himself stirs. The true test approaches - will you prove worthy of becoming a new Keeper of Wisdom?",
            'characters': [
                {'name': 'Boss', 'position': 'CENTER'}
            ]
        }
    ],

    'before_boss': [
        {
            'text': "The central chamber trembles as Vitano materializes, his form shifting between scholar and guardian, between wisdom and power.",
            'characters': [
                {'name': 'Boss1', 'position': 'CENTER'}
            ]
        },
        {
            'text': "'You have gathered the four fundamental truths, young seeker. But knowledge without wisdom is like a sword without a wielder - dangerous and unpredictable.'",
            'characters': [
                {'name': 'VN12', 'position': 'CENTER'}
            ]
        },
        {
            'text': "'Show me that you understand not just the knowledge contained within the Orbs, but the responsibility that comes with it. Let the final trial begin!'",
            'characters': [
                {'name': 'VN13', 'position': 'CENTER'}
            ]
        }
    ],

    'victory': [
        {
            'text': "As Vitano's form dissolves into pure light, a profound truth washes over you. The trials were never about proving your worth to him.",
            'characters': [
                {'name': 'Boss2', 'position': 'CENTER'},
            ]
        },
        {
            'text': "'You have shown wisdom beyond mere knowledge,' Vitano's voice echoes. 'The Orbs were never meant to be hidden forever, but to be rediscovered when the world was ready.'",
            'characters': [
                {'name': 'Boss4', 'position': 'CENTER'}
            ]
        },
        {
            'text': "The sanctuary transforms, darkness giving way to light. What was once a hidden vault of knowledge shall become a beacon of learning.",
            'characters': [
                {'name': 'Boss5', 'position': 'CENTER'}
            ]
        },
        {
            'text': "You, Zahir, are no longer just a seeker of knowledge. You have become its guardian and teacher, tasked with sharing these fundamental truths with a world too long kept in darkness.",
            'characters': [
                {'name': 'VN11', 'position': 'CENTER'}
            ]
        }
    ]
}
        # Test the text wrapping with the longest dialogue line
        longest_text = max([dialogue['text'] for sequence in self.dialogue_sequences.values() 
                          for dialogue in sequence], key=len)
        
        test_wrap = self.wrap_text(longest_text)
        if len(test_wrap) > 3:
            self.max_chars_per_line = len(longest_text) // 2

    def wrap_text(self, text: str) -> List[str]:
        """
        Wrap text to fit within the dialogue box with improved word wrapping.
        
        Args:
            text: The text to wrap
            
        Returns:
            List of wrapped text lines
        """
        words = text.split()
        lines = []
        current_line = []
        current_width = 0
        space_width = self.font.size(' ')[0]
        
        for word in words:
            word_surface = self.font.render(word, True, (255, 255, 255))
            word_width = word_surface.get_width()
            
            # If adding this word exceeds the box width
            if current_width + word_width + (space_width if current_line else 0) > self.box_width - (2 * self.padding):
                if current_line:  # If there are words in the current line
                    lines.append(' '.join(current_line))
                    current_line = [word]
                    current_width = word_width
                else:  # If the word itself is longer than the line
                    lines.append(word)
                    current_line = []
                    current_width = 0
            else:
                current_line.append(word)
                current_width += word_width + (space_width if current_line else 0)
        
        # Add the last line if there's anything left
        if current_line:
            lines.append(' '.join(current_line))
        
        return lines

    def draw(self):
        """Draw the dialogue scene with improved text positioning and wrapping."""
        if not self.dialogue_active:
            return

        # Clear the screen first
        self.screen.fill((0, 0, 0))

        # Update and draw visual novel assets
        self.visual_assets.update()
        self.visual_assets.draw()

        # Calculate dialogue box position
        box_rect = self.dialogue_box.get_rect(center=(self.screen.get_width() // 2, 
                                                    self.screen.get_height() - 120))

        # Draw semi-transparent dialogue box
        self.dialogue_box.fill((20, 20, 20))
        self.screen.blit(self.dialogue_box, box_rect)
        pygame.draw.rect(self.screen, self.border_color, box_rect, self.border_width)

        # Get the current text to display
        current_text = self.target_text[:int(self.text_counter)]
        
        if current_text:
            # Wrap the current text
            wrapped_lines = self.wrap_text(current_text)
            
            # Calculate starting Y position to center text vertically
            total_text_height = len(wrapped_lines) * self.line_spacing
            start_y = box_rect.top + (self.box_height - total_text_height) // 2
            
            # Draw each line
            for i, line in enumerate(wrapped_lines):
                text_surface = self.font.render(line, True, (255, 255, 255))
                text_rect = text_surface.get_rect()
                text_rect.x = box_rect.left + self.padding
                text_rect.y = start_y + (i * self.line_spacing)
                self.screen.blit(text_surface, text_rect)

        # Draw continue prompt when text is fully displayed
        if self.text_counter >= len(self.target_text):
            prompt = self.font.render("Press SPACE to continue...", True, (200, 200, 200))
            prompt_rect = prompt.get_rect(bottomright=(box_rect.right - self.padding,
                                                    box_rect.bottom - self.padding))
            self.screen.blit(prompt, prompt_rect)

    def update_text(self):
        """Update the current text based on dialogue speed."""
        if self.text_counter < len(self.target_text):
            self.text_counter += self.dialogue_speed
            self.current_text = self.target_text[:int(self.text_counter)]

    def setup_scene(self, sequence_key: str, line_index: int):
        """Set up the visual novel scene for the current dialogue line."""
        if sequence_key in self.dialogue_sequences:
            current_line = self.dialogue_sequences[sequence_key][line_index]
                
            # Get characters from current line
            characters = current_line.get('characters', [])
            
            # Set the background with transition
            background_name = current_line.get('background', 'default')
            transition_type = current_line.get('transition', 'fade')  # Default to fade transition
            
            # Different transition types
            if transition_type == 'fade':
                self.visual_assets.set_background(background_name)  # Uses existing fade transition
            elif transition_type == 'instant':
                self.visual_assets.set_background_instant(background_name)
            
            # Move all existing characters off screen first
            for char_name in self.visual_assets.characters:
                self.visual_assets.move_character(char_name, CharacterPosition.OFF_SCREEN)
            
            # Position the new characters
            for char_data in characters:
                character_name = char_data.get('name', '')
                position = char_data.get('position', 'CENTER')
                
                try:
                    pos = CharacterPosition[position]
                    self.visual_assets.move_character(character_name, pos)
                except KeyError:
                    print(f"Warning: Invalid position {position} for character {character_name}")
                    self.visual_assets.move_character(character_name, CharacterPosition.CENTER)
                
    def start_dialogue(self, sequence_key: str):
        """Start a specific dialogue sequence."""
        if sequence_key in self.dialogue_sequences:
            self.current_sequence = self.dialogue_sequences[sequence_key]
            self.current_line_index = 0
            
            # Setup the scene for the first line
            self.setup_scene(sequence_key, self.current_line_index)
            
            # Set the text for the first line
            self.target_text = self.current_sequence[self.current_line_index]['text']
            self.wrapped_lines = self.wrap_text(self.target_text)
            self.current_text = ""
            self.text_counter = 0
            self.dialogue_active = True
            return True
        return False

    def show_dialogue(self, sequence_key: str):
        """Show a complete dialogue sequence and wait for completion."""
        if not self.start_dialogue(sequence_key):
            return False
        
        running = True
        while running and self.dialogue_active:
            self.update_text()
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return False
                if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                    if self.text_counter < len(self.target_text):
                        # Complete current text immediately
                        self.text_counter = len(self.target_text)
                    else:
                        # Move to next line
                        self.current_line_index += 1
                        if self.current_line_index < len(self.current_sequence):
                            # Setup scene for the next line
                            self.setup_scene(sequence_key, self.current_line_index)
                            # Set the text for the next line
                            self.target_text = self.current_sequence[self.current_line_index]['text']
                            self.text_counter = 0
                        else:
                            self.dialogue_active = False
                            running = False
            
            self.draw()
            pygame.display.flip()
            self.clock.tick(60)
        
        return True