import pygame
import random
from config_settings import *

# Initialize Pygame
pygame.init()

# Set up the display
WIDTH, HEIGHT = 1366, 768
SCREEN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Language Matching Memory Game")

# Card dimensions
CARD_WIDTH, CARD_HEIGHT = 140, 100
CARD_MARGIN = 15

# Font
FONT = pygame.font.Font('LEGEND OF ZAHIR/assets/fonts/nokiafc22.ttf', 15)
TIMER_FONT = pygame.font.Font('LEGEND OF ZAHIR/assets/fonts/nokiafc22.ttf', 40)

# Updated colors to match dark theme
DARK_PURPLE = (48, 25, 52)  # Dark background color
LIGHT_PURPLE = (120, 100, 140)  # Lighter purple for unrevealed cards
REVEALED_PURPLE = (80, 60, 100)  # Medium purple for revealed cards
TEXT_COLOR = (200, 190, 220)  # Light purple/white for text
BORDER_COLOR = (150, 130, 170)  # Medium light purple for borders

# Language pairs
ALL_LANGUAGES = [
    ("English", "Hello"),
    ("Spanish", "Hola"),
    ("French", "Bonjour"),
    ("German", "Hallo"),
    ("Italian", "Ciao"),
    ("Japanese", "Konnichiwa"),
    ("Mandarin", "Ni hao"),
    ("Tagalog", "Kumusta"),
    ("Hindi", "Namaste"),
    ("Portuguese", "Olá")
]

class Card:
    def __init__(self, x, y, text):
        self.rect = pygame.Rect(x, y, CARD_WIDTH, CARD_HEIGHT)
        self.text = text
        self.revealed = False

    def draw(self, screen):
        if self.revealed:
            pygame.draw.rect(screen, REVEALED_PURPLE, self.rect)
            text_surface = FONT.render(self.text, True, TEXT_COLOR)
        else:
            pygame.draw.rect(screen, LIGHT_PURPLE, self.rect)
            text_surface = FONT.render("?", True, TEXT_COLOR)
        
        # Add border
        pygame.draw.rect(screen, BORDER_COLOR, self.rect, 2)
        text_rect = text_surface.get_rect(center=self.rect.center)
        screen.blit(text_surface, text_rect)

def create_cards():
    game_languages = random.sample(ALL_LANGUAGES, 6)
    cards = []

    all_texts = game_languages + [(hello, lang) for lang, hello in game_languages]
    random.shuffle(all_texts)
    
    grid_width = 4 * (CARD_WIDTH + CARD_MARGIN) - CARD_MARGIN
    grid_height = 3 * (CARD_HEIGHT + CARD_MARGIN) - CARD_MARGIN
    
    start_x = (WIDTH - grid_width) // 2
    start_y = (HEIGHT - grid_height) // 2
    
    for i, (text1, text2) in enumerate(all_texts):
        row, col = divmod(i, 4)
        x = start_x + col * (CARD_WIDTH + CARD_MARGIN)
        y = start_y + row * (CARD_HEIGHT + CARD_MARGIN)
        cards.append(Card(x, y, text1))
    
    return cards, game_languages

def run_language_matching_game():
    # Load and scale background image
    bg_img = pygame.image.load('LEGEND OF ZAHIR/assets/backgrounds/Language background.jpg')
    bg_img = pygame.transform.scale(bg_img, (WIDTH, HEIGHT))
    
    # Create semi-transparent overlay
    overlay = pygame.Surface((WIDTH, HEIGHT))
    overlay.fill(DARK_PURPLE)
    overlay.set_alpha(150)  # More transparent to show background better
    
    cards, game_languages = create_cards()
    selected_cards = []
    matched_pairs = set()
    clock = pygame.time.Clock()
    running = True
    start_time = pygame.time.get_ticks()
    time_limit = 60000  # 60 seconds

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return "quit"
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                for card in cards:
                    if card.rect.collidepoint(event.pos) and not card.revealed and len(selected_cards) < 2:
                        card.revealed = True
                        selected_cards.append(card)
                        if len(selected_cards) == 2:
                            pygame.time.set_timer(pygame.USEREVENT, 1000)
            elif event.type == pygame.USEREVENT:
                pygame.time.set_timer(pygame.USEREVENT, 0)
                if len(selected_cards) == 2:
                    if (selected_cards[0].text, selected_cards[1].text) in game_languages or \
                       (selected_cards[1].text, selected_cards[0].text) in game_languages:
                        matched_pairs.add(frozenset([selected_cards[0].text, selected_cards[1].text]))
                    else:
                        for card in selected_cards:
                            card.revealed = False
                    selected_cards.clear()

        # Draw background and overlay
        SCREEN.blit(bg_img, (0, 0))
        SCREEN.blit(overlay, (0, 0))

        for card in cards:
            card.draw(SCREEN)

        # Timer logic with updated colors
        elapsed_time = pygame.time.get_ticks() - start_time
        remaining_time = max(0, (time_limit - elapsed_time) // 1000)
        timer_color = (255, 100, 100) if remaining_time <= 5 else TEXT_COLOR  # Red for low time
        timer_text = TIMER_FONT.render(f"Time: {remaining_time}s", True, timer_color)
        timer_rect = timer_text.get_rect(center=(WIDTH // 2, 50))
        SCREEN.blit(timer_text, timer_rect)

        pygame.display.flip()
        clock.tick(60)

        if len(matched_pairs) == len(game_languages):
            return "completed"
        elif remaining_time == 0:
            return "died"

    return "quit"

def main():
    return run_language_matching_game()

if __name__ == "_main_":
    result = main()
    print(f"Game result: {result}")
    pygame.quit()