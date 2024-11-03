import pygame
from config_settings import *

class TutorialSystem:
    def __init__(self, game_instance):
        self.game = game_instance
        self.font = pygame.font.Font(None, 32)
        self.active = True
        self.current_step = 0
        self.tutorial_completed = False
        self.overlay_alpha = 128
        
        # Tutorial steps based on whiteboard requirements
        self.tutorial_steps = [
            {
                "message": "Welcome to Legend of Zahir! Press SPACE to continue",
                "completion_key": pygame.K_SPACE
            },
            {
                "message": "Basic Movement Controls:",
                "substeps": [
                    "W - Move Up",
                    "A - Move Left",
                    "S - Move Down",
                    "D - Move Right"
                ],
                "required_keys": {pygame.K_w, pygame.K_a, pygame.K_s, pygame.K_d},
                "keys_pressed": set()
            },
            {
                "message": "Combat Basics:",
                "substeps": [
                    "Left click to shoot",
                    "Kill enemies to gain experience",
                    "Watch your health bar!"
                ],
                "completion_type": "mouse_click"
            },
            {
                "message": "Dialogue and Interaction:",
                "substeps": [
                    "Press SPACE to interact with NPCs",
                    "Press SPACE again to continue the dialogues with the NPCs"
                ],
                "completion_key": pygame.K_SPACE
            },
            {
                "message": "Your journey will include challenges:",
                "substeps": [
                    "1. Order Pattern Memory",
                    "2. Language Challenge",
                    "3. Stars with Questions",
                    "4. Timeline Order",
                    "5. Collecting Journey"
                ],
                "completion_key": pygame.K_SPACE
            },
            {
                "message": "You're ready to begin! Press SPACE to start",
                "completion_key": pygame.K_SPACE
            }
        ]


    def advance_step(self):
        """Progress to next tutorial step"""
        self.current_step += 1
        
        # Only complete tutorial after showing and completing the last step
        if self.current_step >= len(self.tutorial_steps):
            self.tutorial_completed = True
            self.active = False
            return

        # Initialize keys_pressed for new movement tutorial step if needed
        current = self.tutorial_steps[self.current_step]
        if "required_keys" in current:
            current["keys_pressed"] = set()

    def handle_input(self, events):
        """Handle tutorial input events"""
        if not self.active or self.tutorial_completed:
            return

        current = self.tutorial_steps[self.current_step]
        
        for event in events:
            if "completion_key" in current and event.type == pygame.KEYDOWN:
                if event.key == current["completion_key"]:
                    self.advance_step()
                    
            elif "required_keys" in current and event.type == pygame.KEYDOWN:
                if event.key in current["required_keys"]:
                    current["keys_pressed"].add(event.key)
                    if current["keys_pressed"] == current["required_keys"]:
                        self.advance_step()
                        
            elif "completion_type" in current and current["completion_type"] == "mouse_click":
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    self.advance_step()
        
    def draw(self, screen):
        """Draw tutorial elements"""
        if not self.active or self.tutorial_completed:
            return

        # Semi-transparent overlay
        overlay = pygame.Surface((WIDTH, HEIGHT))
        overlay.fill((0, 0, 0))
        overlay.set_alpha(self.overlay_alpha)
        screen.blit(overlay, (0, 0))

        current = self.tutorial_steps[self.current_step]

        # Draw main message
        text = self.font.render(current["message"], True, WHITE)
        text_rect = text.get_rect(center=(WIDTH/2, HEIGHT/4))
        screen.blit(text, text_rect)

        # Draw substeps if present
        if "substeps" in current:
            for i, substep in enumerate(current["substeps"]):
                text = self.font.render(substep, True, WHITE)
                text_rect = text.get_rect(center=(WIDTH/2, HEIGHT/3 + i*40))
                screen.blit(text, text_rect)

        # Draw key visuals for movement tutorial
        if "required_keys" in current:
            self.draw_movement_visuals(screen, current)

        # Draw combat tutorial elements
        if "completion_type" in current and current["completion_type"] == "mouse_click":
            self.draw_combat_visuals(screen)

    def draw_movement_visuals(self, screen, current):
        """Draw movement tutorial visuals"""
        key_positions = {
            pygame.K_w: (WIDTH/2, HEIGHT/2 - 200),
            pygame.K_a: (WIDTH/2 - 200, HEIGHT/2),
            pygame.K_s: (WIDTH/2, HEIGHT/2 + 200),
            pygame.K_d: (WIDTH/2 + 200, HEIGHT/2)
        }
        
        for key, pos in key_positions.items():
            color = GREEN if key in current.get("keys_pressed", set()) else WHITE
            text = self.font.render(pygame.key.name(key).upper(), True, color)
            text_rect = text.get_rect(center=pos)
            screen.blit(text, text_rect)

    def draw_combat_visuals(self, screen):
        """Draw combat tutorial visuals"""
        mouse_pos = pygame.mouse.get_pos()
        pygame.draw.circle(screen, WHITE, mouse_pos, 5)
        pygame.draw.line(screen, RED, mouse_pos, 
                        (mouse_pos[0] + 20, mouse_pos[1] + 20), 2)