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
from save_system import SaveSystem, SaveLoadMenu
from dialogue import DialogueSystem
from visual_assets import VisualNovelAssets
from leaderboard import *
import os
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
        self.dialogue_system = DialogueSystem(self.screen, self.clock)
        self.player_name = ""
        
        # Initialize tutorial system first
        self.tutorial_system = TutorialSystem(self)
        self.in_tutorial = True
        
        # Initialize game components
        sound_manager.play_music()
        self.game_start_time = time.time()  # Overall game start time - never changes
        self.elapsed_time = 0
        self.pause_time = 0  # Track total paused time
        self.is_paused = False  # Track pause state
        self.pause_start = 0  # Track when pauses begin
        
        # Load sprite sheets
        self.character_spritesheet = Spritesheet('LEGEND OF ZAHIR/main character strip.png')
        self.enemy_spritesheet = Spritesheet('LEGEND OF ZAHIR/skeleton_strip.png')
        self.terrain_spritesheet = Spritesheet('LEGEND OF ZAHIR/dungeon2.jpg')
        
        # Initialize game state
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
        self.game_sequence = ['main', 'candle memory', 'main', 'timezone', 'main', 'language', 'main', 'continent', 'main', 'boss']
        self.current_sequence_index = 0
        self.total_sequences = len(self.game_sequence)
        
        # Initialize save system
        self.save_system = SaveSystem()
        
        self.paused = False
        self.keys_pressed = set()  # Track currently pressed keys
        
        # Initialize leaderboard
        self.leaderboard_system = LeaderboardSystem()

    def game_loop(self):
        """
        Main game loop with integrated dialogue and tutorial systems.
        """
        # Show intro dialogue before starting
        self.dialogue_system.show_dialogue('intro')
        
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
                    self.dialogue_system.show_dialogue('after_tutorial')
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
        
        # Main game sequence loop
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
                # Handle dialogue sequences based on completion
                if current_mode == 'main':
                    # Show appropriate dialogue based on sequence
                    if self.current_sequence_index == 0:  # After first main sequence
                        self.dialogue_system.show_dialogue('after_tutorial')
                        self.show_level_complete_dialogue("Press Enter for Candle Memory Challenge")
                    elif self.current_sequence_index == 2:  # After memory game
                        self.dialogue_system.show_dialogue('after_memory')
                        self.show_level_complete_dialogue("Press Enter for Timezone Challenge")
                    elif self.current_sequence_index == 4:  # After timezone game
                        self.dialogue_system.show_dialogue('after_timezone')
                        self.show_level_complete_dialogue("Press Enter for Language Challenge")
                    elif self.current_sequence_index == 6:  # After language game
                        self.dialogue_system.show_dialogue('after_language')
                        self.show_level_complete_dialogue("Press Enter for The Continent Challenge")
                    elif self.current_sequence_index == 8:  # Before boss battle
                        self.dialogue_system.show_dialogue('after_continent')
                        self.dialogue_system.show_dialogue('before_boss')
                        self.show_level_complete_dialogue("Press Enter for Final Boss Battle")
                elif current_mode == 'candle memory':
                    self.show_level_complete_dialogue("Candle Memory completed! Press Enter to continue")
                elif current_mode == 'timezone':
                    self.show_level_complete_dialogue("Timezone Challenge completed! Press Enter to continue")
                elif current_mode == 'language':
                    self.show_level_complete_dialogue("Language Challenge completed! Press Enter to continue")
                elif current_mode == 'continent':
                    self.show_level_complete_dialogue("Continent Challenge completed! Press Enter to continue")
                elif current_mode == 'boss':
                    self.dialogue_system.show_dialogue('victory')
                
                self.current_sequence_index += 1
                
            elif result == "died":
                if not self.restart_level_prompt():
                    self.running = False
                    break
        
        # Game completion check
        if self.current_sequence_index >= self.total_sequences:
            self.dialogue_system.show_dialogue('victory')
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
            self.elapsed_time = self.get_elapsed_time()

            # Check player health
            if self.player.health <= 0:
                self.playing = False

            # Check for bullet collisions
            hits = pygame.sprite.groupcollide(self.bullets, self.enemies, True, True)
            
            # Check if all enemies are defeated
            if len(self.enemies) == 0:
                self.playing = False
                    
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
        Draw the cumulative game timer on screen.
        Formats time as MM:SS if under an hour, or HH:MM:SS if over an hour.
        """
        total_seconds = int(self.elapsed_time)
        if total_seconds < 3600:  # Less than an hour
            minutes = total_seconds // 60
            seconds = total_seconds % 60
            time_str = f"{minutes:02d}:{seconds:02d}"
        else:  # More than an hour
            hours = total_seconds // 3600
            minutes = (total_seconds % 3600) // 60
            seconds = total_seconds % 60
            time_str = f"{hours:02d}:{minutes:02d}:{seconds:02d}"
        
        timer_text = self.font.render(f"Total Time: {time_str}", True, WHITE)
        timer_rect = timer_text.get_rect(topright=(WIDTH - 20, 10))
        self.screen.blit(timer_text, timer_rect)

    def pause_timer(self):
        """Pause the game timer and record pause start time."""
        if not self.is_paused:
            self.is_paused = True
            self.pause_start = time.time()

    def resume_timer(self):
        """Resume the game timer and update total pause time."""
        if self.is_paused:
            self.pause_time += time.time() - self.pause_start
            self.is_paused = False
            self.pause_start = 0

    def get_elapsed_time(self):
        """
        Calculate actual elapsed time excluding pauses from the very start of the game.
        
        Returns:
            float: Total elapsed time in seconds, excluding paused time
        """
        current_time = time.time()
        current_pause = current_time - self.pause_start if self.is_paused else 0
        return current_time - self.game_start_time - self.pause_time - current_pause

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


    def run_minigame_sequence(self, minigame_type):
        """
        Run a specific minigame while maintaining the cumulative timer.
        """
        try:
            # No need to pause timer during minigame transitions anymore
            # Just run the minigame while timer continues
            result = None
            if minigame_type == 'candle memory':
                result = run_memory_game(self.screen, self.clock)
            elif minigame_type == 'timezone':
                result = run_timezone_game(self.screen, self.clock)
            elif minigame_type == 'language':
                result = run_language_matching_game()
            elif minigame_type == 'continent':
                result = run_continent_game(self.screen, self.clock)
            elif minigame_type == 'boss':
                result = run_boss_battle()
            
            return result
        except Exception as e:
            print(f"Error in minigame sequence: {e}")
            return "quit"
    
    def run_main_game_sequence(self):
        """
        Run a main game sequence without resetting timer.
        """
        try:
            # Set up new game state
            self.new()  # No longer resets timer
            
            # Run main game loop until completion or death
            while self.playing and self.running:
                self.events()
                self.update()
                self.draw()
                self.clock.tick(FPS)

                if self.player.health <= 0:
                    return "died"
                
                # Check if all enemies are defeated
                if len(self.enemies) == 0:
                    return "completed"
                    
            # If we broke out of the loop due to self.running becoming False
            if not self.running:
                return "quit"
                
            return "completed"
            
        except Exception as e:
            print(f"Error in main game sequence: {e}")
            return "quit"

    def show_progress(self):
        """
        Show current progress in game sequence
        """
        sequence_names = {
            'main': 'Main Game',
            'candle memory': 'Candle Challenge',
            'timezone': 'TIMEZONE Challenge',
            'language': 'Language Match',
            'continent': 'Continent Challenge',
            'boss': 'Boss Battle'
        }
        
        current = self.game_sequence[self.current_sequence_index]
        progress_text = f"Current: {sequence_names[current]} ({self.current_sequence_index + 1}/{self.total_sequences})"
        text_surface = self.font.render(progress_text, True, WHITE)
        self.screen.blit(text_surface, (10, 10))

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
        Display the final results screen showing total cumulative time and score.
        Only shows and records leaderboard if player completed the entire game.
        """
        # Get final total time from the very start of the game
        final_time = int(self.get_elapsed_time())
        
        # Calculate time string for display
        if final_time < 3600:  # Less than an hour
            time_str = f"{final_time // 60:02d}:{final_time % 60:02d}"
        else:  # More than an hour
            hours = final_time // 3600
            minutes = (final_time % 3600) // 60
            seconds = final_time % 60
            time_str = f"{hours:02d}:{minutes:02d}:{seconds:02d}"
        
        # Check if game was completed (reached the end of all sequences)
        game_completed = self.current_sequence_index >= self.total_sequences
        
        if game_completed:
            # Only check rank and add to leaderboard if game was completed
            rank = self.leaderboard_system.get_rank(final_time)
            if rank is not None:
                show_new_highscore(self.screen, self.font, rank, final_time)
                self.leaderboard_system.add_score(self.player_name, final_time)
        
        # Show completion or game over text
        if game_completed:
            text = self.font.render('Game Complete!', True, WHITE)
        else:
            text = self.font.render('Game Over', True, RED)
        text_rect = text.get_rect(center=(WIDTH/2, HEIGHT/2 - 50))
        
        # Show time text
        time_text = self.font.render(f'Total Time: {time_str}', True, WHITE)
        time_rect = time_text.get_rect(center=(WIDTH/2, HEIGHT/2))
        
        show_leaderboard = True
        while show_leaderboard:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return
                if event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN:
                    show_leaderboard = False
            
            self.screen.fill(BLACK)
            self.screen.blit(text, text_rect)
            self.screen.blit(time_text, time_rect)
            
            # Only show leaderboard if game was completed
            if game_completed:
                draw_leaderboard(self.screen, self.font, self.leaderboard_system)
            else:
                # Show message explaining why leaderboard isn't shown
                msg = self.font.render('Complete the game to appear on leaderboard!', True, YELLOW)
                msg_rect = msg.get_rect(center=(WIDTH/2, HEIGHT/2 + 50))
                self.screen.blit(msg, msg_rect)
                
                # Show continue prompt
                continue_text = self.font.render('Press ENTER to continue', True, WHITE)
                continue_rect = continue_text.get_rect(center=(WIDTH/2, HEIGHT - 50))
                self.screen.blit(continue_text, continue_rect)
            
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
        """Show the save/load menu while pausing the timer."""
        try:
            self.pause_timer()  # Pause timer during menu
            menu = SaveLoadMenu(self)
            menu_active = True
            paused = True
            
            # Store current screen
            background = pygame.Surface((WIDTH, HEIGHT))
            background.blit(self.screen, (0, 0))
            
            while menu_active and self.running and paused:
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        self.running = False
                        self.resume_timer()
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
                
                if paused:
                    self.screen.blit(background, (0, 0))
                    menu.draw()
                    pygame.display.flip()
                    self.clock.tick(30)
            
            self.resume_timer()  # Resume timer after menu closes
                    
        except Exception as e:
            print(f"Error in save/load menu: {e}")
            self.show_message("An error occurred in the menu", duration=2.0)
            self.resume_timer()

    def handle_save_action(self, menu):
        """Handle save game action with timer state."""
        try:
            # Add timer state to save data
            save_data = {
                'elapsed_time': self.elapsed_time,
                'start_time': self.start_time,
                'pause_time': self.pause_time
            }
            success = self.save_system.save_game(self, additional_data=save_data)
            if success:
                self.show_message("Game saved successfully!", duration=1.5)
            else:
                self.show_message("Failed to save game!", duration=1.5)
        except Exception as e:
            print(f"Error saving game: {e}")
            self.show_message("Error saving game!", duration=1.5)

    def handle_load_action(self, menu):
        """
        Handle load game action and restore timer state.
        
        Returns:
            bool: True if load successful, False otherwise
        """
        try:
            saves = self.save_system.list_saves()
            if saves and menu.selected_index < len(saves):
                save_data = self.save_system.load_game(saves[menu.selected_index]['name'], self)
                if save_data:
                    # Restore timer state
                    self.elapsed_time = save_data.get('elapsed_time', self.elapsed_time)
                    self.start_time = save_data.get('start_time', self.start_time)
                    self.pause_time = save_data.get('pause_time', self.pause_time)
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
        """
        Reset game state while preserving the cumulative timer.
        Note: This only resets game progress, not the elapsed time.
        """
        self.minigames_completed = 0
        self.current_level = 0
        self.in_main_game = True
        self.current_minigame_index = 0
        self.current_sequence_index = 0
        self.in_tutorial = True
        
        # Reset tutorial if it exists
        if hasattr(self, 'tutorial_system'):
            self.tutorial_system.reset()
        
        # Reset sprite groups
        self.allsprites = pygame.sprite.LayeredUpdates()
        self.blocks = pygame.sprite.LayeredUpdates()
        self.enemies = pygame.sprite.LayeredUpdates()
        self.attacks = pygame.sprite.LayeredUpdates()
        self.bullets = pygame.sprite.LayeredUpdates()
        
        # Recreate game world
        self.createTilemap()
        self.create_enemies()
        
        # Note: We don't reset these time-related variables
        # self.start_time
        # self.elapsed_time
        # self.pause_time
        # self.is_paused
        # self.pause_start

# Game initialization and main loop
g = Game()  # Create a new Game instance
g.intro_screen()  # Show the intro screen
g.game_loop()  # Start the main game loop
pygame.quit()  # Quit pygame
sys.exit()  # Exit the program