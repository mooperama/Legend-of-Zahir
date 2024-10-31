import pygame
import random
import time
from config_settings import *
from player import *
from sprites import *

class Bullet(pygame.sprite.Sprite):
    def __init__(self, x, y, direction):
        super().__init__()
        self.image = pygame.Surface([BULLETSIZE,BULLETSIZE])
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
        
        # Load spritesheets FIRST
        self.character_spritesheet = Spritesheet('LEGEND OF ZAHIR/knight_strip.png')
        self.enemy_spritesheet = Spritesheet('LEGEND OF ZAHIR/skeleton_strip.png')
        self.terrain_spritesheet = Spritesheet('LEGEND OF ZAHIR/dungeon2.jpg')
        
        # Load unlit candles
        self.tile_images = [
            pygame.image.load('LEGEND OF ZAHIR/assets/tiles/tile1.png').convert_alpha(), #1 black candle
        ]
        # Load lit candles
        self.flash_images = [
            pygame.image.load('LEGEND OF ZAHIR/assets/tiles/tile1_flash.png').convert_alpha(),
            pygame.image.load('LEGEND OF ZAHIR/assets/tiles/tile2_flash.png').convert_alpha(),
            pygame.image.load('LEGEND OF ZAHIR/assets/tiles/tile3_flash.png').convert_alpha(),
            pygame.image.load('LEGEND OF ZAHIR/assets/tiles/tile4_flash.png').convert_alpha()
        ]
        
        # Resize images to match tile size
        self.tile_size = TILESIZE * 2
        for i in range(len(self.tile_images)):
            self.tile_images[i] = pygame.transform.scale(self.tile_images[i], (self.tile_size, self.tile_size))
            self.flash_images[i] = pygame.transform.scale(self.flash_images[i], (self.tile_size, self.tile_size))
        
        # Initialize sprite groups
        self.allsprites = pygame.sprite.LayeredUpdates()
        self.blocks = pygame.sprite.LayeredUpdates()
        self.enemies = pygame.sprite.LayeredUpdates()
        self.attacks = pygame.sprite.LayeredUpdates()
        self.bullets = pygame.sprite.LayeredUpdates()
        
        # Game state variables
        self.sequence = []
        self.player_sequence = []
        self.score = 0
        self.game_state = "show_sequence"
        self.win_displayed = False
        
        # Create the map first
        self.create_map()
        
        # Square properties
        self.squares = [
            pygame.Rect(TILESIZE, TILESIZE, self.tile_size, self.tile_size),
            pygame.Rect(WIDTH - TILESIZE * 3, TILESIZE, self.tile_size, self.tile_size),
            pygame.Rect(TILESIZE, HEIGHT - TILESIZE * 3, self.tile_size, self.tile_size),
            pygame.Rect(WIDTH - TILESIZE * 3, HEIGHT - TILESIZE * 3, self.tile_size, self.tile_size)
        ]
        
        self.current_flash = None
        self.flash_start = time.time()
        self.flash_duration = 0.5
        self.sequence_index = 0
        self.flash_alpha = 255  # For fade effect

    def draw(self):
        self.screen.fill(BLACK)
        
        # Draw all sprites (includes walls and player)
        self.allsprites.draw(self.screen)
        
        # Draw the tiles
        for i, square in enumerate(self.squares):
            # Draw normal or flashing tile
            if self.current_flash == i:
                # Draw flashing tile
                self.screen.blit(self.flash_images[i], square)
            else:
                # Draw normal tile
                self.screen.blit(self.tile_images[i], square)
        
        # Draw score
        font = pygame.font.Font('LEGEND OF ZAHIR/assets/fonts/nokiafc22.ttf', 36)
        score_text = font.render(f"Score: {self.score}/5", True, WHITE)
        self.screen.blit(score_text, (WIDTH // 2 - score_text.get_width() // 2, 10))

        if self.game_state == "win":
            win_text = font.render("Congratulations! You Won!", True, WHITE)
            self.screen.blit(win_text, (WIDTH // 2 - win_text.get_width() // 2, HEIGHT // 2))
        elif self.game_state == "game_over":
            game_over_text = font.render("Game Over!", True, WHITE)
            self.screen.blit(game_over_text, (WIDTH // 2 - game_over_text.get_width() // 2, HEIGHT // 2))
            
    def create_map(self):
        """Create the game map from MEMORY_TILEMAP using Block class"""
        for i, row in enumerate(MEMORY_TILEMAP):
            for j, column in enumerate(row):
                if column == "W":
                    Block(self, j, i)  # Create wall using main game's Block class
                elif column == "P":
                    # Create player and store reference
                    self.player = Player(self, j, i)  # Use main game's Player class
                    self.allsprites.add(self.player)

    def display_sequence(self):
        """Display the sequence of colors by flashing them one at a time"""
        current_time = time.time()
        
        # Generate new sequence if needed
        if len(self.sequence) == 0:  # Changed condition to be more explicit
            self.sequence = [random.randint(0, 3) for _ in range(self.score + 1)]
            self.sequence_index = 0
            self.current_flash = self.sequence[0]
            self.flash_start = current_time
            self.player_sequence = []

        # If we're not currently flashing a color, move to the next one
        elif self.current_flash is None:
            if self.sequence_index < len(self.sequence):
                self.current_flash = self.sequence[self.sequence_index]
                self.flash_start = current_time

    def handle_shooting(self, bullet):
        for i, square in enumerate(self.squares):
            if square.colliderect(bullet.rect):
                self.player_sequence.append(i)
                bullet.kill()
                
                if self.player_sequence[-1] != self.sequence[len(self.player_sequence) - 1]:
                    self.game_state = "game_over"
                elif len(self.player_sequence) == len(self.sequence):
                    self.score += 1
                    if self.score >= 5:
                        self.game_state = "win"
                        self.win_displayed = True  # Set flag when win condition met
                        return True
                    
                    # Only continue with new sequence if we haven't won
                    self.sequence = []
                    self.sequence_index = 0
                    self.current_flash = None
                    self.player_sequence = []
                    self.game_state = "show_sequence"
                return True
        return False

    def update(self):
        # Check for win condition first
        if self.score >= 5:
            self.game_state = "win"
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

    def shoot(self, target_pos):
        """
        Create a bullet aimed at the target position.
        Args:
            target_pos: (x, y) tuple of the mouse click position
        """
        player_center = self.player.rect.center
        # Calculate direction vector
        dx = target_pos[0] - player_center[0]
        dy = target_pos[1] - player_center[1]
        # Normalize direction
        length = (dx**2 + dy**2)**0.5
        if length > 0:
            dx = dx/length
            dy = dy/length
        direction = [dx, dy]
        
        # Create bullet with proper parameters
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
                if event.button == 1:  # Left click
                    game.shoot(pygame.mouse.get_pos())
        
        game.update()
        game.draw()
        
        # Check win condition first
        if game.game_state == "win":
            pygame.display.flip()
            time.sleep(2)  # Show win message for 2 seconds
            return "completed"
        elif game.game_state == "game_over":
            pygame.display.flip()
            time.sleep(2)
            return "died" if game.score == 0 else "completed"
            
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