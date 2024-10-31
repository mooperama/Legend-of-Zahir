import pygame
from sprites import *
from config_settings import *
from enemies import *
from player import *
from MINIGAME2 import run_timezone_game
from MINIGAME3 import run_continent_game
from MINIGAME4 import main as run_language_matching_game
from MINIGAME5 import main as run_boss_battle
from soundmanager import sound_manager
from tutorial import *
from save_system import *
import sys
import time

"""
i luv jessica ng (i cant commit)
"""
class Game:
    def __init__(self):
        pygame.init()
        pygame.mixer.init()
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("Legend of Zahir")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.Font(None, 32)
        self.running = True
        self.player_name = ""  # Add this line to store player name
        
        # Initialize tutorial system first
        self.tutorial_system = TutorialSystem(self)
        self.in_tutorial = True
        
        # Initialize game components
        sound_manager.play_music()
        self.start_time = time.time()
        self.elapsed_time = 0
        
        # Load sprite sheets
        self.character_spritesheet = Spritesheet('LEGEND OF ZAHIR/knight_strip.png')
        self.enemy_spritesheet = Spritesheet('LEGEND OF ZAHIR/skeleton_strip.png')
        self.terrain_spritesheet = Spritesheet('LEGEND OF ZAHIR/dungeon2.jpg')
        
        # Initialize game state immediately
        self.allsprites = pygame.sprite.LayeredUpdates()
        self.blocks = pygame.sprite.LayeredUpdates()
        self.enemies = pygame.sprite.LayeredUpdates()
        self.attacks = pygame.sprite.LayeredUpdates()
        self.bullets = pygame.sprite.LayeredUpdates()
        
        # Create initial game world
        self.createTilemap()
        self.create_enemies()
        self.playing = True
        
        # Game sequence setup
        self.game_sequence = ['main', 'timezone', 'main', 'language','main','continent','main', 'boss']
        self.current_sequence_index = 0
        self.total_sequences = len(self.game_sequence)
           
        # Add after other initializations
        self.save_system = ZahirSaveSystem()

    # Add these methods to the Game class
    def save_current_game(self):
        return self.save_system.save_game(self)

    def load_saved_game(self, save_name):
        return self.save_system.load_game(save_name, self)

    def show_save_load_menu(self):
        """Show a menu for saving/loading games"""
        saves = self.save_system.list_saves()
        # Implement menu UI here using pygame
        # You can add this to your pause menu or create a separate menu

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
                    if next_mode == 'timezone':
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

    def events(self):
        """
        Handle game events, including quitting and mouse clicks.
        """
        events = pygame.event.get()
        
        # Handle tutorial input first
        if hasattr(self, 'tutorial_system') and self.tutorial_system.active:
            self.tutorial_system.handle_input(events)
            
        for event in events:
            if event.type == pygame.QUIT:
                self.playing = False
                self.running = False
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1 and not self.tutorial_system.active:
                    self.player.shoot(pygame.mouse.get_pos())
                    sound_manager.play_sound('bullet')

    def update(self):
        """
        Update game objects and check for game over or victory conditions.
        """
        self.allsprites.update()  # Update all sprite objects
        self.elapsed_time = time.time() - self.start_time  # Update elapsed time

        if self.player.health <= 0:  # If player's health is depleted
            self.playing = False  # End the game

        # Check for bullet collisions with enemies
        hits = pygame.sprite.groupcollide(self.bullets, self.enemies, True, True)
        for hit in hits:
            # Handle enemy hit (could add score, play sound, etc.)
            pass

        if len(self.enemies) == 0:  # If all enemies are defeated
            self.playing = False  # End the current level

    def draw(self):
            """
            Draw all game objects and UI elements to the screen.
            """
            self.screen.fill(BACKGROUND_COLOR)
            self.allsprites.draw(self.screen)
            self.player.draw_health_bar(self.screen)
            self.player.draw_exp_bar(self.screen)
            self.player.draw_stats(self.screen)
            self.draw_timer()
            
            # Draw player name
            name_text = self.font.render(self.player_name, True, BLACK)
            self.screen.blit(name_text, (10, 10))

            # Draw tutorial if active
            if self.tutorial_system.active:
                self.tutorial_system.draw(self.screen)
                
            pygame.display.update()

    def draw_timer(self):
        """
        Draw the game timer on the screen.
        """
        timer_text = self.font.render(f"Time: {int(self.elapsed_time)}s", True, WHITE)
        self.screen.blit(timer_text, (WIDTH - 150, 10))  # Draw timer in top-right corner

    def main(self):
        """
        Main game loop that runs while the game is playing.
        """
        while self.playing:
            self.events()  # Handle events
            self.update()  # Update game objects
            self.draw()  # Draw the game
            self.clock.tick(FPS)  # Control the frame rate

            if self.player.health <= 0:
                return "died"  # Player died

        if len(self.enemies) == 0:
            return "completed"  # Level completed


    def create_enemies(self):
        for _ in range(3):
            enemy = Enemy.create_random(self)
            self.enemies.add(enemy)
            self.allsprites.add(enemy)  # Changed from self.add(enemy)

    def game_over(self):
        """
        Display the game over screen and handle restart or quit options.
        """
        text = self.font.render('GAME OVER', True, WHITE)
        text_rect = text.get_rect(center=(WIDTH/2, HEIGHT/2 - 50))

        time_text = self.font.render(f'Time: {int(self.elapsed_time)}s', True, WHITE)
        time_rect = time_text.get_rect(center=(WIDTH/2, HEIGHT/2))

        restart_button = pygame.Rect(WIDTH/2 - 70, HEIGHT/2 + 50, 140, 40)
        restart_text = self.font.render('Restart', True, BLACK)

        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                    return
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if restart_button.collidepoint(event.pos):
                        self.reset_game()
                        return

            self.screen.fill(BLACK)
            self.screen.blit(text, text_rect)
            self.screen.blit(time_text, time_rect)
            pygame.draw.rect(self.screen, WHITE, restart_button)
            self.screen.blit(restart_text, (restart_button.x + 30, restart_button.y + 10))
            pygame.display.update()
            self.clock.tick(FPS)

    def run_minigame(self, minigame):
        """
        Run the selected minigame.

        Args:
            minigame (str): The name of the minigame to run.

        Returns:
            str: The result of the minigame ("completed" or "died").
        """
        if minigame == 'timezone':
            result = run_timezone_game(self.screen, self.clock)
        elif minigame == 'language':
            result = run_language_matching_game()
        elif minigame == 'continent':
            result = run_continent_game()
        elif minigame == 'boss':
            result = run_boss_battle()
        
        self.minigames_completed += 1
        self.current_level += 1
        return result

    def show_congratulations(self):
        """
        Display the victory screen and handle play again or quit options.
        """
        text = self.font.render('Congratulations! You won!', True, WHITE)
        text_rect = text.get_rect(center=(WIDTH/2, HEIGHT/2 - 125))

        time_text = self.font.render(f'Time: {int(self.elapsed_time)}s', True, WHITE)
        time_rect = time_text.get_rect(center=(WIDTH/2, HEIGHT/2 - 75))

        play_again_button = pygame.Rect(WIDTH/2 - 70, HEIGHT/2 + 25, 140, 40)
        play_again_text = self.font.render('Play Again', True, BLACK)

        quit_button = pygame.Rect(WIDTH/2 + 85, HEIGHT/2 + 25, 140, 40)
        quit_text = self.font.render('Quit', True, BLACK)

        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                    return False
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if play_again_button.collidepoint(event.pos):
                        self.reset_game()
                        return True
                    elif quit_button.collidepoint(event.pos):
                        self.running = False
                        return False

            self.screen.fill(BLACK)
            self.screen.blit(text, text_rect)
            self.screen.blit(time_text, time_rect)
            pygame.draw.rect(self.screen, WHITE, play_again_button)
            self.screen.blit(play_again_text, (play_again_button.x + 20, play_again_button.y + 10))
            pygame.draw.rect(self.screen, WHITE, quit_button)
            self.screen.blit(quit_text, (quit_button.x + 45, quit_button.y + 10))
            pygame.display.update()
            self.clock.tick(FPS)

    def show_level_complete_dialogue(self, message):
        """
        Display a dialogue box with a message when a level is completed.

        Args:
            message (str): The message to display in the dialogue box.
        """
        dialogue_box = pygame.Surface((500, 100))
        dialogue_box.fill(WHITE)
        dialogue_box_rect = dialogue_box.get_rect(center=(WIDTH/2, HEIGHT/2))

        text = self.font.render(message, True, BLACK)
        text_rect = text.get_rect(center=(250, 50))
        dialogue_box.blit(text, text_rect)

        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                    return
                if event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN:
                    return

            self.screen.blit(dialogue_box, dialogue_box_rect)
            pygame.display.update()
            self.clock.tick(FPS)

    def run_main_game(self):
        """
        Run the main game until completion or player death.
        """
        while self.running:
            self.new()  # Set up a new game state
            result = self.main()  # Run the main game loop
            if result == "completed":
                # Remove the selection and directly go to the first minigame
                self.show_level_complete_dialogue("Press Enter to start PEMDAS Challenge")
                self.in_main_game = False
                break
            elif result == "died":
                if not self.restart_level_prompt():
                    self.running = False
                    break

    
    def run_main_game_sequence(self):
        """
        Run a main game sequence
        """
        self.new()  # Set up new game state
        return self.main()  # Run main game and return result

    def run_minigame_sequence(self, minigame_type):
        """
        Run a specific minigame
        """
        if minigame_type == 'timezone':
            return run_timezone_game(self.screen, self.clock)
        elif minigame_type == 'language':
            return run_language_matching_game()
        elif minigame_type == 'continent':
            return run_continent_game(self.screen, self.clock)
        elif minigame_type == 'boss':
            return run_boss_battle()
        return "quit"

    def show_progress(self):
        """
        Show current progress in game sequence
        """
        sequence_names = {
            'main': 'Main Game',
            'timezone': 'TIMEZONE Challenge',
            'language': 'Language Match',
            'continent': 'Continent Challenge',
            'boss': 'Boss Battle'
        }
        
        current = self.game_sequence[self.current_sequence_index]
        progress_text = f"Current: {sequence_names[current]} ({self.current_sequence_index + 1}/{self.total_sequences})"
        text_surface = self.font.render(progress_text, True, WHITE)
        self.screen.blit(text_surface, (10, 10))

    def run_current_minigame(self):
        """
        Run the current minigame and return the result.
        """
        # Force the order of minigames
        if self.current_minigame_index == 0:
            return run_timezone_game(self.screen, self.clock)
        elif self.current_minigame_index == 1:
            return run_language_matching_game()
        elif self.current_minigame_index == 2:
            return run_continent_game()
        elif self.current_minigame_index == 3:
            return run_boss_battle()
        
        return "quit"

    def restart_level_prompt(self):
        """
        Display a prompt asking if the player wants to restart the level after dying.

        Returns:
            bool: True if the player wants to restart, False otherwise.
        """
        prompt_box = pygame.Surface((400, 150))
        prompt_box.fill(WHITE)
        prompt_box_rect = prompt_box.get_rect(center=(WIDTH/2, HEIGHT/2))

        text = self.font.render("You died! Restart level?", True, BLACK)
        text_rect = text.get_rect(center=(200, 50))
        prompt_box.blit(text, text_rect)

        yes_button = pygame.Rect(50, 100, 100, 40)
        no_button = pygame.Rect(250, 100, 100, 40)

        pygame.draw.rect(prompt_box, GREEN, yes_button)
        pygame.draw.rect(prompt_box, RED, no_button)

        yes_text = self.font.render("Yes", True, BLACK)
        no_text = self.font.render("No", True, BLACK)

        prompt_box.blit(yes_text, (85, 110))
        prompt_box.blit(no_text, (285, 110))

        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return False
                if event.type == pygame.MOUSEBUTTONDOWN:
                    mouse_pos = pygame.mouse.get_pos()
                    adjusted_pos = (mouse_pos[0] - prompt_box_rect.x, mouse_pos[1] - prompt_box_rect.y)
                    if yes_button.collidepoint(adjusted_pos):
                        return True
                    elif no_button.collidepoint(adjusted_pos):
                        return False

            self.screen.blit(prompt_box, prompt_box_rect)
            pygame.display.update()
            self.clock.tick(FPS)

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

    def reset_game(self):
        """
        Reset all game state variables to start a new game.
        """
        self.minigames_completed = 0
        self.current_level = 0
        self.elapsed_time = 0
        self.in_main_game = True
        self.current_minigame_index = 0
        # Reset any other necessary game state variables

# Game initialization and main loop
g = Game()  # Create a new Game instance
g.intro_screen()  # Show the intro screen
g.game_loop()  # Start the main game loop
pygame.quit()  # Quit pygame
sys.exit()  # Exit the program