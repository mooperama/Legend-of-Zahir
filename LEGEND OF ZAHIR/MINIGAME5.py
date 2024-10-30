import pygame
import os
import random
import string

pygame.init()

#HELLOOOO DO U SEE THIS NYEHEHE 

# CONSTANTS
WIDTH, HEIGHT = 960, 540
WIN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("BOSS BATTLE!!")
FPS = 60
BOSS_VEL = random.randint(7,10)
VEL = 7
BOSS_BULLET_VEL = 10
BULLET_VEL = 12
MAG = 3  # how many bullets can exist at a time

# CONSTANTS, ELEMENTS
PLAYER_SPEED = 90
PLAYER_WIDTH, PLAYER_HEIGHT = 100, 100
BOSS_WIDTH, BOSS_HEIGHT = 170, 170

PLAYER_SPRITE_IMAGE = pygame.image.load(os.path.join('LEGEND OF ZAHIR/Minigame 5 Assets', 'Player Sprite.png'))
PLAYER_SPRITE = pygame.transform.rotate(pygame.transform.scale(PLAYER_SPRITE_IMAGE, (PLAYER_WIDTH, PLAYER_HEIGHT)), 90)

BOSS_SPRITE_IMAGE = pygame.image.load(os.path.join('LEGEND OF ZAHIR/Minigame 5 Assets/Boss Sprite.png'))
BOSS_SPRITE = pygame.transform.rotate(pygame.transform.scale(BOSS_SPRITE_IMAGE, (BOSS_WIDTH, BOSS_HEIGHT)), 270)

PLAYER_HEALTH_IMAGE = pygame.image.load(os.path.join('LEGEND OF ZAHIR/Minigame 5 Assets/Player health icon.jpg'))
PLAYER_HEALTH = pygame.transform.scale(PLAYER_HEALTH_IMAGE, (30,30))

# COLORS
BLUE = (25, 118, 210)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
YELLOW = (255, 255, 0)
GREEN = (0, 255, 0)
POPUP_COLOR = (0, 0, 0, 128) #128 is opacity

# GAME ELEMENTS
WALL = pygame.Rect(WIDTH // 2 - 10, 0, 10, HEIGHT)
BACKGROUND = pygame.transform.scale(pygame.image.load(os.path.join('LEGEND OF ZAHIR/Minigame 5 Assets/Dungeon Background.png')), (WIDTH, HEIGHT))

BOSS_HIT = pygame.USEREVENT + 1
PLAYER_HIT = pygame.USEREVENT + 2

FONT = pygame.font.SysFont('comicsans', 40)

POPUP_DURATION = 8000 #8 Seconds (in miliseconds)
SHOOTING_PHASE_DURATION = 10000 #10 Seconds (in miliseconds)

def create_text_input(shuffled_word):
    '''
    1. Text input pop-up for the word game
    '''
    popup = pygame.Surface((600,200))
    popup.fill(WHITE)
    pygame.draw.rect(popup, BLACK, popup.get_rect(), 5)

    font = pygame.font.SysFont('comicsans', 30)
    text1 = font.render("Unscramble the Southeast Asian", True, BLACK)
    text2 = font.render("country to unlock 3 bullets:", True, BLACK)
    text3 = font.render(f"{shuffled_word}", True, BLACK)

    popup.blit(text1, (popup.get_width() // 2 - text1.get_width() // 2, 20))
    popup.blit(text2, (popup.get_width() // 2 - text2.get_width() // 2, 50))
    popup.blit(text3, (popup.get_width() // 2 - text3.get_width() // 2, 80))

    return popup

# DRAWING
def draw_window(player, boss, playerBullets, bossBullets, player_hp, boss_hp, shuffled_word, player_input, popup=None, game_over=False, win=False):
    """
    Draws the background, wall, player, and boss on to the screen
    """
    WIN.blit(BACKGROUND, (0, 0))
    pygame.draw.rect(WIN, BLACK, WALL)
    WIN.blit(PLAYER_SPRITE, (player.x, player.y))
    WIN.blit(BOSS_SPRITE, (boss.x, boss.y))

    #drawing bullets for player and boss
    for bullet in playerBullets:
        pygame.draw.rect(WIN, RED, bullet)

    for bullet, dx, dy in bossBullets:
        pygame.draw.rect(WIN, YELLOW, bullet)

    # HP for player
    for i in range (player_hp):
        WIN.blit(PLAYER_HEALTH, (775 + i * 45, 10))

    # HP bar for boss
    pygame.draw.rect(WIN, RED, (WIDTH - 950, 10, 200, 20))
    pygame.draw.rect(WIN, GREEN, (WIDTH - 950, 10, 200 * (boss_hp / 100), 20))

    #pop up **
    if popup:
        WIN.blit(popup, (WIDTH//2 - 300 , HEIGHT//2 - 100)) #popup location
        input_surface = FONT.render(player_input, True, BLACK) #player input
        WIN.blit(input_surface, (WIDTH//2 - input_surface.get_width()//2, HEIGHT//2 +20))

    #Game end
    if game_over:
        game_over_text = "YOU WIN!" if win else "DEFEAT"
        game_over_surface = FONT.render(game_over_text, True, WHITE)
        WIN.blit(game_over_surface, (WIDTH//2 - game_over_surface.get_width()//2, HEIGHT//2 - game_over_surface.get_height()//2))

    pygame.display.update()

# MOVEMENT
def player_movement(keys_pressed, player):
    """
    Checks if a key is pressed, and makes corresponding player movements 
    if certain keys are pressed.
    """
    if keys_pressed[pygame.K_a] and player.x - VEL > WALL.x:  # left
        player.x -= VEL
    if keys_pressed[pygame.K_d] and player.x + VEL + player.width < WIDTH :  # right
        player.x += VEL
    if keys_pressed[pygame.K_w] and player.y - VEL > 0:  # up
        player.y -= VEL
    if keys_pressed[pygame.K_s] and player.y + VEL + player.height < HEIGHT:  # down
        player.y += VEL

def boss_movement(boss):
    """
    Picks a random element from a list of 4 directions. 
    The boss will move accordingly.
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

# PLAYER SHOOTING
def shooting(playerBullets, player, boss):
    """
    1. Makes bullets move towards the boss
    2. Detects if the bullet hits/collides with the boss
    3. Removes the bullet from the player bullets list if:
        - the bullet hits the boss
        - the bullet is out of the field of view
    """
    for bullet in playerBullets:
        bullet.x -= BULLET_VEL
        if boss.colliderect(bullet):
            pygame.event.post(pygame.event.Event(BOSS_HIT))
            playerBullets.remove(bullet)
        elif bullet.x < 0:
            playerBullets.remove(bullet)

# BOSS SHOOTING
def boss_shooting(bossBullets, boss):
    '''
    Allows the boss to shoot:
        1. Makes the boss shoot every second
        2. Makes the boss shoot in a circular way
        3. Adds bullets to the bullet list (So we can keep track of where the bullets are and update them later)
    '''
    if random.randint(1,90) == 1:
        #1 in 90 chance to shoot per frame, when the boss shoots is random
        for angle in range (0, 360, 45): #8-directional shooting
            dx = BOSS_BULLET_VEL * pygame.math.Vector2(1, 0).rotate(angle).x
            dy = BOSS_BULLET_VEL * pygame.math.Vector2(1, 0).rotate(angle).y
            bullet = pygame.Rect(boss.x + boss.width // 2, boss.y + boss.height//2, 30, 30)
            bossBullets.append((bullet, dx, dy))

def update_boss_shooting(bossBullets, player):
    '''
    Updates the bossBullets list which we just made 
    so that we can track when a player is hit or if 
    the bullets go off the screen (removes from list)
    '''
    for bullet, dx, dy in bossBullets[:]:
        bullet.x += dx
        bullet.y += dy
        if player.colliderect(bullet):
            pygame.event.post(pygame.event.Event(PLAYER_HIT))
            bossBullets.remove((bullet, dx, dy)) 
            '''need the dx and dy to know which one because
            in one circular shot, there are multiple separate bullets'''
        elif not bullet.colliderect(pygame.Rect(0, 0, WIDTH, HEIGHT)):
            bossBullets.remove((bullet, dx, dy))
            
# WORD GAME
def generate_word():
    '''
    Generates shuffled for the word game
    '''
    wordList = ['PHILIPPINES', 'LAOS', 'SINGAPORE', 'THAILAND', 'VIETNAM', 'CAMBODIA', 'TIMOR LESTE', 'MYANMAR', 'BRUNEI', 'MALAYSIA', 'INDONESIA']
    word = random.choice(wordList)
    shuffled = ''.join(random.sample(word, len(word)))
    '''
    1. random.sample will make a new list of random elements from 'word'
    2. .join will join those togehter
    3. it will use 'word' and the len of 'word'
        - if we change the len(word) to 3 itll give 3 letters
        - we use len(word) to use all the elements of 'word'
    '''
    return word, shuffled

def main():
    boss = pygame.Rect(100, 300, BOSS_WIDTH, BOSS_HEIGHT)
    player = pygame.Rect(700, 300, PLAYER_WIDTH, PLAYER_HEIGHT)

    playerBullets = []
    bossBullets = [] 

    player_hp = 4
    boss_hp = 100

    clock = pygame.time.Clock()
    run = True

    word, shuffled_word = generate_word()
    player_input = ""
    can_shoot = False
    bullets_fired = 0 

    popup_active = True 
    popup_start_time = pygame.time.get_ticks() #start with it not active
    shooting_phase_start_time = 0

    while run:
        clock.tick(FPS)
        current_time = pygame.time.get_ticks()

        #Event handling
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False

            if popup_active: 
                """
                When the popup is active it should run this if statement,
                then the can shoot boolean will carry over 
                """
                #Controls for typing (caps, backspace, enter)
                if event.type == pygame.KEYDOWN:
                    #Makes all inputs all caps
                    if event.unicode.isalpha():
                        player_input += event.unicode.upper()
                    elif event.key == pygame.K_BACKSPACE:
                        player_input = player_input[:-1]
                    elif event.key == pygame.K_SPACE:
                        player_input += " "
                    elif event.key == pygame.K_RETURN:
                    #Entering the player input
                        if player_input == word:
                        #Setting up shooting if the input == word
                            can_shoot = True 
                            bullets_fired = 0
                            popup_active = False
                            shooting_phase_start_time = current_time
                        else: #if no input, or if input =! word
                            player_hp -= 1
                        player_input = ""
                        popup_active = False
            elif can_shoot == True and event.type ==  pygame.MOUSEBUTTONDOWN and event.button == 1 and bullets_fired < MAG:
                '''
                #player shooting
                CONDITIONS:
                1. Can_shoot will be updated based on while the popup was active
                2. Spacebar is pressed 
                3. Bullets < MAG (still have shots left)
                '''
                bullet = pygame.Rect(player.x - player.width, player.y + player.height // 2 - 2, 40, 15)
                #positional: left side of sprite, comes out from the middle of player, 40 pix wide, 15 pix tall
                playerBullets.append(bullet)
                bullets_fired += 1
                if bullets_fired == MAG:
                    can_shoot = False

            if event.type == BOSS_HIT:
                boss_hp -= 10

            if event.type == PLAYER_HIT:
                player_hp -= 1

        if player_hp <= 0 or boss_hp <= 0:
                draw_window(player, boss, playerBullets, bossBullets, player_hp, boss_hp, shuffled_word, player_input, game_over=True, win=boss_hp <=0)
                pygame.time.delay (3000) #show the screen for 3 seconds
                run = False

        keys_pressed = pygame.key.get_pressed()

        #OPPOSITE OF FREEZING GAME
        #Only allowing movement when popup is NOT active
        if not popup_active:
            player_movement(keys_pressed, player)
            shooting(playerBullets, player, boss)
            boss_movement(boss)
            boss_shooting(bossBullets, boss)
            update_boss_shooting(bossBullets, player)
            
        #Popup closing when time is up ** CHANGED FROM ACTIVE TO NOT ACTIVE
        '''
        Here we check if the amount of time that has passed since 
        the pop up opened is greater than the duration. If it is 
        greater than or equal we close the pop up
        '''
        if popup_active and current_time - popup_start_time >= POPUP_DURATION:
            popup_active = False
            player_hp -= 1 #lose 1 hp for not answering in time
            shooting_phase_start_time = current_time

        #popup again after shooting phase ** CHANGED FROM NOT ACTIVE TO ACTIVE
        if not popup_active and not can_shoot and current_time - shooting_phase_start_time >= SHOOTING_PHASE_DURATION:
            popup_active = True
            popup_start_time = current_time
            word, shuffled_word = generate_word()
            player_input = ""

        #create pop-up if active
        popup = create_text_input(shuffled_word) if popup_active else None

        draw_window(player, boss, playerBullets, bossBullets, player_hp, boss_hp, shuffled_word, player_input, popup)

    pygame.quit()

if __name__ == "__main__":
    main()