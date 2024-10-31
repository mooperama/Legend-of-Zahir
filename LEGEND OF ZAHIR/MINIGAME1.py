import pygame
import random
import time
from config_settings import *
from player import *
from sprites import *

class Bullet(pygame.sprite.Sprite):
    def __init__(self, x, y, direction):
        super().__init__()
        self.image = pygame.Surface([BULLETSIZE, BULLETSIZE])
        self.image.fill(WHITE)
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        
        # Set speed and direction
        self.speed = 10
        self.dx = direction[0] * self.speed
        self.dy = direction[1] * self.speed
        
        # Store position as float for precise movement
        self.x = float(x)
        self.y = float(y)
        
    def update(self):
        self.x += self.dx
        self.y += self.dy
        self.rect.x = int(self.x)
        self.rect.y = int(self.y)

class MemoryGame:
    def __init__(self, screen, clock):
        self.screen = screen
        self.clock = clock
        
        # Load spritesheets
        self.character_spritesheet = Spritesheet('LEGEND OF ZAHIR/knight_strip.png')
        self.enemy_spritesheet = Spritesheet('LEGEND OF ZAHIR/skeleton_strip.png')
        self.terrain_spritesheet = Spritesheet('LEGEND OF ZAHIR/dungeon2.jpg')
        
        # Initialize sprite groups
        self.allsprites = pygame.sprite.LayeredUpdates()
        self.blocks = pygame.sprite.LayeredUpdates()
        self.enemies = pygame.sprite.LayeredUpdates()
        self.attacks = pygame.sprite.LayeredUpdates()
        self.bullets = pygame.sprite.LayeredUpdates()
        
        # Game state variables
        self.colors = [RED, GREEN, BLUE, YELLOW]
        self.sequence = []
        self.player_sequence = []
        self.score = 0
        self.game_state = "show_sequence"
        
        # Create the map
        self.create_map()
        
        # Square properties
        self.square_size = TILESIZE * 2
        self.squares = [
            pygame.Rect(TILESIZE, TILESIZE, self.square_size, self.square_size),
            pygame.Rect(WIDTH - TILESIZE * 3, TILESIZE, self.square_size, self.square_size),
            pygame.Rect(TILESIZE, HEIGHT - TILESIZE * 3, self.square_size, self.square_size),
            pygame.Rect(WIDTH - TILESIZE * 3, HEIGHT - TILESIZE * 3, self.square_size, self.square_size)
        ]
        self.square_colors = [RED, GREEN, BLUE, YELLOW]
        self.current_flash = None
        self.flash_start = time.time()
        self.flash_duration = 0.5
        self.sequence_index = 0

    def create_map(self):
        for i, row in enumerate(MEMORY_TILEMAP):
            for j, column in enumerate(row):
                if column == "W":
                    Block(self, j, i)
                elif column == "P":
                    self.player = Player(self, j, i)
                    self.allsprites.add(self.player)

    def display_sequence(self):
        current_time = time.time()
        
        if len(self.sequence) == 0:
            self.sequence = [random.randint(0, 3)]
            self.sequence_index = 0
            self.current_flash = self.sequence[0]
            self.flash_start = current_time
            self.player_sequence = []
        elif self.current_flash is None:
            if self.sequence_index < len(self.sequence):
                self.current_flash = self.sequence[self.sequence_index]
                self.flash_start = current_time

    def handle_shooting(self, bullet):
        for i, square in enumerate(self.squares):
            if square.colliderect(bullet.rect):
                self.player_sequence.append(i)
                bullet.kill()
                
                # Check if the shot matches the sequence
                if self.player_sequence[-1] != self.sequence[len(self.player_sequence) - 1]:
                    self.game_state = "game_over"
                elif len(self.player_sequence) == len(self.sequence):
                    self.score += 1
                    if self.score >= 1:
                        self.game_state = "win"  # Set game_state to "win"
                        return True
                return True
        return False

    def update(self):
        # Do nothing if game is won
        if self.game_state == "win":
            return
            
        self.allsprites.update()
        
        # Update bullets and check collisions
        for bullet in list(self.bullets):
            self.handle_shooting(bullet)
            if not pygame.display.get_surface().get_rect().contains(bullet.rect):
                bullet.kill()
        
        # Update sequence display
        if self.game_state == "show_sequence":
            current_time = time.time()
            if self.current_flash is not None:
                if current_time - self.flash_start > self.flash_duration:
                    self.sequence_index += 1
                    self.current_flash = None
                    
                    if self.sequence_index >= len(self.sequence):
                        self.game_state = "player_turn"
            else:
                self.display_sequence()

    def draw(self):
        self.screen.fill(BLACK)
        self.allsprites.draw(self.screen)
        
        # Draw squares
        for i, square in enumerate(self.squares):
            color = self.square_colors[i]
            if self.current_flash == i:
                color = WHITE
            pygame.draw.rect(self.screen, color, square)
        
        # Draw score
        font = pygame.font.Font(None, 36)
        score_text = font.render(f"Score: {self.score}/1", True, WHITE)
        self.screen.blit(score_text, (WIDTH // 2 - score_text.get_width() // 2, 10))
        
        # Draw win/game over messages
        if self.game_state == "win":
            win_text = font.render("Congratulations! You Won!", True, WHITE)
            self.screen.blit(win_text, (WIDTH // 2 - win_text.get_width() // 2, HEIGHT // 2))
        elif self.game_state == "game_over":
            game_over_text = font.render("Game Over!", True, WHITE)
            self.screen.blit(game_over_text, (WIDTH // 2 - game_over_text.get_width() // 2, HEIGHT // 2))

    def shoot(self, target_pos):
        player_center = self.player.rect.center
        dx = target_pos[0] - player_center[0]
        dy = target_pos[1] - player_center[1]
        length = (dx**2 + dy**2)**0.5
        if length > 0:
            dx = dx/length
            dy = dy/length
        direction = [dx, dy]
        
        bullet = Bullet(player_center[0], player_center[1], direction)
        self.bullets.add(bullet)
        self.allsprites.add(bullet)

def run_memory_game(screen, clock):
    game = MemoryGame(screen, clock)
    running = True
    
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return "quit"
            elif event.type == pygame.MOUSEBUTTONDOWN and game.game_state == "player_turn":
                if event.button == 1:
                    game.shoot(pygame.mouse.get_pos())
        
        game.update()
        game.draw()
        
        # Stop the game immediately upon win
        if game.game_state == "win":
            pygame.display.flip()
            time.sleep(2)  # Display win message briefly
            return "completed"
        elif game.game_state == "game_over":
            pygame.display.flip()
            time.sleep(2)
            return "died"
            
        pygame.display.flip()
        clock.tick(FPS)
    
    return "quit"

if __name__ == "__main__":
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Memory Shooting Game")
    clock = pygame.time.Clock()
    
    result = run_memory_game(screen, clock)
    
    pygame.quit()