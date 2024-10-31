import pygame
import random
from config_settings import *

# Initialize Pygame
pygame.init()

# Set up the display
WIDTH, HEIGHT = 960, 720
SCREEN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Language Matching Memory Game")

# Card dimensions
CARD_WIDTH, CARD_HEIGHT = 140, 100
CARD_MARGIN = 15

# Font
FONT = pygame.font.Font(None, 36)
TIMER_FONT = pygame.font.Font(None, 48)

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
    """
    Represents a card in the memory game.
    """

    def __init__(self, x, y, text):
        """
        Initialize a new card.

        Args:
            x (int): The x-coordinate of the card.
            y (int): The y-coordinate of the card.
            text (str): The text to display on the card.
        """
        self.rect = pygame.Rect(x, y, CARD_WIDTH, CARD_HEIGHT)
        self.text = text
        self.revealed = False

    def draw(self, screen):
        """
        Draw the card on the screen.

        Args:
            screen (pygame.Surface): The surface to draw the card on.
        """
        if self.revealed:
            pygame.draw.rect(screen, BLUE, self.rect)
            text_surface = FONT.render(self.text, True, WHITE)
        else:
            pygame.draw.rect(screen, GRAY, self.rect)
            text_surface = FONT.render("?", True, BLACK)
        
        text_rect = text_surface.get_rect(center=self.rect.center)
        screen.blit(text_surface, text_rect)

def create_cards():
    """
    Create and return a list of Card objects and game languages.

    Returns:
        tuple: A tuple containing a list of Card objects and a list of game languages.
    """
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
    """
    Run the main game loop for the Language Matching Memory Game.

    Returns:
        str: The result of the game ('completed', 'died', or 'quit').
    """
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
                            pygame.time.set_timer(pygame.USEREVENT, 1000)  # Set timer for 1 second
            elif event.type == pygame.USEREVENT:
                pygame.time.set_timer(pygame.USEREVENT, 0)  # Cancel the timer
                if len(selected_cards) == 2:
                    if (selected_cards[0].text, selected_cards[1].text) in game_languages or \
                       (selected_cards[1].text, selected_cards[0].text) in game_languages:
                        matched_pairs.add(frozenset([selected_cards[0].text, selected_cards[1].text]))
                    else:
                        for card in selected_cards:
                            card.revealed = False
                    selected_cards.clear()

        SCREEN.fill(WHITE)
        for card in cards:
            card.draw(SCREEN)

        # Timer logic
        elapsed_time = pygame.time.get_ticks() - start_time
        remaining_time = max(0, (time_limit - elapsed_time) // 1000)  # Convert to seconds
        timer_text = TIMER_FONT.render(f"Time: {remaining_time}s", True, RED if remaining_time <= 5 else BLACK)
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
    """
    Main function to run the Language Matching Game when the script is run directly.
    
    Returns:
        str: The result of the game ('completed', 'died', or 'quit').
    """
    return run_language_matching_game()

if __name__ == "__main__":
    result = main()
    print(f"Game result: {result}")
    pygame.quit()