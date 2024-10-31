import pygame
import datetime
from datetime import datetime
import pytz
import random
import time

# Initialize Pygame
pygame.init()

# Constants
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
FPS = 60

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (128, 128, 128)
LIGHT_GRAY = (200, 200, 200)
BLUE = (0, 100, 255)
GREEN = (0, 255, 0)
RED = (255, 0, 0)
DARK_BLUE = (0, 0, 128)

class Button:
    def __init__(self, x, y, width, height, text, color, hover_color):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.color = color
        self.hover_color = hover_color
        self.is_hovered = False
        self.font = pygame.font.Font(None, 32)
        
    def draw(self, screen):
        color = self.hover_color if self.is_hovered else self.color
        pygame.draw.rect(screen, color, self.rect, border_radius=5)
        pygame.draw.rect(screen, BLACK, self.rect, 2, border_radius=5)
        
        text_surface = self.font.render(self.text, True, BLACK)
        text_rect = text_surface.get_rect(center=self.rect.center)
        screen.blit(text_surface, text_rect)
        
    def handle_event(self, event):
        if event.type == pygame.MOUSEMOTION:
            self.is_hovered = self.rect.collidepoint(event.pos)
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.rect.collidepoint(event.pos):
                return True
        return False

class InputBox:
    def __init__(self, x, y, width, height):
        self.rect = pygame.Rect(x, y, width, height)
        self.color = LIGHT_GRAY
        self.text = ""
        self.font = pygame.font.Font(None, 32)
        self.active = False
        
    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            self.active = self.rect.collidepoint(event.pos)
            self.color = WHITE if self.active else LIGHT_GRAY
        if event.type == pygame.KEYDOWN and self.active:
            if event.key == pygame.K_RETURN:
                return self.text
            elif event.key == pygame.K_BACKSPACE:
                self.text = self.text[:-1]
            elif len(self.text) < 5:
                if event.unicode.isdigit() or event.unicode == ':':
                    self.text += event.unicode
        return None
        
    def draw(self, screen):
        pygame.draw.rect(screen, self.color, self.rect, border_radius=5)
        pygame.draw.rect(screen, BLACK, self.rect, 2, border_radius=5)
        
        text_surface = self.font.render(self.text, True, BLACK)
        text_rect = text_surface.get_rect(center=self.rect.center)
        screen.blit(text_surface, text_rect)

class TimezoneGame:
    def __init__(self):
        # Initialize display first
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Timezone Conversion Game")
        self.clock = pygame.time.Clock()
        
        # Initialize fonts
        self.font = pygame.font.Font(None, 32)
        self.small_font = pygame.font.Font(None, 24)
        
        # Initialize timezone data first
        self.timezone_pairs = [
            ('US/Pacific', 'US/Eastern'),
            ('US/Pacific', 'Europe/London'),
            ('US/Eastern', 'Europe/Paris'),
            ('Europe/London', 'Asia/Tokyo'),
            ('Asia/Dubai', 'Australia/Sydney'),
            ('Europe/Paris', 'Asia/Shanghai'),
            ('US/Pacific', 'Asia/Tokyo'),
            ('US/Eastern', 'Asia/Dubai')
        ]
        
        self.timezone_hints = {
            'US/Pacific': 'PST/PDT (UTC-8/-7)',
            'US/Eastern': 'EST/EDT (UTC-5/-4)',
            'Europe/London': 'GMT/BST (UTC+0/+1)',
            'Europe/Paris': 'CET/CEST (UTC+1/+2)',
            'Asia/Tokyo': 'JST (UTC+9)',
            'Asia/Dubai': 'GST (UTC+4)',
            'Australia/Sydney': 'AEST/AEDT (UTC+10/+11)',
            'Asia/Shanghai': 'CST (UTC+8)'
        }
        
        # Initialize game state
        self.score = 0
        self.hints_used = 0
        self.questions_asked = 0
        self.max_questions = 5
        self.current_hint_index = 0
        self.current_hints = []
        self.feedback_message = ""
        self.feedback_color = BLACK
        
        # Generate first question
        self.current_question = self.generate_question()
        
        # Initialize UI elements last
        self.input_box = InputBox(300, 400, 100, 40)
        self.hint_button = Button(50, 400, 100, 40, "Hint", LIGHT_GRAY, WHITE)
        self.submit_button = Button(450, 400, 100, 40, "Submit", LIGHT_GRAY, GREEN)
        self.next_button = Button(600, 400, 100, 40, "Next", LIGHT_GRAY, BLUE)

    def generate_question(self):
        from_tz, to_tz = random.choice(self.timezone_pairs)
        hour = random.randint(0, 23)
        minute = random.choice([0, 30])
        
        source_time = datetime.now().replace(hour=hour, minute=minute)
        source_tz = pytz.timezone(from_tz)
        target_tz = pytz.timezone(to_tz)
        
        source_time = source_tz.localize(source_time)
        target_time = source_time.astimezone(target_tz)
        
        # Generate hints
        self.current_hints = [
            f"From: {self.timezone_hints[from_tz]}",
            f"To: {self.timezone_hints[to_tz]}",
            f"Tip: The time difference is {target_time.hour - source_time.hour} hours"
        ]
        
        self.current_hint_index = 0
        
        return {
            'from_tz': from_tz,
            'to_tz': to_tz,
            'source_time': source_time,
            'correct_answer': target_time
        }

    def check_answer(self, answer):
        try:
            hour, minute = map(int, answer.split(':'))
            if 0 <= hour < 24 and minute in [0, 30]:
                correct_time = self.current_question['correct_answer']
                return hour == correct_time.hour and minute == correct_time.minute
        except:
            pass
        return False

    def draw(self):
        self.screen.fill(WHITE)
        
        # Draw question
        question_text = (f"Convert {self.current_question['source_time'].strftime('%H:%M')} from "
                        f"{self.current_question['from_tz'].split('/')[-1]} to "
                        f"{self.current_question['to_tz'].split('/')[-1]}")
        
        text_surface = self.font.render(question_text, True, BLACK)
        self.screen.blit(text_surface, (50, 50))
        
        # Draw score
        score_text = f"Score: {self.score} | Question: {self.questions_asked}/{self.max_questions}"
        score_surface = self.font.render(score_text, True, BLACK)
        self.screen.blit(score_surface, (50, 100))
        
        # Draw hints
        hint_y = 150
        for i in range(self.current_hint_index):
            hint_surface = self.small_font.render(self.current_hints[i], True, BLUE)
            self.screen.blit(hint_surface, (50, hint_y))
            hint_y += 30
        
        # Draw feedback
        if self.feedback_message:
            feedback_surface = self.font.render(self.feedback_message, True, self.feedback_color)
            self.screen.blit(feedback_surface, (50, 300))
        
        # Draw UI elements
        self.input_box.draw(self.screen)
        self.hint_button.draw(self.screen)
        self.submit_button.draw(self.screen)
        self.next_button.draw(self.screen)
        
        pygame.display.flip()

    def run(self):
        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                
                # Handle input box
                answer = self.input_box.handle_event(event)
                if answer:
                    self.check_and_update(answer)
                
                # Handle buttons
                if self.hint_button.handle_event(event):
                    if self.current_hint_index < len(self.current_hints):
                        self.current_hint_index += 1
                        self.hints_used += 1
                
                if self.submit_button.handle_event(event):
                    self.check_and_update(self.input_box.text)
                
                if self.next_button.handle_event(event):
                    if self.questions_asked < self.max_questions:
                        self.next_question()
                    else:
                        self.show_final_score()
                        running = False
            
            self.draw()
            self.clock.tick(FPS)
        
        # Show final score for 3 seconds before closing
        if self.questions_asked >= self.max_questions:
            time.sleep(3)
        
        pygame.quit()

    def check_and_update(self, answer):
        if self.check_answer(answer):
            points = 3 - self.current_hint_index
            self.score += max(1, points)
            self.feedback_message = f"Correct! +{max(1, points)} points"
            self.feedback_color = GREEN
            if self.questions_asked >= self.max_questions:
                self.show_final_score()
        else:
            self.feedback_message = "Incorrect. Try again or use a hint"
            self.feedback_color = RED

    def next_question(self):
        self.questions_asked += 1
        self.current_question = self.generate_question()
        self.input_box.text = ""
        self.feedback_message = ""
        self.current_hint_index = 0

    def show_final_score(self):
        self.screen.fill(WHITE)
        
        # Display final score
        score_text = f"Final Score: {self.score}/{self.max_questions * 3}"
        score_surface = self.font.render(score_text, True, BLACK)
        score_rect = score_surface.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 - 50))
        self.screen.blit(score_surface, score_rect)
        
        # Display rating
        performance = (self.score / (self.max_questions * 3)) * 100
        if performance >= 90:
            rating = "Outstanding! You're a timezone master!"
        elif performance >= 70:
            rating = "Great job! You're getting really good at this!"
        elif performance >= 50:
            rating = "Good effort! Keep practicing!"
        else:
            rating = "Practice makes perfect! Try again!"
        
        rating_surface = self.font.render(rating, True, BLUE)
        rating_rect = rating_surface.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 + 50))
        self.screen.blit(rating_surface, rating_rect)
        
        pygame.display.flip()

if __name__ == "__main__":
    game = TimezoneGame()
    game.run()