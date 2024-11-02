import pygame
import random

# Constants
WIDTH = 960
HEIGHT = 540
FPS = 60
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (128, 128, 128)
GREEN = (0, 255, 0)
RED = (255, 0, 0)
LIGHT_GREEN = (200, 255, 200)
LIGHT_RED = (255, 200, 200)

# Font configurations
FONT_PATH = 'LEGEND OF ZAHIR/assets/fonts/nokiafc22.ttf'
REGULAR_SIZE = 15
MEDIUM_SIZE = 25
LARGE_SIZE = 40

# Simplified timezone definitions (UTC offsets in hours)
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

        pygame.draw.rect(surface, self.color, self.rect)
        text_surface = font.render(self.text, True, BLACK)
        text_rect = text_surface.get_rect(center=self.rect.center)
        surface.blit(text_surface, text_rect)

    def handle_event(self, event):
        if event.type == pygame.MOUSEMOTION:
            self.is_hovered = self.rect.collidepoint(event.pos)
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if self.is_hovered:
                return True
        return False

class TimezoneGame:
    def __init__(self, screen, clock):
        self.screen = screen
        self.clock = clock
        
        # Initialize fonts with Nokia style
        self.regular_font = pygame.font.Font(FONT_PATH, REGULAR_SIZE)
        self.medium_font = pygame.font.Font(FONT_PATH, MEDIUM_SIZE)
        self.large_font = pygame.font.Font(FONT_PATH, LARGE_SIZE)
        
        self.score = 0
        self.total_questions = 0
        self.correct_answers = 0
        self.lives = 4
        self.generate_question()
        self.create_buttons()
        self.selected_answer = None
        self.show_result = False
        self.game_over = False
        self.create_continue_button()

    def create_continue_button(self):
        button_width = 160
        button_height = 45
        x = (WIDTH - button_width) // 2
        y = HEIGHT - 100
        self.continue_button = Button(x, y, button_width, button_height, "Continue")

    def generate_question(self):
        self.source_tz_name = random.choice(list(TIMEZONES.keys()))
        self.target_tz_name = random.choice([tz for tz in TIMEZONES.keys() if tz != self.source_tz_name])
        
        source_offset = TIMEZONES[self.source_tz_name]
        target_offset = TIMEZONES[self.target_tz_name]
        
        self.source_hour = random.randint(0, 23)
        self.source_minute = random.choice([0, 15, 30, 45])
        
        hour_diff = target_offset - source_offset
        target_hour = (self.source_hour + hour_diff) % 24
        
        self.correct_answer = f"{target_hour:02d}:{self.source_minute:02d}"
        
        wrong_hours = [(target_hour + offset) % 24 for offset in [-2, -1, 1, 2]]
        wrong_times = [f"{h:02d}:{self.source_minute:02d}" for h in wrong_hours]
        
        self.choices = wrong_times[:3] + [self.correct_answer]
        random.shuffle(self.choices)

    def create_buttons(self):
        self.buttons = []
        button_width = 160
        button_height = 45
        spacing = 15
        start_y = HEIGHT // 2

        for i, choice in enumerate(self.choices):
            x = (WIDTH - button_width) // 2
            y = start_y + (button_height + spacing) * i
            button = Button(x, y, button_width, button_height, choice)
            button.is_correct = (choice == self.correct_answer)
            self.buttons.append(button)

    def draw_question_screen(self):
        # Draw lives
        lives_text = f"Lives: {'❤' * self.lives}"
        lives_surface = self.regular_font.render(lives_text, True, RED)
        self.screen.blit(lives_surface, (WIDTH - 150, 20))

        # Draw correct answers counter
        correct_text = f"Correct Answers: {self.correct_answers}/3"
        correct_surface = self.regular_font.render(correct_text, True, GREEN)
        self.screen.blit(correct_surface, (20, 60))

        question_text = f"Convert time from {self.source_tz_name} to {self.target_tz_name}"
        text_surface = self.medium_font.render(question_text, True, BLACK)
        text_rect = text_surface.get_rect(center=(WIDTH//2, HEIGHT//6))
        self.screen.blit(text_surface, text_rect)

        time_text = f"{self.source_hour:02d}:{self.source_minute:02d}"
        time_surface = self.large_font.render(time_text, True, BLACK)
        time_rect = time_surface.get_rect(center=(WIDTH//2, HEIGHT//3))
        self.screen.blit(time_surface, time_rect)

        for button in self.buttons:
            button.draw(self.screen, self.regular_font)

    def draw_result_screen(self):
        result_text = "Correct!" if self.selected_answer == self.correct_answer else "Wrong!"
        color = GREEN if self.selected_answer == self.correct_answer else RED
        result_surface = self.medium_font.render(result_text, True, color)
        result_rect = result_surface.get_rect(center=(WIDTH//2, HEIGHT//6))
        self.screen.blit(result_surface, result_rect)

        explanation_text = f"The correct time in {self.target_tz_name} is {self.correct_answer}"
        explanation_surface = self.regular_font.render(explanation_text, True, BLACK)
        explanation_rect = explanation_surface.get_rect(center=(WIDTH//2, HEIGHT//3))
        self.screen.blit(explanation_surface, explanation_rect)

        for button in self.buttons:
            button.draw(self.screen, self.regular_font)

        self.continue_button.draw(self.screen, self.regular_font)

    def draw(self):
        self.screen.fill(WHITE)

        score_text = self.regular_font.render(f"Score: {self.score}/{self.total_questions}", True, BLACK)
        self.screen.blit(score_text, (20, 20))

        if self.game_over:
            game_over_text = self.large_font.render("Game Over!", True, BLACK)
            final_score_text = self.medium_font.render(
                f"Correct Answers: {self.correct_answers}/3", True, BLACK
            )
            if self.lives <= 0:
                status_text = self.regular_font.render("Out of lives!", True, RED)
            else:
                status_text = self.regular_font.render(
                    "Victory! Press SPACE to finish" if self.correct_answers >= 3 
                    else "Not enough correct answers! Press SPACE to finish", 
                    True, 
                    GREEN if self.correct_answers >= 3 else RED
                )
            
            self.screen.blit(game_over_text, 
                           (WIDTH//2 - game_over_text.get_width()//2, HEIGHT//3))
            self.screen.blit(final_score_text, 
                           (WIDTH//2 - final_score_text.get_width()//2, HEIGHT//2))
            self.screen.blit(status_text,
                           (WIDTH//2 - status_text.get_width()//2, HEIGHT*2//3))
        elif self.show_result:
            self.draw_result_screen()
        else:
            self.draw_question_screen()

        pygame.display.flip()

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return "quit"

            if self.game_over:
                if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                    if self.lives <= 0:
                        return "failed"  # Changed from "died" to "failed"
                    elif self.correct_answers >= 3:
                        return "completed"
                    else:
                        return "failed"  # Changed from "died" to "failed"
            elif self.show_result:
                if self.continue_button.handle_event(event):
                    if self.correct_answers >= 3 or self.lives <= 0:
                        self.game_over = True
                    else:
                        self.generate_question()
                        self.create_buttons()
                        self.show_result = False
            else:
                for i, button in enumerate(self.buttons):
                    if button.handle_event(event):
                        self.selected_answer = self.choices[i]
                        button.was_selected = True
                        self.show_result = True
                        self.total_questions += 1
                        if self.selected_answer == self.correct_answer:
                            self.score += 1
                            self.correct_answers += 1
                        else:
                            self.lives -= 1

        return None

def run_timezone_game(screen=None, clock=None):
    """
    Main function that can be called from the main game.
    Returns:
        str: "completed", "failed", or "quit" based on game outcome
    """
    if screen is None or clock is None:
        pygame.init()
        screen = pygame.display.set_mode((WIDTH, HEIGHT))
        clock = pygame.time.Clock()
        pygame.display.set_caption("Timezone Conversion Game")

    game = TimezoneGame(screen, clock)
    
    while True:  # Changed from running variable to infinite loop with returns
        result = game.handle_events()
        if result in ["completed", "failed", "quit"]:
            return result
            
        game.draw()
        clock.tick(FPS)

        if screen is None:  # Only quit if we created our own screen
            pygame.quit()

# For standalone testing
if __name__ == "__main__":
    run_timezone_game()