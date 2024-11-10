import pygame
import os
import random
import string
from sprites import Spritesheet

# Initialize Pygame
pygame.init()

# Game Constants
WIDTH, HEIGHT = 960, 540
WIN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("BOSS BATTLE!!")
FPS = 60
BOSS_VEL = random.randint(7, 10)
VEL = 7
BOSS_BULLET_VEL = 8
BULLET_VEL = 12
MAG = 3  # Bullets allowed at a time
BULLETSIZE = 32  # Added for bullet size consistency

# Sprite Dimensions
PLAYER_WIDTH, PLAYER_HEIGHT = 30, 48  # Modified to match main game sprite size
BOSS_WIDTH, BOSS_HEIGHT = 170, 170

# Load and transform boss sprite
BOSS_SPRITE_IMAGE = pygame.image.load(os.path.join('LEGEND OF ZAHIR/assets/graphics/sprites/boss 3_3 sprite.PNG'))
BOSS_SPRITE = pygame.transform.rotate(pygame.transform.scale(BOSS_SPRITE_IMAGE, (BOSS_WIDTH, BOSS_HEIGHT)), 360)

PLAYER_HEALTH_IMAGE = pygame.image.load(os.path.join('LEGEND OF ZAHIR/Minigame 5 Assets/Player health icon.png'))
PLAYER_HEALTH = pygame.transform.scale(PLAYER_HEALTH_IMAGE, (50, 50))

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

# Player Animation Setup
class Player(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.character_spritesheet = Spritesheet('LEGEND OF ZAHIR/main character strip.png')
        
        # Create animation dictionaries
        self.animations = {
            'down': [self.character_spritesheet.get_sprite(3, 3, 15, 26),
                    self.character_spritesheet.get_sprite(24, 3, 15, 26)],
            'up': [self.character_spritesheet.get_sprite(87, 3, 15, 26),
                  self.character_spritesheet.get_sprite(108, 3, 15, 26)],
            'left': [self.character_spritesheet.get_sprite(131, 3, 11, 29),
                    self.character_spritesheet.get_sprite(151, 3, 11, 30)],
            'right': [self.character_spritesheet.get_sprite(46, 3, 11, 29),
                     self.character_spritesheet.get_sprite(68, 3, 11, 30)]
        }
        
        # Scale all animation frames
        for direction in self.animations:
            self.animations[direction] = [pygame.transform.scale(img, (PLAYER_WIDTH, PLAYER_HEIGHT)) 
                                       for img in self.animations[direction]]
        
        self.facing = 'right'
        self.animation_loop = 0
        self.animation_speed = 0.1
        self.last_update = pygame.time.get_ticks()
        
        self.image = self.animations[self.facing][0]
        self.rect = pygame.Rect(x, y, PLAYER_WIDTH, PLAYER_HEIGHT)

    def animate(self):
        now = pygame.time.get_ticks()
        if now - self.last_update > self.animation_speed * 1000:
            self.last_update = now
            self.animation_loop = (self.animation_loop + 1) % len(self.animations[self.facing])
            self.image = self.animations[self.facing][self.animation_loop]

class Bullet(pygame.sprite.Sprite):
    def __init__(self, x, y, direction):
        super().__init__()
        try:
            self.original_image = pygame.image.load('LEGEND OF ZAHIR/fireball.png').convert_alpha()
            self.original_image = pygame.transform.scale(self.original_image, (BULLETSIZE, BULLETSIZE))
        except pygame.error:
            self.original_image = pygame.Surface((BULLETSIZE, BULLETSIZE))
            self.original_image.fill((255, 165, 0))
            
        self.image = self.original_image
        self.rect = self.image.get_rect(center=(x, y))
        self.direction = direction
        self.speed = BULLET_VEL
        
        # Add sound effect
        try:
            self.shoot_sound = pygame.mixer.Sound('LEGEND OF ZAHIR/assets/sounds/sfx/fireball.mp3')
            self.shoot_sound.play()
        except:
            print("Could not load bullet sound")

    def update(self):
        self.rect.x += self.direction[0] * self.speed
        self.rect.y += self.direction[1] * self.speed
        
        # Rotate bullet to face direction
        angle = pygame.math.Vector2(self.direction).angle_to((1, 0))
        self.image = pygame.transform.rotate(self.original_image, angle)
        self.rect = self.image.get_rect(center=self.rect.center)

class BossBullet(pygame.sprite.Sprite):
    def __init__(self, x, y, direction):
        super().__init__()
        try:
            # Load and scale the boss bullet image
            self.original_image = pygame.image.load('LEGEND OF ZAHIR/purple (2).png').convert_alpha()
            self.original_image = pygame.transform.scale(self.original_image, (50, 50))
        except pygame.error:
            # Fallback if image loading fails
            print("Could not load boss bullet image - using default shape")
            self.original_image = pygame.Surface((30, 30), pygame.SRCALPHA)
            pygame.draw.circle(self.original_image, (255, 0, 0), (15, 15), 15)
            
        self.image = self.original_image
        self.rect = self.image.get_rect(center=(x, y))
        self.dx = direction[0]
        self.dy = direction[1]
        
        # Calculate angle for rotation
        angle = pygame.math.Vector2(direction).angle_to((1, 0))
        self.image = pygame.transform.rotate(self.original_image, angle)
        self.rect = self.image.get_rect(center=self.rect.center)

    def update(self):
        self.rect.x += self.dx
        self.rect.y += self.dy

def create_text_input(shuffled_word):
    """
    Create a text input popup surface for the word unscrambling game.
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
    """Draw the game window with all elements."""
    WIN.blit(BACKGROUND, (0, 0))
    WIN.blit(player.image, player.rect)
    WIN.blit(BOSS_SPRITE, (boss.x, boss.y))

    # Draw bullets
    for bullet in playerBullets:
        WIN.blit(bullet.image, bullet.rect)
    for bullet in bossBullets:  # Changed from tuple unpacking to direct sprite usage
        WIN.blit(bullet.image, bullet.rect)

    # Draw health
    for i in range(player_hp):
        WIN.blit(PLAYER_HEALTH, (775 + i * 45, 10))
    pygame.draw.rect(WIN, RED, (WIDTH - 950, 10, 200, 20))
    pygame.draw.rect(WIN, GREEN, (WIDTH - 950, 10, 200 * (boss_hp / 100), 20))

    if popup:
        WIN.blit(popup, (WIDTH//2 - 300, HEIGHT//2 - 100))
        input_surface = FONT.render(player_input, True, BLACK)
        WIN.blit(input_surface, (WIDTH//2 - input_surface.get_width()//2, HEIGHT//2 + 20))

    if game_over:
        game_over_text = "YOU WIN!" if win else "DEFEAT"
        game_over_surface = FONT.render(game_over_text, True, WHITE)
        WIN.blit(game_over_surface, (WIDTH//2 - game_over_surface.get_width()//2, 
                                   HEIGHT//2 - game_over_surface.get_height()//2))

    pygame.display.update()

def player_movement(keys_pressed, player):
    """Handle player movement and animation."""
    moved = False
    if keys_pressed[pygame.K_a] and player.rect.x - VEL > WALL.x:  # left
        player.rect.x -= VEL
        player.facing = 'left'
        moved = True
    if keys_pressed[pygame.K_d] and player.rect.x + VEL + player.rect.width < WIDTH:  # right
        player.rect.x += VEL
        player.facing = 'right'
        moved = True
    if keys_pressed[pygame.K_w] and player.rect.y - VEL > 0:  # up
        player.rect.y -= VEL
        player.facing = 'up'
        moved = True
    if keys_pressed[pygame.K_s] and player.rect.y + VEL + player.rect.height < HEIGHT:  # down
        player.rect.y += VEL
        player.facing = 'down'
        moved = True
        
    if moved:
        player.animate()
    else:
        player.image = player.animations[player.facing][0]

def boss_movement(boss):
    """Handle random boss movement."""
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
    """Handle player bullet movement and collision."""
    for bullet in playerBullets[:]:
        bullet.update()
        
        # Check if bullet is out of bounds
        if bullet.rect.right < 0 or bullet.rect.left > WIDTH or \
           bullet.rect.bottom < 0 or bullet.rect.top > HEIGHT:
            playerBullets.remove(bullet)
            continue
            
        # Check for collision with boss
        boss_rect = pygame.Rect(boss.x, boss.y, BOSS_WIDTH, BOSS_HEIGHT)
        if boss_rect.colliderect(bullet.rect):
            pygame.event.post(pygame.event.Event(BOSS_HIT))
            playerBullets.remove(bullet)

def boss_shooting(bossBullets, boss):
    """Create boss bullets in a circular pattern."""
    if random.randint(1, 90) == 1:  # Random chance to shoot
        for angle in range(0, 360, 45):  # 8 directions
            # Calculate direction vector
            direction = pygame.math.Vector2(1, 0).rotate(angle)
            dx = BOSS_BULLET_VEL * direction.x
            dy = BOSS_BULLET_VEL * direction.y
            
            # Create new bullet at boss center
            bullet = BossBullet(
                boss.x + boss.width // 2,
                boss.y + boss.height // 2,
                (dx, dy)
            )
            bossBullets.append(bullet)

def update_boss_shooting(bossBullets, player):
    """Update boss bullet positions and handle collisions."""
    for bullet in bossBullets[:]:
        bullet.update()
        
        # Check for collision with player
        if player.rect.colliderect(bullet.rect):
            pygame.event.post(pygame.event.Event(PLAYER_HIT))
            bossBullets.remove(bullet)
            continue
            
        # Remove bullets that are off screen
        if not bullet.rect.colliderect(pygame.Rect(0, 0, WIDTH, HEIGHT)):
            bossBullets.remove(bullet)

def generate_word():
    """Generate a random Southeast Asian country name and its scrambled version."""
    wordList = ['PHILIPPINES', 'LAOS', 'SINGAPORE', 'THAILAND', 'VIETNAM', 
                'CAMBODIA', 'TIMOR LESTE', 'MYANMAR', 'BRUNEI', 'MALAYSIA', 'INDONESIA']
    word = random.choice(wordList)
    shuffled = ''.join(random.sample(word, len(word)))
    return word, shuffled

def main():
    """Main game loop for the boss battle."""
    # Initialize game objects
    boss = pygame.Rect(100, 300, BOSS_WIDTH, BOSS_HEIGHT)
    player = Player(700, 300)

    # Initialize game state
    playerBullets = []
    bossBullets = []  # Now stores BossBullet sprites
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

            elif can_shoot and event.type == pygame.MOUSEBUTTONDOWN and event.button == 1 and bullets_fired < MAG:
                # Calculate direction vector
                mouse_x, mouse_y = pygame.mouse.get_pos()
                start_pos = (player.rect.centerx, player.rect.centery)
                direction = pygame.math.Vector2(mouse_x - start_pos[0], mouse_y - start_pos[1])
                if direction.length() > 0:
                    direction = direction.normalize()
                    bullet = Bullet(start_pos[0], start_pos[1], (direction.x, direction.y))
                    playerBullets.append(bullet)
                    bullets_fired += 1
                    if bullets_fired == MAG:
                        can_shoot = False

            if event.type == BOSS_HIT:
                boss_hp -= 10
            if event.type == PLAYER_HIT:
                player_hp -= 1

        # Check win/lose conditions
        if player_hp <= 0 or boss_hp <= 0:
            draw_window(player, boss, playerBullets, bossBullets, player_hp, boss_hp, 
                       shuffled_word, player_input, game_over=True, win=boss_hp <= 0)
            pygame.time.delay(3000)
            return "completed" if boss_hp <= 0 else "died"

        # Update game state when popup is not active
        if not popup_active:
            player_movement(keys_pressed, player)
            shooting(playerBullets, player, boss)
            boss_movement(boss)
            if not popup_active:  # Only shoot when popup is not active
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