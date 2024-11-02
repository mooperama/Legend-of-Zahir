import pygame
import os
import random
import string

# Initialize Pygame
pygame.init()

# Game Constants
WIDTH, HEIGHT = 960, 540
WIN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("BOSS BATTLE!!")
FPS = 60
BOSS_VEL = random.randint(7, 10)
VEL = 7
BOSS_BULLET_VEL = 10
BULLET_VEL = 12
MAG = 3  # Bullets allowed at a time

# Sprite Dimensions
PLAYER_WIDTH, PLAYER_HEIGHT = 100, 100
BOSS_WIDTH, BOSS_HEIGHT = 170, 170

# Load and transform sprites
PLAYER_SPRITE_IMAGE = pygame.image.load(os.path.join('LEGEND OF ZAHIR/Minigame 5 Assets', 'Player Sprite.png'))
PLAYER_SPRITE = pygame.transform.rotate(pygame.transform.scale(PLAYER_SPRITE_IMAGE, (PLAYER_WIDTH, PLAYER_HEIGHT)), 90)

BOSS_SPRITE_IMAGE = pygame.image.load(os.path.join('LEGEND OF ZAHIR/Minigame 5 Assets/Boss Sprite.png'))
BOSS_SPRITE = pygame.transform.rotate(pygame.transform.scale(BOSS_SPRITE_IMAGE, (BOSS_WIDTH, BOSS_HEIGHT)), 270)

PLAYER_HEALTH_IMAGE = pygame.image.load(os.path.join('LEGEND OF ZAHIR/Minigame 5 Assets/Player health icon.jpg'))
PLAYER_HEALTH = pygame.transform.scale(PLAYER_HEALTH_IMAGE, (30, 30))

# Colors
BLUE = (25, 118, 210)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
YELLOW = (255, 255, 0)
GREEN = (0, 255, 0)
POPUP_COLOR = (0, 0, 0, 128)

# Game Elements
WALL = pygame.Rect(WIDTH // 2 - 10, 0, 10, HEIGHT)
BACKGROUND = pygame.transform.scale(pygame.image.load(
    os.path.join('LEGEND OF ZAHIR/Minigame 5 Assets/Alt Dungeon Background.png')), (WIDTH, HEIGHT))

# Custom Events
BOSS_HIT = pygame.USEREVENT + 1
PLAYER_HIT = pygame.USEREVENT + 2

# Font and Timing Settings
FONT = pygame.font.Font('LEGEND OF ZAHIR/assets/fonts/nokiafc22.ttf', 30)
POPUP_DURATION = 8000  # 8 seconds
SHOOTING_PHASE_DURATION = 10000  # 10 seconds

def create_text_input(shuffled_word):
    """
    Create a text input popup surface for the word unscrambling game.
    
    Args:
        shuffled_word (str): The scrambled word to display
        
    Returns:
        pygame.Surface: The rendered popup surface
    """
    popup = pygame.Surface((600, 200))
    popup.fill(WHITE)
    pygame.draw.rect(popup, BLACK, popup.get_rect(), 5)

    font = pygame.font.Font('LEGEND OF ZAHIR/assets/fonts/nokiafc22.ttf', 20)
    text1 = font.render("Unscramble the Southeast Asian", True, BLACK)
    text2 = font.render("country to unlock 3 bullets:", True, BLACK)
    text3 = font.render(f"{shuffled_word}", True, BLACK)

    popup.blit(text1, (popup.get_width() // 2 - text1.get_width() // 2, 20))
    popup.blit(text2, (popup.get_width() // 2 - text2.get_width() // 2, 50))
    popup.blit(text3, (popup.get_width() // 2 - text3.get_width() // 2, 80))

    return popup

def draw_window(player, boss, playerBullets, bossBullets, player_hp, boss_hp, 
                shuffled_word, player_input, popup=None, game_over=False, win=False):
    """
    Draw the game window with all elements.
    
    Args:
        player (pygame.Rect): Player rectangle
        boss (pygame.Rect): Boss rectangle
        playerBullets (list): List of player bullet rectangles
        bossBullets (list): List of boss bullet tuples (rect, dx, dy)
        player_hp (int): Player health
        boss_hp (int): Boss health
        shuffled_word (str): Current scrambled word
        player_input (str): Current player input
        popup (pygame.Surface, optional): Popup surface. Defaults to None.
        game_over (bool, optional): Whether game is over. Defaults to False.
        win (bool, optional): Whether player won. Defaults to False.
    """
    WIN.blit(BACKGROUND, (0, 0))
    WIN.blit(PLAYER_SPRITE, (player.x, player.y))
    WIN.blit(BOSS_SPRITE, (boss.x, boss.y))

    # Draw bullets
    for bullet in playerBullets:
        pygame.draw.rect(WIN, RED, bullet)
    for bullet, dx, dy in bossBullets:
        pygame.draw.rect(WIN, YELLOW, bullet)

    # Draw health
    for i in range(player_hp):
        WIN.blit(PLAYER_HEALTH, (775 + i * 45, 10))
    pygame.draw.rect(WIN, RED, (WIDTH - 950, 10, 200, 20))
    pygame.draw.rect(WIN, GREEN, (WIDTH - 950, 10, 200 * (boss_hp / 100), 20))

    # Draw popup if active
    if popup:
        WIN.blit(popup, (WIDTH//2 - 300, HEIGHT//2 - 100))
        input_surface = FONT.render(player_input, True, BLACK)
        WIN.blit(input_surface, (WIDTH//2 - input_surface.get_width()//2, HEIGHT//2 + 20))

    # Draw game over text
    if game_over:
        game_over_text = "YOU WIN!" if win else "DEFEAT"
        game_over_surface = FONT.render(game_over_text, True, WHITE)
        WIN.blit(game_over_surface, (WIDTH//2 - game_over_surface.get_width()//2, 
                                   HEIGHT//2 - game_over_surface.get_height()//2))

    pygame.display.update()

def player_movement(keys_pressed, player):
    """
    Handle player movement based on keyboard input.
    
    Args:
        keys_pressed (pygame.key.ScancodeWrapper): Current keyboard state
        player (pygame.Rect): Player rectangle
    """
    if keys_pressed[pygame.K_a] and player.x - VEL > WALL.x:  # left
        player.x -= VEL
    if keys_pressed[pygame.K_d] and player.x + VEL + player.width < WIDTH:  # right
        player.x += VEL
    if keys_pressed[pygame.K_w] and player.y - VEL > 0:  # up
        player.y -= VEL
    if keys_pressed[pygame.K_s] and player.y + VEL + player.height < HEIGHT:  # down
        player.y += VEL

def boss_movement(boss):
    """
    Handle random boss movement.
    
    Args:
        boss (pygame.Rect): Boss rectangle
    """
    direction = random.choice(['up', 'down', 'left', 'right'])
    if direction == 'up' and boss.y > 0:
        boss.y -= BOSS_VEL
    elif direction == 'down' and boss.y + boss.height < HEIGHT:
        boss.y += BOSS_VEL
    elif direction == 'left' and boss.x > 0:
        boss.x -= BOSS_VEL
    elif direction == 'right' and boss.x + boss.width < WALL.x:
        boss.x += BOSS_VEL

def shooting(playerBullets, player, boss):
    """
    Handle player bullet movement and collision.
    
    Args:
        playerBullets (list): List of player bullet rectangles
        player (pygame.Rect): Player rectangle
        boss (pygame.Rect): Boss rectangle
    """
    for bullet in playerBullets[:]:
        bullet.x -= BULLET_VEL
        if boss.colliderect(bullet):
            pygame.event.post(pygame.event.Event(BOSS_HIT))
            playerBullets.remove(bullet)
        elif bullet.x < 0:
            playerBullets.remove(bullet)

def boss_shooting(bossBullets, boss):
    """
    Create boss bullets in a circular pattern.
    
    Args:
        bossBullets (list): List of boss bullet tuples (rect, dx, dy)
        boss (pygame.Rect): Boss rectangle
    """
    if random.randint(1, 90) == 1:
        for angle in range(0, 360, 45):
            dx = BOSS_BULLET_VEL * pygame.math.Vector2(1, 0).rotate(angle).x
            dy = BOSS_BULLET_VEL * pygame.math.Vector2(1, 0).rotate(angle).y
            bullet = pygame.Rect(boss.x + boss.width // 2, boss.y + boss.height//2, 30, 30)
            bossBullets.append((bullet, dx, dy))

def update_boss_shooting(bossBullets, player):
    """
    Update boss bullet positions and handle collisions.
    
    Args:
        bossBullets (list): List of boss bullet tuples (rect, dx, dy)
        player (pygame.Rect): Player rectangle
    """
    for bullet, dx, dy in bossBullets[:]:
        bullet.x += dx
        bullet.y += dy
        if player.colliderect(bullet):
            pygame.event.post(pygame.event.Event(PLAYER_HIT))
            bossBullets.remove((bullet, dx, dy))
        elif not bullet.colliderect(pygame.Rect(0, 0, WIDTH, HEIGHT)):
            bossBullets.remove((bullet, dx, dy))

def generate_word():
    """
    Generate a random Southeast Asian country name and its scrambled version.
    
    Returns:
        tuple: (original word, scrambled word)
    """
    wordList = ['PHILIPPINES', 'LAOS', 'SINGAPORE', 'THAILAND', 'VIETNAM', 
                'CAMBODIA', 'TIMOR LESTE', 'MYANMAR', 'BRUNEI', 'MALAYSIA', 'INDONESIA']
    word = random.choice(wordList)
    shuffled = ''.join(random.sample(word, len(word)))
    return word, shuffled

def main():
    """
    Main game loop for the boss battle.
    
    Returns:
        str: Game outcome - "completed" for victory, "died" for defeat, "quit" for exit
    """
    # Initialize game objects
    boss = pygame.Rect(100, 300, BOSS_WIDTH, BOSS_HEIGHT)
    player = pygame.Rect(700, 300, PLAYER_WIDTH, PLAYER_HEIGHT)

    # Initialize game state
    playerBullets = []
    bossBullets = []
    player_hp = 4
    boss_hp = 100
    clock = pygame.time.Clock()
    run = True

    # Initialize word game state
    word, shuffled_word = generate_word()
    player_input = ""
    can_shoot = False
    bullets_fired = 0

    # Initialize timing
    popup_active = True
    popup_start_time = pygame.time.get_ticks()
    shooting_phase_start_time = 0

    while run:
        clock.tick(FPS)
        current_time = pygame.time.get_ticks()
        keys_pressed = pygame.key.get_pressed()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return "quit"

            # Handle word puzzle input
            if popup_active:
                if event.type == pygame.KEYDOWN:
                    if event.unicode.isalpha():
                        player_input += event.unicode.upper()
                    elif event.key == pygame.K_BACKSPACE:
                        player_input = player_input[:-1]
                    elif event.key == pygame.K_SPACE:
                        player_input += " "
                    elif event.key == pygame.K_RETURN:
                        if player_input == word:
                            can_shoot = True
                            bullets_fired = 0
                            popup_active = False
                            shooting_phase_start_time = current_time
                        else:
                            player_hp -= 1
                        player_input = ""
                        popup_active = False

            # Handle shooting
            elif can_shoot and event.type == pygame.MOUSEBUTTONDOWN and event.button == 1 and bullets_fired < MAG:
                bullet = pygame.Rect(player.x - player.width, player.y + player.height // 2 - 2, 40, 15)
                playerBullets.append(bullet)
                bullets_fired += 1
                if bullets_fired == MAG:
                    can_shoot = False

            # Handle hits
            if event.type == BOSS_HIT:
                boss_hp -= 10
            if event.type == PLAYER_HIT:
                player_hp -= 1

        # Check win/lose conditions
        if player_hp <= 0 or boss_hp <= 0:
            draw_window(player, boss, playerBullets, bossBullets, player_hp, boss_hp, 
                       shuffled_word, player_input, game_over=True, win=boss_hp <= 0)
            pygame.time.delay(3000)  # Show end screen for 3 seconds
            # Return game outcome instead of quitting
            return "completed" if boss_hp <= 0 else "died"

        # Update game state when popup is not active
        if not popup_active:
            player_movement(keys_pressed, player)
            shooting(playerBullets, player, boss)
            boss_movement(boss)
            boss_shooting(bossBullets, boss)
            update_boss_shooting(bossBullets, player)

        # Handle popup timing
        if popup_active and current_time - popup_start_time >= POPUP_DURATION:
            popup_active = False
            player_hp -= 1
            shooting_phase_start_time = current_time

        # Start new word puzzle after shooting phase
        if not popup_active and not can_shoot and current_time - shooting_phase_start_time >= SHOOTING_PHASE_DURATION:
            popup_active = True
            popup_start_time = current_time
            word, shuffled_word = generate_word()
            player_input = ""

        # Draw current game state
        popup = create_text_input(shuffled_word) if popup_active else None
        draw_window(player, boss, playerBullets, bossBullets, player_hp, boss_hp, 
                   shuffled_word, player_input, popup)

    return "quit"

if __name__ == "__main__":
    result = main()
    pygame.quit()