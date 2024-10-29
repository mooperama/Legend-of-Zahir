import pygame
import random
import time
from config_settings import *

# Initialize Pygame
pygame.init()

# Set up the display
WIDTH, HEIGHT = 400, 400
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Color Memory Game")

# Game variables
colors = [RED, GREEN, BLUE, YELLOW]
sequence = []
player_sequence = []
score = 0

# Functions
def draw_colored_circle(color, position):
    pygame.draw.circle(screen, color, position, 50)

def display_sequence():
    screen.fill(WHITE)
    for i, color in enumerate(sequence):
        draw_colored_circle(color, (100 + (i % 2) * 200, 100 + (i // 2) * 200))
        pygame.display.flip()
        time.sleep(0.5)
        screen.fill(WHITE)
        pygame.display.flip()
        time.sleep(0.2)

def get_clicked_color(pos):
    x, y = pos
    if 50 < x < 150 and 50 < y < 150:
        return RED
    elif 250 < x < 350 and 50 < y < 150:
        return GREEN
    elif 50 < x < 150 and 250 < y < 350:
        return BLUE
    elif 250 < x < 350 and 250 < y < 350:
        return YELLOW
    return None

# Main game loop
def main():
    global score  # Make score global so we can modify it
    running = True
    game_state = "show_sequence"

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN and game_state == "player_turn":
                clicked_color = get_clicked_color(event.pos)
                if clicked_color:
                    player_sequence.append(clicked_color)
                    if player_sequence[-1] != sequence[len(player_sequence) - 1]:
                        game_state = "game_over"
                    elif len(player_sequence) == len(sequence):
                        score += 1
                        player_sequence.clear()
                        game_state = "show_sequence"

        screen.fill(WHITE)

        if game_state == "show_sequence":
            sequence.append(random.choice(colors))
            display_sequence()
            game_state = "player_turn"
        elif game_state == "player_turn":
            draw_colored_circle(RED, (100, 100))
            draw_colored_circle(GREEN, (300, 100))
            draw_colored_circle(BLUE, (100, 300))
            draw_colored_circle(YELLOW, (300, 300))
        elif game_state == "game_over":
            font = pygame.font.Font(None, 36)
            text = font.render(f"Game Over! Score: {score}", True, BLACK)
            screen.blit(text, (WIDTH // 2 - text.get_width() // 2, HEIGHT // 2 - text.get_height() // 2))
            pygame.display.flip()
            time.sleep(3)
            running = False

        pygame.display.flip()

    pygame.quit()

if __name__ == "__main__":
    main()