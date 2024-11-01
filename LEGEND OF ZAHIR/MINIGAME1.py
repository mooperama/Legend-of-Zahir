import pygame
import random
import time
from config_settings import *
from player import *
from sprites import *

class Bullet(pygame.sprite.Sprite):
    """
    A projectile that can be fired by the player.
    
    Attributes:
        image: The bullet's visual representation
        rect: The bullet's position and size
        speed: Movement speed of the bullet
        dx, dy: Direction components
        x, y: Precise floating-point position
    """
    def __init__(self, x, y, direction):
        """
        Initialize a new bullet.
        
        Args:
            x (float): Starting x position
            y (float): Starting y position
            direction (list): [dx, dy] normalized direction vector
        """
        super().__init__()
        self.image = pygame.Surface([BULLETSIZE, BULLETSIZE])
        self.image.fill(WHITE)
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        
        self.speed = 10
        self.dx = direction[0] * self.speed
        self.dy = direction[1] * self.speed
        
        self.x = float(x)
        self.y = float(y)
        
    def update(self):
        """Update bullet position based on its direction and speed."""
        self.x += self.dx
        self.y += self.dy
        self.rect.x = int(self.x)
        self.rect.y = int(self.y)

class MemoryGame:
    """
    A memory game where players shoot targets in sequence.
    
    The game displays a sequence of colored candles that the player must
    replicate by shooting them in the correct order.
    """
    def __init__(self, screen, clock):
        """
        Initialize the memory game.
        
        Args:
            screen: Pygame display surface
            clock: Pygame clock object
        """
        self.screen = screen
        self.clock = clock
        
        # Load spritesheets
        self.character_spritesheet = Spritesheet('LEGEND OF ZAHIR/knight_strip.png')
        self.enemy_spritesheet = Spritesheet('LEGEND OF ZAHIR/skeleton_strip.png')
        self.terrain_spritesheet = Spritesheet('LEGEND OF ZAHIR/dungeon2.jpg')
        
        # Initialize image lists
        self.tile_images = []
        self.flash_images = []
        
        # Load and store candle images
        try:
            # Load unlit candle (black) - we'll use this same image for all unlit states
            black_candle = pygame.image.load('LEGEND OF ZAHIR/Minigame 1 Assets/Black candle.jpg').convert_alpha()
            
            # Load lit candles
            colored_candles = [
                'LEGEND OF ZAHIR/Minigame 1 Assets/Blue candle.jpg',
                'LEGEND OF ZAHIR/Minigame 1 Assets/Orange candle.jpg',
                'LEGEND OF ZAHIR/Minigame 1 Assets/Purple candle.jpg',
                'LEGEND OF ZAHIR/Minigame 1 Assets/Red candle.jpg'
            ]
            
            # Set up tile size
            self.tile_size = TILESIZE * 2
            
            # Create tile images (all black candles)
            for _ in range(4):  # We need 4 black candles
                resized_black = pygame.transform.scale(black_candle, (self.tile_size, self.tile_size))
                self.tile_images.append(resized_black)
            
            # Load and resize colored candles
            for candle_path in colored_candles:
                colored_candle = pygame.image.load(candle_path).convert_alpha()
                resized_colored = pygame.transform.scale(colored_candle, (self.tile_size, self.tile_size))
                self.flash_images.append(resized_colored)
                
        except pygame.error as e:
            print(f"Couldn't load image: {e}")
            pygame.quit()
            raise SystemExit(f"Couldn't load required images: {e}")
        
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
        
        # Set up square positions
        self.squares = [
            pygame.Rect(TILESIZE, TILESIZE, self.tile_size, self.tile_size),
            pygame.Rect(WIDTH - TILESIZE * 3, TILESIZE, self.tile_size, self.tile_size),
            pygame.Rect(TILESIZE, HEIGHT - TILESIZE * 3, self.tile_size, self.tile_size),
            pygame.Rect(WIDTH - TILESIZE * 3, HEIGHT - TILESIZE * 3, self.tile_size, self.tile_size)
        ]
        
        # Animation control variables
        self.current_flash = None
        self.flash_start = time.time()
        self.flash_duration = 0.5
        self.sequence_index = 0
        self.flash_alpha = 255

    def draw(self):
        """Draw the game state to the screen."""
        self.screen.fill(BLACK)
        
        # Draw all sprites
        self.allsprites.draw(self.screen)
        
        # Draw the candles
        for i, square in enumerate(self.squares):
            if self.current_flash == i and i < len(self.flash_images):
                self.screen.blit(self.flash_images[i], square)
            elif i < len(self.tile_images):
                self.screen.blit(self.tile_images[i], square)
        
        # Draw score
        try:
            font = pygame.font.Font('LEGEND OF ZAHIR/assets/fonts/nokiafc22.ttf', 36)
        except pygame.error:
            font = pygame.font.Font(None, 36)  # Fallback to default font
            
        score_text = font.render(f"Score: {self.score}/5", True, WHITE)
        self.screen.blit(score_text, (WIDTH // 2 - score_text.get_width() // 2, 10))

        # Draw game state messages
        if self.game_state == "win":
            win_text = font.render("Congratulations! You Won!", True, WHITE)
            self.screen.blit(win_text, (WIDTH // 2 - win_text.get_width() // 2, HEIGHT // 2))
        elif self.game_state == "game_over":
            game_over_text = font.render("Game Over!", True, WHITE)
            self.screen.blit(game_over_text, (WIDTH // 2 - game_over_text.get_width() // 2, HEIGHT // 2))

    def create_map(self):
        """Create the game map using the MEMORY_TILEMAP configuration."""
        for i, row in enumerate(MEMORY_TILEMAP):
            for j, column in enumerate(row):
                if column == "W":
                    Block(self, j, i)
                elif column == "P":
                    self.player = Player(self, j, i)
                    self.allsprites.add(self.player)

    def display_sequence(self):
        """Generate and display the sequence of colors to memorize."""
        current_time = time.time()
        
        if not self.sequence:
            self.sequence = [random.randint(0, 3) for _ in range(self.score + 1)]
            self.sequence_index = 0
            self.current_flash = self.sequence[0]
            self.flash_start = current_time
            self.player_sequence = []
        elif self.current_flash is None and self.sequence_index < len(self.sequence):
            self.current_flash = self.sequence[self.sequence_index]
            self.flash_start = current_time

    def handle_shooting(self, bullet):
        """
        Handle bullet collision with targets.
        
        Args:
            bullet: The bullet sprite to check for collisions
            
        Returns:
            bool: True if bullet hit a target, False otherwise
        """
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
                        self.win_displayed = True
                        return True
                    
                    self.sequence = []
                    self.sequence_index = 0
                    self.current_flash = None
                    self.player_sequence = []
                    self.game_state = "show_sequence"
                return True
        return False

    def update(self):
        """Update game state, including sprites, bullets, and sequence display."""
        if self.score >= 5:
            self.game_state = "win"
            return
            
        self.allsprites.update()
        
        # Update bullets
        for bullet in list(self.bullets):
            self.handle_shooting(bullet)
            if not pygame.display.get_surface().get_rect().contains(bullet.rect):
                bullet.kill()
        
        # Handle sequence display
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
            target_pos (tuple): (x, y) coordinates of the target position
        """
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
    """
    Run the memory game loop.
    
    Args:
        screen: Pygame display surface
        clock: Pygame clock object
        
    Returns:
        str: Game result ("completed", "died", "quit")
    """
    try:
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
            
            if game.game_state == "win":
                pygame.display.flip()
                time.sleep(2)
                return "completed"
            elif game.game_state == "game_over":
                pygame.display.flip()
                time.sleep(2)
                return "died" if game.score == 0 else "completed"
                
            pygame.display.flip()
            clock.tick(FPS)
        
        return "quit"
        
    except Exception as e:
        print(f"Error in memory game: {e}")
        return "quit"

if __name__ == "__main__":
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Memory Shooting Game")
    clock = pygame.time.Clock()
    
    try:
        result = run_memory_game(screen, clock)
        print(f"Game finished with result: {result}")
    except Exception as e:
        print(f"Error running game: {e}")
    finally:
        pygame.quit()