import pygame
import random
import time
import math
from config_settings import *
from player import *
from sprites import *

class Bullet(pygame.sprite.Sprite):
    def __init__(self, x, y, direction):
        super().__init__()
        
        try:
            self.original_image = pygame.image.load('LEGEND OF ZAHIR/fireball.png').convert_alpha()
            scaled_size = (32, 32)
            self.image = pygame.transform.scale(self.original_image, scaled_size)
        except pygame.error as e:
            print(f"Couldn't load bullet image: {e}")
            self.image = pygame.Surface([BULLETSIZE, BULLETSIZE])
            self.image.fill(RED)

        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        
        self.speed = 10
        self.dx = direction[0] * self.speed
        self.dy = direction[1] * self.speed
        
        self.x = float(self.rect.centerx)
        self.y = float(self.rect.centery)
        
        angle = math.degrees(math.atan2(-direction[1], direction[0]))
        self.image = pygame.transform.rotate(self.image, angle)
        
    def update(self):
        self.x += self.dx
        self.y += self.dy
        self.rect.centerx = int(self.x)
        self.rect.centery = int(self.y)

class MemoryGame:
    def __init__(self, screen, clock):
        self.screen = screen
        self.clock = clock
        self.initialize_game()
        self.light_surface = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)

    def initialize_game(self):
        """Initialize or reset the game state"""
        self.character_spritesheet = Spritesheet('LEGEND OF ZAHIR/main character strip.png')
        self.enemy_spritesheet = Spritesheet('LEGEND OF ZAHIR/skeleton_strip.png')
        self.terrain_spritesheet = Spritesheet('LEGEND OF ZAHIR/dungeon2.jpg')
        
        self.tile_images = []
        self.flash_images = []
        
        try:
            self.original_image = pygame.image.load('LEGEND OF ZAHIR/fireball.png').convert_alpha()
            scaled_size = (32, 32)
            self.original_image = pygame.transform.scale(self.original_image, scaled_size)

            black_candle = pygame.image.load('LEGEND OF ZAHIR/Minigame 1 Assets/Black candle.png').convert_alpha()
            
            colored_candles = [
                'LEGEND OF ZAHIR/Minigame 1 Assets/Blue candle.png',
                'LEGEND OF ZAHIR/Minigame 1 Assets/Orange candle.png',
                'LEGEND OF ZAHIR/Minigame 1 Assets/Purple candle.png',
                'LEGEND OF ZAHIR/Minigame 1 Assets/Red candle.png'
            ]
            
            self.tile_size = TILESIZE * 2
            
            for _ in range(4):
                resized_black = pygame.transform.scale(black_candle, (self.tile_size, self.tile_size))
                self.tile_images.append(resized_black)
            
            for candle_path in colored_candles:
                colored_candle = pygame.image.load(candle_path).convert_alpha()
                resized_colored = pygame.transform.scale(colored_candle, (self.tile_size, self.tile_size))
                self.flash_images.append(resized_colored)
                
        except pygame.error as e:
            print(f"Couldn't load image: {e}")
            pygame.quit()
            raise SystemExit(f"Couldn't load required images: {e}")
        
        self.allsprites = pygame.sprite.LayeredUpdates()
        self.blocks = pygame.sprite.LayeredUpdates()
        self.enemies = pygame.sprite.LayeredUpdates()
        self.attacks = pygame.sprite.LayeredUpdates()
        self.bullets = pygame.sprite.LayeredUpdates()
        
        self.sequence = []
        self.player_sequence = []
        self.score = 0
        self.game_state = "show_sequence"
        self.win_displayed = False
        self.retry_prompt = False
        self.retry_start_time = 0
        
        self.create_map()
        
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
        self.flash_alpha = 255

    #nye 
    def update_light_mask(self):
        """Create the spotlight effect around the player and candles"""
        if not hasattr(self, 'player') or not hasattr(self.player, 'rect'):
            return
            
        # Create the dark overlay
        self.light_surface = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        self.light_surface.fill((0, 0, 0, 250))

        # Player's spotlight
        pygame.draw.circle(
            self.light_surface,
            (0, 0, 0, 0),
            self.player.rect.center,
            50
        )

        # Candle spotlights with orange rings
        for square in self.squares:
            # Clear circle for each candle
            pygame.draw.circle(
                self.light_surface,
                (0, 0, 0, 0),
                square.center,
                50
            )
            # Orange ring around each candle
            pygame.draw.circle(
                self.light_surface,
                (255, 165, 0, 100),
                square.center,
                55,
                5
            )

    def draw(self):
        self.screen.fill(BLACK)
        
        self.allsprites.draw(self.screen)
        
        for i, square in enumerate(self.squares):
            if self.current_flash == i and i < len(self.flash_images):
                self.screen.blit(self.flash_images[i], square)
            elif i < len(self.tile_images):
                self.screen.blit(self.tile_images[i], square)
        
        # Apply the light mask before drawing text
        self.update_light_mask()
        self.screen.blit(self.light_surface, (0, 0))
        
        # Text
        try:
            font = pygame.font.Font('LEGEND OF ZAHIR/assets/fonts/nokiafc22.ttf', 36)
        except pygame.error:
            font = pygame.font.Font(None, 36)
            
        score_text = font.render(f"Score: {self.score}/5", True, WHITE)
        self.screen.blit(score_text, (WIDTH // 2 - score_text.get_width() // 2, 10))

        if self.game_state == "win":
            win_text = font.render("Congratulations! You Won!", True, WHITE)
            self.screen.blit(win_text, (WIDTH // 2 - win_text.get_width() // 2, HEIGHT // 2))
        elif self.game_state == "game_over":
            game_over_text = font.render("Game Over! Click to retry", True, WHITE)
            self.screen.blit(game_over_text, (WIDTH // 2 - game_over_text.get_width() // 2, HEIGHT // 2))

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
        for i, square in enumerate(self.squares):
            if square.colliderect(bullet.rect):
                self.player_sequence.append(i)
                bullet.kill()
                
                if self.player_sequence[-1] != self.sequence[len(self.player_sequence) - 1]:
                    self.game_state = "game_over"
                    self.retry_start_time = time.time()
                    return True
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
        if self.score >= 5:
            self.game_state = "win"
            return
            
        self.allsprites.update()
        
        for bullet in list(self.bullets):
            self.handle_shooting(bullet)
            if not pygame.display.get_surface().get_rect().contains(bullet.rect):
                bullet.kill()
        
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

    def reset_level(self):
        """Reset the current level while maintaining score"""
        self.sequence = []
        self.player_sequence = []
        self.current_flash = None
        self.sequence_index = 0
        self.game_state = "show_sequence"

def run_memory_game(screen, clock):
    try:
        game = MemoryGame(screen, clock)
        running = True
        
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return "quit"
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if game.game_state == "player_turn":
                        if event.button == 1:
                            game.shoot(pygame.mouse.get_pos())
                    elif game.game_state == "game_over":
                        if event.button == 1:
                            # Reset the level but keep the score
                            game.reset_level()
            
            game.update()
            game.draw()
            
            if game.game_state == "win":
                pygame.display.flip()
                time.sleep(2)
                return "completed"
                
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