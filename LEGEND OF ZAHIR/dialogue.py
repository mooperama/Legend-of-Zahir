import pygame
from typing import List, Dict, Optional

class DialogueSystem:
    def __init__(self, screen, clock):
        self.screen = screen
        self.clock = clock
        self.font = pygame.font.Font(None, 32)
        self.dialogue_box = pygame.Surface((700, 150))
        self.dialogue_box.set_alpha(230)
        self.dialogue_speed = 2  # Characters per frame
        self.current_text = ""
        self.target_text = ""
        self.text_counter = 0
        self.dialogue_active = False
        
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

    def start_dialogue(self, sequence_key: str):
        """Start a specific dialogue sequence."""
        if sequence_key in self.dialogue_sequences:
            self.current_sequence = self.dialogue_sequences[sequence_key]
            self.current_line_index = 0
            self.target_text = self.current_sequence[0]
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

    def draw(self):
        """Draw the dialogue box and text."""
        if not self.dialogue_active:
            return

        # Draw semi-transparent dialogue box
        self.dialogue_box.fill((0, 0, 0))
        box_rect = self.dialogue_box.get_rect(center=(self.screen.get_width() // 2, 
                                                     self.screen.get_height() - 100))
        self.screen.blit(self.dialogue_box, box_rect)

        # Draw text
        text_surface = self.font.render(self.current_text, True, (255, 255, 255))
        text_rect = text_surface.get_rect(center=(self.screen.get_width() // 2, 
                                                 self.screen.get_height() - 100))
        self.screen.blit(text_surface, text_rect)

        # Draw continue prompt
        if self.text_counter >= len(self.target_text):
            prompt = self.font.render("Press SPACE to continue...", True, (200, 200, 200))
            prompt_rect = prompt.get_rect(bottomright=(self.screen.get_width() - 20,
                                                     self.screen.get_height() - 20))
            self.screen.blit(prompt, prompt_rect)

    def handle_input(self, event: pygame.event.Event) -> bool:
        """Handle player input for dialogue progression."""
        if not self.dialogue_active:
            return False

        if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
            if self.text_counter < len(self.target_text):
                # Show full text immediately
                self.text_counter = len(self.target_text)
                self.current_text = self.target_text
            else:
                # Move to next line or end dialogue
                self.current_line_index += 1
                if self.current_line_index < len(self.current_sequence):
                    self.target_text = self.current_sequence[self.current_line_index]
                    self.current_text = ""
                    self.text_counter = 0
                else:
                    self.dialogue_active = False
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
                if self.handle_input(event):
                    running = False
            
            self.draw()
            pygame.display.flip()
            self.clock.tick(60)
        
        return True