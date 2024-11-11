import pygame
import random
from soundmanager import *

# Constants
WIDTH = 1366
HEIGHT = 768
FPS = 60
PLAYER_HEALTH_IMAGE = pygame.image.load(os.path.join('LEGEND OF ZAHIR/Minigame 5 Assets/Player health icon.png'))
PLAYER_HEALTH = pygame.transform.scale(PLAYER_HEALTH_IMAGE, (50, 55))

# Updated colors to match dark theme
WHITE = (200, 190, 220)  # Lighter purple/white
BLACK = (48, 25, 52)     # Dark purple
GRAY = (120, 100, 140)   # Medium purple
GREEN = (144, 238, 144)  # Soft green
RED = (255, 100, 100)    # Soft red
LIGHT_GREEN = (180, 255, 180)  # Lighter soft green
LIGHT_RED = (255, 180, 180)    # Lighter soft red
BLUE = (150, 150, 255)   # Soft blue
BORDER_COLOR = (150, 130, 170)  # Medium light purple

# Font configurations
FONT_PATH = 'LEGEND OF ZAHIR/assets/fonts/nokiafc22.ttf'
REGULAR_SIZE = 15
MEDIUM_SIZE = 25
LARGE_SIZE = 40

# Timezone definitions (UTC offsets in hours)
TIMEZONES = {
    'New York': -5,
    'London': 0,
    'Paris': 1,
    'Dubai': 4,
    'Tokyo': 9,
    'Sydney': 10,
    'Los Angeles': -8,
    'Singapore': 8
}

class Button:
    def __init__(self, x, y, width, height, text):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.color = GRAY
        self.is_hovered = False
        self.is_correct = False
        self.was_selected = False

    def draw(self, surface, font):
        if self.was_selected:
            self.color = LIGHT_GREEN if self.is_correct else LIGHT_RED
        elif self.is_hovered:
            self.color = WHITE
        else:
            self.color = GRAY

        # Draw button with border
        pygame.draw.rect(surface, self.color, self.rect)
        pygame.draw.rect(surface, BORDER_COLOR, self.rect, 2)
        text_surface = font.render(self.text, True, BLACK)
        text_rect = text_surface.get_rect(center=self.rect.center)
        surface.blit(text_surface, text_rect)

    def handle_event(self, event):
        if event.type == pygame.MOUSEMOTION:
            self.is_hovered = self.rect.collidepoint(event.pos)
            return False
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if self.is_hovered:
                sound_manager.play_sound('button_click')  # Changed to 'buttons' to match the loaded sound
                return True
        return False
    
class TimezoneGame:
    def __init__(self, screen, clock):
        self.screen = screen
        self.clock = clock
        
        # Load and scale background image
        self.bg_img = pygame.image.load('LEGEND OF ZAHIR/assets/backgrounds/Time background.jpg')
        self.bg_img = pygame.transform.scale(self.bg_img, (WIDTH, HEIGHT))
        
        # Add semi-transparent overlay
        self.overlay = pygame.Surface((WIDTH, HEIGHT))
        self.overlay.fill(BLACK)
        self.overlay.set_alpha(150)  # More transparent to show background better
        
        self.regular_font = pygame.font.Font(FONT_PATH, REGULAR_SIZE)
        self.medium_font = pygame.font.Font(FONT_PATH, MEDIUM_SIZE)
        self.large_font = pygame.font.Font(FONT_PATH, LARGE_SIZE)
        
        self.score = 0
        self.total_questions = 0
        self.correct_answers = 0
        self.lives = 4
        self.buttons = []
        
        self.generate_question()
        self.create_buttons()
        self.selected_answer = None
        self.show_result = False
        self.game_over = False
        self.create_continue_button()

    def create_continue_button(self):
        self.continue_button = Button(
            (WIDTH - 160) // 2,
            HEIGHT - 100,
            160,
            45,
            "Continue"
        )

    def create_buttons(self):
        self.buttons = []
        button_width = 160
        button_height = 45
        spacing = 5
        start_y = HEIGHT - 300

        for i, choice in enumerate(self.choices):
            x = (WIDTH - button_width) // 2
            y = start_y + (button_height + spacing) * i
            button = Button(x, y, button_width, button_height, choice)
            button.is_correct = (choice == self.correct_answer)
            self.buttons.append(button)

    def generate_question(self):
        self.source_tz_name = random.choice(list(TIMEZONES.keys()))
        self.target_tz_name = random.choice([tz for tz in TIMEZONES.keys() if tz != self.source_tz_name])
        
        source_offset = TIMEZONES[self.source_tz_name]
        target_offset = TIMEZONES[self.target_tz_name]
        
        self.source_hour = random.randint(0, 23)
        self.source_minute = random.choice([0, 15, 30, 45])
        
        hour_diff = target_offset - source_offset
        target_hour = int((self.source_hour + hour_diff) % 24)
        
        self.correct_answer = f"{target_hour:02d}:{self.source_minute:02d}"
        
        wrong_hours = [(target_hour + offset) % 24 for offset in [-2, -1, 1, 2]]
        wrong_times = [f"{int(h):02d}:{self.source_minute:02d}" for h in wrong_hours]
        
        self.choices = wrong_times[:3] + [self.correct_answer]
        random.shuffle(self.choices)

    def get_calculation_hint(self):
        source_offset = TIMEZONES[self.source_tz_name]
        target_offset = TIMEZONES[self.target_tz_name]
        diff = target_offset - source_offset
        
        if diff > 0:
            return f"Hint: Add {diff} hours to {self.source_hour:02d}:00"
        elif diff < 0:
            return f"Hint: Subtract {abs(diff)} hours from {self.source_hour:02d}:00"
        else:
            return "Hint: Time is the same in both zones"

    def draw_question_screen(self):
        # Draw lives using heart images
        for i in range(self.lives):
            self.screen.blit(PLAYER_HEALTH, (15 + i * 45, 10))  # Position hearts with spacing

        # Draw correct answers text
        correct_text = f"Correct Answers: {self.correct_answers}/3"
        correct_surface = self.regular_font.render(correct_text, True, GREEN)
        self.screen.blit(correct_surface, (20, 60))

        # Draw question
        question_text = f"Convert time from {self.source_tz_name} to {self.target_tz_name}"
        text_surface = self.medium_font.render(question_text, True, WHITE)
        text_rect = text_surface.get_rect(center=(WIDTH // 2, HEIGHT // 6))
        self.screen.blit(text_surface, text_rect)

        # Draw time
        time_text = f"{self.source_hour:02d}:{self.source_minute:02d}"
        time_surface = self.large_font.render(time_text, True, WHITE)
        time_rect = time_surface.get_rect(center=(WIDTH // 2, HEIGHT // 3))
        self.screen.blit(time_surface, time_rect)

        # Draw calculation hint
        hint_text = self.get_calculation_hint()
        hint_surface = self.regular_font.render(hint_text, True, BLUE)
        hint_rect = hint_surface.get_rect(center=(WIDTH // 2, HEIGHT // 3 + 30))
        self.screen.blit(hint_surface, hint_rect)

        # Draw answer buttons
        for button in self.buttons:
            button.draw(self.screen, self.regular_font)


    def draw_result_screen(self):
        result_text = "Correct!" if self.selected_answer == self.correct_answer else "Wrong!"
        color = GREEN if self.selected_answer == self.correct_answer else RED
        result_surface = self.medium_font.render(result_text, True, color)
        result_rect = result_surface.get_rect(center=(WIDTH//2, HEIGHT//6))
        self.screen.blit(result_surface, result_rect)

        explanation_text = f"The correct time in {self.target_tz_name} is {self.correct_answer}"
        explanation_surface = self.regular_font.render(explanation_text, True, WHITE)
        explanation_rect = explanation_surface.get_rect(center=(WIDTH//2, HEIGHT//3))
        self.screen.blit(explanation_surface, explanation_rect)

        for button in self.buttons:
            button.draw(self.screen, self.regular_font)
        self.continue_button.draw(self.screen, self.regular_font)

    def draw(self):
        """Draw the game state with updated victory/defeat messages."""
        # Draw background and overlay
        self.screen.blit(self.bg_img, (0, 0))
        self.screen.blit(self.overlay, (0, 0))

        # Draw lives using heart images
        for i in range(self.lives):
            self.screen.blit(PLAYER_HEALTH, (15 + i * 45, 10))

        # Draw correct answers text
        correct_text = f"Correct Answers: {self.correct_answers}/3"
        correct_surface = self.regular_font.render(correct_text, True, GREEN)
        self.screen.blit(correct_surface, (20, 60))

        if self.game_over:
            if self.correct_answers >= 3:  # Victory condition
                title_text = "Challenge Complete!"
                title_color = GREEN
            else:  # Failed condition
                title_text = "Challenge Failed!"
                title_color = RED

            # Draw main result text
            result_text = self.large_font.render(title_text, True, title_color)
            result_rect = result_text.get_rect(center=(WIDTH//2, HEIGHT//2 - 50))
            self.screen.blit(result_text, result_rect)

            # Draw score text
            score_text = self.medium_font.render(
                f"Final Score: {self.correct_answers}/3", True, WHITE)
            score_rect = score_text.get_rect(center=(WIDTH//2, HEIGHT//2 + 20))
            self.screen.blit(score_text, score_rect)

            # Draw continue instruction
            continue_text = self.regular_font.render(
                "Press SPACE to continue", True, WHITE)
            continue_rect = continue_text.get_rect(center=(WIDTH//2, HEIGHT//2 + 80))
            self.screen.blit(continue_text, continue_rect)
            
        else:
            # Draw normal game elements when game is not over
            if not self.show_result:
                # Draw question
                question_text = f"Convert time from {self.source_tz_name} to {self.target_tz_name}"
                text_surface = self.medium_font.render(question_text, True, WHITE)
                text_rect = text_surface.get_rect(center=(WIDTH//2, HEIGHT//6))
                self.screen.blit(text_surface, text_rect)

                # Draw time
                time_text = f"{self.source_hour:02d}:{self.source_minute:02d}"
                time_surface = self.large_font.render(time_text, True, WHITE)
                time_rect = time_surface.get_rect(center=(WIDTH//2, HEIGHT//3))
                self.screen.blit(time_surface, time_rect)

                # Draw calculation hint
                hint_text = self.get_calculation_hint()
                hint_surface = self.regular_font.render(hint_text, True, BLUE)
                hint_rect = hint_surface.get_rect(center=(WIDTH//2, HEIGHT//3 + 30))
                self.screen.blit(hint_surface, hint_rect)

                # Draw answer buttons
                for button in self.buttons:
                    button.draw(self.screen, self.regular_font)
            else:
                # Draw result screen
                result_text = "Correct!" if self.selected_answer == self.correct_answer else "Wrong!"
                color = GREEN if self.selected_answer == self.correct_answer else RED
                result_surface = self.medium_font.render(result_text, True, color)
                result_rect = result_surface.get_rect(center=(WIDTH//2, HEIGHT//6))
                self.screen.blit(result_surface, result_rect)

                explanation_text = f"The correct time in {self.target_tz_name} is {self.correct_answer}"
                explanation_surface = self.regular_font.render(explanation_text, True, WHITE)
                explanation_rect = explanation_surface.get_rect(center=(WIDTH//2, HEIGHT//3))
                self.screen.blit(explanation_surface, explanation_rect)

                for button in self.buttons:
                    button.draw(self.screen, self.regular_font)
                self.continue_button.draw(self.screen, self.regular_font)

        pygame.display.update()

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return "quit"

            if self.game_over:
                if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                    sound_manager.play_sound('button_click') 
                    if self.lives <= 0:
                        return "failed"
                    elif self.correct_answers >= 3:
                        return "completed"
                    else:
                        return "failed"
            elif self.show_result:
                if self.continue_button.handle_event(event):  # Button class handles sound
                    if self.correct_answers >= 3 or self.lives <= 0:
                        self.game_over = True
                    else:
                        self.generate_question()
                        self.create_buttons()
                        self.show_result = False
            else:
                for button in self.buttons:
                    if button.handle_event(event):  # Button class handles sound
                        self.selected_answer = button.text
                        button.was_selected = True
                        self.show_result = True
                        self.total_questions += 1
                        if self.selected_answer == self.correct_answer:
                            self.score += 1
                            self.correct_answers += 1
                            if self.correct_answers >= 3:
                                self.game_over = True
                        else:
                            self.lives -= 1
                            if self.lives <= 0:
                                self.game_over = True
        return None

def run_timezone_game(screen=None, clock=None):
    if screen is None or clock is None:
        pygame.init()
        screen = pygame.display.set_mode((WIDTH, HEIGHT))
        clock = pygame.time.Clock()
        pygame.display.set_caption("Timezone Conversion Game")

    game = TimezoneGame(screen, clock)
    
    while True:
        result = game.handle_events()
        if result:
            return result
            
        game.draw()
        clock.tick(FPS)

if __name__ == "__main__":
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    clock = pygame.time.Clock()
    result = run_timezone_game(screen, clock)
    pygame.quit()