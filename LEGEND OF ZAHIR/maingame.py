import pygame
from sprites import *
from config_settings import *
from enemies import *
from player import *
from MINIGAME2 import run_pemdas_game
from MINIGAME4 import main as run_language_matching_game
from MINIGAME5 import main as run_boss_battle
from soundmanager import sound_manager
from tutorial import *
from save_system import SaveSystem, SaveLoadMenu
import os
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
        
        # Game sequence setup
        self.game_sequence = ['main', 'candle memory', 'main', 'timezone', 'main', 'language','main','continent','main', 'boss']
        self.current_sequence_index = 0
        self.total_sequences = len(self.game_sequence)
           
        # Initialize save system
        self.save_system = SaveSystem()

        self.paused = False  # Add this line
        
        # Add keyboard state tracking for save system
        self.keys_pressed = set()  # Track currently pressed keys


    def game_loop(self):
        """
        Modified main game loop that shows gameplay during tutorial
        """
        # Tutorial loop with gameplay
        while self.running and self.in_tutorial:
            # Handle events
            events = pygame.event.get()
            for event in events:
                if event.type == pygame.QUIT:
                    self.running = False
                    return
                
                # Handle both tutorial and game events
                self.tutorial_system.handle_input(events)
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    self.player.shoot(pygame.mouse.get_pos())
                    sound_manager.play_sound('bullet')
                
                # Check if tutorial is completed
                if self.tutorial_system.tutorial_completed:
                    self.in_tutorial = False
                    break
            
            # Update game state during tutorial
            self.allsprites.update()
            
            # Draw game and tutorial overlay
            self.screen.fill(BACKGROUND_COLOR)
            self.allsprites.draw(self.screen)
            self.player.draw_health_bar(self.screen)
            self.player.draw_exp_bar(self.screen)
            self.player.draw_stats(self.screen)
            self.draw_timer()
            
            # Draw tutorial overlay last
            self.tutorial_system.draw(self.screen)
            
            pygame.display.update()
            self.clock.tick(FPS)
        
        # Continue with main game loop
        while self.running and self.current_sequence_index < self.total_sequences:
            current_mode = self.game_sequence[self.current_sequence_index]
            
            if current_mode == 'main':
                result = self.run_main_game_sequence()
            else:
                result = self.run_minigame_sequence(current_mode)
            
            if result == "quit":
                self.running = False
                break
            
            if result == "completed":
                # Show appropriate transition message based on next game
                if self.current_sequence_index + 1 < self.total_sequences:
                    next_mode = self.game_sequence[self.current_sequence_index + 1]
                    if next_mode == 'candle memory':
                        self.show_level_complete_dialogue("Main game complete! Press Enter for Candle Challenge")
                    elif next_mode == 'timezone':
                        self.show_level_complete_dialogue("Main game complete! Press Enter for Timezone Challenge")
                    elif next_mode == 'language':
                        self.show_level_complete_dialogue("Main game complete! Press Enter for Language Challenge")
                    elif next_mode == 'continent':
                        self.show_level_complete_dialogue("Main game complete! Press Enter for The Continent Challenge")
                    elif next_mode == 'boss':
                        self.show_level_complete_dialogue("Main game complete! Press Enter for Final Boss Battle")
                    elif next_mode == 'main':
                        self.show_level_complete_dialogue("Minigame complete! Press Enter to return to main game")
                
                self.current_sequence_index += 1
            elif result == "died":
                if not self.restart_level_prompt():
                    self.running = False
                    break

        if self.current_sequence_index >= self.total_sequences:
            self.show_congratulations()
        
        self.show_final_results()


    def name_entry_screen(self):
        """
        Display a screen for the player to enter their name.
        Returns the entered name.
        """
        input_box = pygame.Rect(WIDTH/2 - 100, HEIGHT/2, 200, 32)
        color_inactive = pygame.Color('lightskyblue3')
        color_active = pygame.Color('dodgerblue2')
        color = color_inactive
        active = False
        text = ''
        done = False

        prompt = self.font.render('Please Enter Your Player Name:', True, WHITE)
        prompt_rect = prompt.get_rect(center=(WIDTH/2, HEIGHT/2 - 50))

        enter_text = self.font.render('Press ENTER when done', True, WHITE)
        enter_rect = enter_text.get_rect(center=(WIDTH/2, HEIGHT/2 + 50))

        while not done:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                    return ''
                
                if event.type == pygame.MOUSEBUTTONDOWN:
                    active = input_box.collidepoint(event.pos)
                    color = color_active if active else color_inactive
                
                if event.type == pygame.KEYDOWN:
                    if active:
                        if event.key == pygame.K_RETURN:
                            done = True
                        elif event.key == pygame.K_BACKSPACE:
                            text = text[:-1]
                        else:
                            # Limit name length to 15 characters
                            if len(text) < 15:
                                text += event.unicode

            self.screen.fill(BLACK)
            
            # Draw prompt
            self.screen.blit(prompt, prompt_rect)
            
            # Draw the input box
            txt_surface = self.font.render(text, True, color)
            width = max(200, txt_surface.get_width()+10)
            input_box.w = width
            input_box.centerx = WIDTH/2
            pygame.draw.rect(self.screen, color, input_box, 2)
            self.screen.blit(txt_surface, (input_box.x+5, input_box.y+5))
            
            # Draw enter instruction
            self.screen.blit(enter_text, enter_rect)
            
            pygame.display.flip()
            self.clock.tick(FPS)

        return text if text else "Player"  # Return "Player" if no name entered

    def intro_screen(self):
        """
        Modified intro screen to transition to name entry
        """
        title = self.font.render('Legend of Zahir', True, WHITE)
        title_rect = title.get_rect(center=(WIDTH/2, HEIGHT/3))

        play_button = pygame.Rect(WIDTH/2 - 50, HEIGHT/2, 100, 50)
        play_text = self.font.render('Play', True, BLACK)

        intro_running = True
        while intro_running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                    return
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if play_button.collidepoint(event.pos):
                        intro_running = False
                        self.player_name = self.name_entry_screen()  # Get player name
                        return

            self.screen.fill(BLACK)
            self.screen.blit(title, title_rect)
            pygame.draw.rect(self.screen, WHITE, play_button)
            self.screen.blit(play_text, (play_button.x + 30, play_button.y + 15))
            pygame.display.update()
            self.clock.tick(FPS)

    def createTilemap(self):
        """
        Create the game world based on the TILEMAP defined in config_settings.
        """
        for i, row in enumerate(TILEMAP):
            for j, column in enumerate(row):
                if column == "W":
                    Block(self, j, i)  # Create a wall block
                if column == "P":
                    self.player = Player(self, j, i)  # Create the player
                if column == "E":
                    Enemy(self, j, i)  # Create an enemy

    def new(self):
        """
        Set up a new game, create sprite groups, and initialize game objects.
        """
        # Initialize sprite groups
        self.allsprites = pygame.sprite.LayeredUpdates()
        self.blocks = pygame.sprite.LayeredUpdates()
        self.enemies = pygame.sprite.LayeredUpdates()
        self.attacks = pygame.sprite.LayeredUpdates()
        self.bullets = pygame.sprite.LayeredUpdates()

        self.createTilemap()  # Create the game world
        self.create_enemies()  # Spawn initial enemies
        self.playing = True  # Set the game state to playing
        self.start_time = time.time()  # Record the start time

# Replace the existing events method with this:
    def events(self):
        """Handle game events with save system integration."""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.playing = False
                self.running = False
                
            # Handle key press events
            elif event.type == pygame.KEYDOWN:
                self.keys_pressed.add(event.key)
                
                # Handle save system shortcuts
                if event.key == pygame.K_ESCAPE and not self.paused:
                    self.paused = True
                    self.show_save_load_menu()
                    self.paused = False
                elif event.key == pygame.K_q and not self.paused:
                    self.quick_save()
                elif event.key == pygame.K_r and not self.paused:
                    self.quick_load()
                    
            # Handle key release events
            elif event.type == pygame.KEYUP:
                self.keys_pressed.discard(event.key)
                
            # Handle shooting when not paused
            if event.type == pygame.MOUSEBUTTONDOWN and not self.paused:
                if event.button == 1 and not self.tutorial_system.active:
                    self.player.shoot(pygame.mouse.get_pos())
                    sound_manager.play_sound('bullet')


# Replace the existing update method with this:
    def update(self):
        """Update game state when not paused."""
        if not self.paused:
            self.allsprites.update()
            self.elapsed_time = time.time() - self.start_time

            if self.player.health <= 0:
                self.playing = False

            # Check for bullet collisions
            hits = pygame.sprite.groupcollide(self.bullets, self.enemies, True, True)
            
            if len(self.enemies) == 0:
                self.playing = False
                
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

            self.screen.blit(prompt_box, prompt_box_rect)
            pygame.display.update()
            self.clock.tick(FPS)
        
        self.show_final_results()

    def show_final_results(self):
        """
        Display the final results screen showing total time and score.
        """
        text = self.font.render('Game Complete!', True, WHITE)
        text_rect = text.get_rect(center=(WIDTH/2, HEIGHT/2 - 50))

        time_text = self.font.render(f'Total Time: {int(self.elapsed_time)}s', True, WHITE)
        time_rect = time_text.get_rect(center=(WIDTH/2, HEIGHT/2))


        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return

            self.screen.fill(BLACK)
            self.screen.blit(text, text_rect)
            self.screen.blit(time_text, time_rect)
            pygame.display.update()
            self.clock.tick(FPS)


# Replace the existing quick_save method with this:
    def quick_save(self):
        """Perform a quick save with auto-generated name."""
        try:
            if self.save_system.save_game(self):
                self.show_message("Game saved! (Q)", duration=1.0)
            else:
                self.show_message("Save failed! (Q)", duration=1.0)
        except Exception as e:
            print(f"Error in quick save: {e}")
            self.show_message("Save error! (Q)", duration=1.0)

# Replace the existing quick_load method with this:
    def quick_load(self):
        """Load the most recent save file."""
        try:
            saves = self.save_system.list_saves()
            if saves:
                # Sort saves by date and get most recent
                saves.sort(key=lambda x: x['date'], reverse=True)
                if self.save_system.load_game(saves[0]['name'], self):
                    self.show_message("Game loaded! (R)", duration=1.0)
                else:
                    self.show_message("Load failed! (R)", duration=1.0)
            else:
                self.show_message("No saves found! (R)", duration=1.0)
        except Exception as e:
            print(f"Error in quick load: {e}")
            self.show_message("Load error! (R)", duration=1.0)

    def show_message(self, message, duration=2.0):
        """
        Show a temporary message on screen
        
        Args:
            message (str): Message to display
            duration (float): How long to show message in seconds
        """
        # Create semi-transparent overlay
        overlay = pygame.Surface((WIDTH, HEIGHT))
        overlay.fill((0, 0, 0))
        overlay.set_alpha(128)
        
        # Render message
        font = pygame.font.Font(None, 36)
        text = font.render(message, True, WHITE)
        text_rect = text.get_rect(center=(WIDTH/2, HEIGHT/2))
        
        # Calculate end time
        end_time = time.time() + duration
        
        # Show message
        while time.time() < end_time:
            # Draw current game state
            self.draw()
            
            # Draw message overlay
            self.screen.blit(overlay, (0, 0))
            self.screen.blit(text, text_rect)
            
            pygame.display.flip()
            self.clock.tick(FPS)
            
            # Check for early exit
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return
                if event.type == pygame.KEYDOWN:
                    return

    # Replace the existing show_save_load_menu method with this:
    def show_save_load_menu(self):
        """Show the save/load menu and handle user interaction."""
        try:
            menu = SaveLoadMenu(self)
            menu_active = True
            paused = True
            
            # Store the current game screen
            background = pygame.Surface((WIDTH, HEIGHT))
            background.blit(self.screen, (0, 0))
            
            while menu_active and self.running and paused:
                # Handle events
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        self.running = False
                        return
                    elif event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_ESCAPE:
                            menu_active = False
                            paused = False
                            break
                        
                        # Handle menu input
                        result = menu.handle_input(event)
                        if result == 'back':
                            menu_active = False
                            paused = False
                        elif result == 'save':
                            self.handle_save_action(menu)
                        elif result == 'load':
                            if self.handle_load_action(menu):
                                menu_active = False
                                paused = False
                
                # Draw menu
                if paused:
                    self.screen.blit(background, (0, 0))
                    menu.draw()
                    pygame.display.flip()
                    self.clock.tick(30)
                    
        except Exception as e:
            print(f"Error in save/load menu: {e}")
            self.show_message("An error occurred in the menu", duration=2.0)
    def handle_save_action(self, menu):
        """Handle save game action."""
        try:
            success = self.save_system.save_game(self)
            if success:
                self.show_message("Game saved successfully!", duration=1.5)
            else:
                self.show_message("Failed to save game!", duration=1.5)
        except Exception as e:
            print(f"Error saving game: {e}")
            self.show_message("Error saving game!", duration=1.5)

    def handle_load_action(self, menu):
        """
        Handle load game action.
        Returns:
            bool: True if load successful, False otherwise
        """
        try:
            saves = self.save_system.list_saves()
            if saves and menu.selected_index < len(saves):
                if self.save_system.load_game(saves[menu.selected_index]['name'], self):
                    self.show_message("Game loaded successfully!", duration=1.5)
                    return True
                else:
                    self.show_message("Failed to load game!", duration=1.5)
            return False
        except Exception as e:
            print(f"Error loading game: {e}")
            self.show_message("Error loading game!", duration=1.5)
            return False
            
    def reset_game(self):
        """Reset the game state for a new playthrough."""
        self.current_sequence_index = 0
        self.in_tutorial = True
        if hasattr(self, 'tutorial_system'):
            self.tutorial_system.reset()
        # Any other state variables that need resetting

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