import pygame
from sprites import *
from config_settings import *
from enemies import *
from player import *
from MINIGAME1 import run_memory_game
from MINIGAME2 import run_timezone_game
from MINIGAME3 import run_continent_game
from MINIGAME4 import main as run_language_matching_game
from MINIGAME5 import main as run_boss_battle
from soundmanager import sound_manager
from tutorial import *
from dialogue import DialogueSystem
from save_system import SaveSystem, SaveLoadMenu
import os
from dialogue import VisualNovelManager, SceneType
from enum import Enum
import sys
import time

class GameState(Enum):
    MAIN_GAME = "main_game"
    DIALOGUE = "dialogue"
    MINIGAME = "minigame"
    CUTSCENE = "cutscene"
    TRANSITION = "transition"

class Game:
    """Main game class that handles the game loop, initialization, and core game logic."""

    def __init__(self):
        """Initialize the game, set up the display, clock, and load assets."""
        pygame.init()
        pygame.mixer.init()
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("Legend of Zahir")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.Font(None, 32)
        
        # Game state initialization
        self.running = True
        self.playing = False
        self.state = GameState.MAIN_GAME
        self.start_time = 0
        self.elapsed_time = 0

        # Load managers and systems
        self.visual_novel = VisualNovelManager(self.screen)
        sound_manager.play_music()

        # Load sprite sheets
        self.character_spritesheet = Spritesheet('knight_strip.png')
        self.enemy_spritesheet = Spritesheet('skeleton_strip.png')
        self.terrain_spritesheet = Spritesheet('dungeon2.jpg')

        # Game progression tracking
        self.game_sequence = [
            {'type': 'dialogue', 'id': 'game_intro'},
            {'type': 'main', 'id': 'initial_combat'},
            {'type': 'dialogue', 'id': 'pemdas_intro'},
            {'type': 'minigame', 'id': 'pemdas'},
            {'type': 'dialogue', 'id': 'pemdas_complete'},
            {'type': 'main', 'id': 'combat_section_2'},
            {'type': 'dialogue', 'id': 'language_intro'},
            {'type': 'minigame', 'id': 'language'},
            {'type': 'dialogue', 'id': 'language_complete'},
            {'type': 'dialogue', 'id': 'boss_intro'},
            {'type': 'minigame', 'id': 'boss'},
            {'type': 'dialogue', 'id': 'game_complete'}
        ]
        self.current_sequence_index = 0
        
        # Initialize story dialogues
        self._init_story_dialogues()

    def new(self):
        """Set up a new game, create sprite groups, and initialize game objects."""
        self.all_sprites = pygame.sprite.LayeredUpdates()
        self.blocks = pygame.sprite.LayeredUpdates()
        self.enemies = pygame.sprite.LayeredUpdates()
        self.attacks = pygame.sprite.LayeredUpdates()
        self.bullets = pygame.sprite.LayeredUpdates()

        self.createTilemap()
        self.create_enemies()
        self.playing = True
        self.start_time = time.time()

    def handle_sequence(self):
        """Handle the current sequence in the game progression."""
        current_sequence = self.game_sequence[self.current_sequence_index]
        
        if current_sequence['type'] == 'dialogue':
            if not self.visual_novel.is_scene_active():
                self.visual_novel.start_scene(current_sequence['id'])
                self.state = GameState.DIALOGUE
        
        elif current_sequence['type'] == 'main':
            if self.state != GameState.MAIN_GAME:
                self.state = GameState.MAIN_GAME
                self.new()
        
        elif current_sequence['type'] == 'minigame':
            if self.state != GameState.MINIGAME:
                self.state = GameState.MINIGAME
                self.start_minigame(current_sequence['id'])

    def start_minigame(self, minigame_id):
        """Start the specified minigame."""
        result = None
        if minigame_id == 'pemdas':
            result = run_pemdas_game(self.screen, self.clock)
        elif minigame_id == 'language':
            result = run_language_matching_game()
        elif minigame_id == 'boss':
            result = run_boss_battle()
            
        if result == "completed":
            self.current_sequence_index += 1
            self.state = GameState.MAIN_GAME

    def update(self):
        """Update game objects based on current state."""
        if self.state == GameState.MAIN_GAME:
            self.all_sprites.update()
            self.elapsed_time = time.time() - self.start_time
            
            if len(self.enemies) == 0:
                self.current_sequence_index += 1
                self.handle_sequence()
            
            if self.player.health <= 0:
                self.playing = False
                
        elif self.state == GameState.DIALOGUE:
            self.visual_novel.update()

    def events(self):
        """Handle game events based on current state."""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.playing = False
                self.running = False
            
            if self.state == GameState.DIALOGUE:
                if self.visual_novel.handle_input(event):
                    self.current_sequence_index += 1
                    self.handle_sequence()
                    
            elif self.state == GameState.MAIN_GAME:
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1:
                        self.player.shoot(pygame.mouse.get_pos())
                        sound_manager.play_sound('bullet')

    def draw(self):
        """Draw game elements based on current state."""
        self.screen.fill(BACKGROUND_COLOR)
        
        if self.state == GameState.MAIN_GAME:
            self.all_sprites.draw(self.screen)
            self.player.draw_health_bar(self.screen)
            self.player.draw_exp_bar(self.screen)
            self.player.draw_stats(self.screen)
            self.draw_timer()
        
        if self.state == GameState.DIALOGUE:
            self.visual_novel.draw()
        
        pygame.display.update()

    def createTilemap(self):
            """Create the game world based on the TILEMAP defined in config_settings."""
            for i, row in enumerate(TILEMAP):
                for j, column in enumerate(row):
                    if column == "W":
                        Block(self, j, i)
                    if column == "P":
                        self.player = Player(self, j, i)
                    if column == "E":
                        Enemy(self, j, i)

    def create_enemies(self):
        """Create enemies at random positions in the game world."""
        for _ in range(3):
            enemy = Enemy.create_random(self)
            self.enemies.add(enemy)
            self.all_sprites.add(enemy)

    def handle_minigame_transition(self, minigame_id: str) -> None:
        """
        Handle transition to and from minigames.
        
        Args:
            minigame_id: Identifier for the minigame to transition to
        """
        # Fade out effect
        fade_surface = pygame.Surface((WIDTH, HEIGHT))
        fade_surface.fill(BLACK)
        for alpha in range(0, 255, 5):
            fade_surface.set_alpha(alpha)
            self.screen.blit(fade_surface, (0, 0))
            pygame.display.update()
            pygame.time.delay(5)

        # Run appropriate minigame
        result = None
        if minigame_id == "pemdas":
            self.visual_novel.start_scene("pemdas_intro")
            while self.visual_novel.is_scene_active():
                self.events()
                self.visual_novel.update()
                self.visual_novel.draw()
                pygame.display.update()
                self.clock.tick(FPS)
            result = run_pemdas_game(self.screen, self.clock)
            
        elif minigame_id == "language":
            self.visual_novel.start_scene("language_intro")
            while self.visual_novel.is_scene_active():
                self.events()
                self.visual_novel.update()
                self.visual_novel.draw()
                pygame.display.update()
                self.clock.tick(FPS)
            result = run_language_matching_game()
            
        elif minigame_id == "boss":
            self.visual_novel.start_scene("boss_intro")
            while self.visual_novel.is_scene_active():
                self.events()
                self.visual_novel.update()
                self.visual_novel.draw()
                pygame.display.update()
                self.clock.tick(FPS)
            result = run_boss_battle()

        # Handle minigame completion
        if result == "completed":
            completion_scene = f"{minigame_id}_complete"
            if completion_scene in self.story_dialogues:
                self.visual_novel.start_scene(completion_scene)

        # Fade back in
        for alpha in range(255, 0, -5):
            fade_surface.set_alpha(alpha)
            self.screen.blit(fade_surface, (0, 0))
            pygame.display.update()
            pygame.time.delay(5)

        return result

    def game_loop(self):
        """Main game loop with improved sequence handling and transitions."""
        # Start with intro dialogue
        self.visual_novel.start_scene("game_intro")
        
        while self.running:
            if self.current_sequence_index >= len(self.game_sequence):
                self.show_game_completion()
                break

            current_sequence = self.game_sequence[self.current_sequence_index]
            
            if current_sequence["type"] == "dialogue":
                # Handle dialogue sequences
                while self.visual_novel.is_scene_active():
                    self.events()
                    self.visual_novel.update()
                    self.draw()
                    self.clock.tick(FPS)
                self.current_sequence_index += 1
                
            elif current_sequence["type"] == "main":
                # Handle main gameplay
                self.new()
                while self.playing:
                    self.events()
                    self.update()
                    self.draw()
                    self.clock.tick(FPS)
                    
                    if len(self.enemies) == 0:
                        self.current_sequence_index += 1
                        break
                        
            elif current_sequence["type"] == "minigame":
                # Handle minigame transitions
                result = self.handle_minigame_transition(current_sequence["id"])
                if result == "completed":
                    self.current_sequence_index += 1
                elif result == "failed":
                    self.handle_minigame_failure()

    def handle_minigame_failure(self):
        """Handle player failure in minigames."""
        retry = self.show_retry_prompt()
        if not retry:
            self.running = False

    def show_retry_prompt(self) -> bool:
        """
        Display a prompt asking if the player wants to retry the challenge.
        
        Returns:
            bool: True if player wants to retry, False otherwise
        """
        prompt_surface = pygame.Surface((400, 200))
        prompt_surface.fill(WHITE)
        prompt_rect = prompt_surface.get_rect(center=(WIDTH//2, HEIGHT//2))
        
        font = pygame.font.Font(None, 36)
        text = font.render("Try again?", True, BLACK)
        yes_text = font.render("Yes", True, BLACK)
        no_text = font.render("No", True, BLACK)
        
        yes_button = pygame.Rect(prompt_rect.left + 50, prompt_rect.bottom - 70, 100, 40)
        no_button = pygame.Rect(prompt_rect.right - 150, prompt_rect.bottom - 70, 100, 40)
        
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return False
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if yes_button.collidepoint(event.pos):
                        return True
                    if no_button.collidepoint(event.pos):
                        return False
            
            self.screen.fill(BLACK)
            pygame.draw.rect(self.screen, WHITE, prompt_rect)
            self.screen.blit(text, (prompt_rect.centerx - text.get_width()//2, prompt_rect.top + 30))
            
            pygame.draw.rect(self.screen, GREEN, yes_button)
            pygame.draw.rect(self.screen, RED, no_button)
            
            self.screen.blit(yes_text, (yes_button.centerx - yes_text.get_width()//2, 
                                      yes_button.centery - yes_text.get_height()//2))
            self.screen.blit(no_text, (no_button.centerx - no_text.get_width()//2, 
                                     no_button.centery - no_text.get_height()//2))
            
            pygame.display.update()
            self.clock.tick(FPS)

    def show_game_completion(self):
        """Display the game completion sequence."""
        self.visual_novel.start_scene("game_complete")
        while self.visual_novel.is_scene_active():
            self.events()
            self.visual_novel.update()
            self.visual_novel.draw()
            pygame.display.update()
            self.clock.tick(FPS)
        
        self.show_final_results()

    def show_final_results(self):
        """Display final game results and statistics."""
        completion_surface = pygame.Surface((WIDTH, HEIGHT))
        completion_surface.fill(BLACK)
        
        font = pygame.font.Font(None, 48)
        title = font.render("Journey Complete!", True, WHITE)
        time_text = font.render(f"Total Time: {int(self.elapsed_time)}s", True, WHITE)
        
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_RETURN:
                        return
            
            self.screen.blit(completion_surface, (0, 0))
            self.screen.blit(title, (WIDTH//2 - title.get_width()//2, HEIGHT//3))
            self.screen.blit(time_text, (WIDTH//2 - time_text.get_width()//2, HEIGHT//2))
            
            pygame.display.update()
            self.clock.tick(FPS)

    def reset_game(self):
        """Reset the game state for a new playthrough."""
        self.current_sequence_index = 0
        self.elapsed_time = 0
        self.player.health = self.player.max_health
        self.player.exp = 0
        self.player.level = 1
        self.enemies.empty()
        self.bullets.empty()
        self.playing = True

    # Game initialization and main loop
    def main():
        """Initialize and run the game."""
        game = Game()
        game.intro_screen()
        while game.running:
            game.game_loop()
        pygame.quit()
        sys.exit()

    if __name__ == "__main__":
        main()