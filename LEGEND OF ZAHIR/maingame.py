import pygame
from sprites import *
from config_settings import *
from enemies import *
from player import *
from tiles import *
from doors import *
from MINIGAME1 import run_memory_game
from MINIGAME2 import run_timezone_game
from MINIGAME3 import run_continent_game
from MINIGAME4 import main as run_language_matching_game
from MINIGAME5 import main as run_boss_battle
from soundmanager import sound_manager
from tutorial import *
from dialogue import DialogueSystem
from visual_assets import VisualNovelAssets
from leaderboard import *
import os
import sys
import time


class Game:
    def __init__(self):
        pygame.init()
        pygame.mixer.init()
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("Legend of Zahir")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.Font('LEGEND OF ZAHIR/assets/fonts/nokiafc22.ttf', 24)
        self.running = True
        self.dialogue_system = DialogueSystem(self.screen, self.clock)
        self.player_name = ""
        self.background = Background(self)
        
        # Initialize tutorial system first
        self.tutorial_system = TutorialSystem(self)
        self.in_tutorial = True
        
        # Initialize game components
        sound_manager.play_music()
        self.game_start_time = time.time()
        self.elapsed_time = 0
        self.pause_time = 0
        self.is_paused = False
        self.pause_start = 0

        # Initialize sound manager and load button sound
        sound_manager.load_sound('button_click', 'buttons.mp3')  # Add button click sound
        sound_manager.play_music()
        
        # Load sprite sheets
        self.character_spritesheet = Spritesheet('LEGEND OF ZAHIR/main character strip.png')
        self.enemy_spritesheet = Spritesheet('LEGEND OF ZAHIR/06-conjurer.png')
        self.terrain_spritesheet = Spritesheet('LEGEND OF ZAHIR/dungeon2.jpg')
        
        # Initialize game state
        self.allsprites = pygame.sprite.LayeredUpdates()
        self.blocks = pygame.sprite.LayeredUpdates()
        self.enemies = pygame.sprite.LayeredUpdates()
        self.attacks = pygame.sprite.LayeredUpdates()
        self.bullets = pygame.sprite.LayeredUpdates()

        # Modified door-related attributes with reset functionality
        self.door_sprite = None
        self.door_visible = False
        self.door_prompt_visible = False
        self.door_position = None
        self.enemies_defeated = False  # New flag to track if enemies are defeated
        
        # Game sequence setup
        self.game_sequence = ['main', 'candle memory', 'main', 'timezone', 'main', 'language', 'main', 'continent', 'main', 'boss']
        self.current_sequence_index = 0
        self.total_sequences = len(self.game_sequence)

        self.game_start_time = None  # Will be set after tutorial
        self.elapsed_time = 0
        self.pause_time = 0
        self.is_paused = False
        self.pause_start = 0
        self.in_tutorial = True
        
        self.paused = False
        self.keys_pressed = set()
        self.ammo_system = AmmoSystem() #bullet limits
        
        # Initialize leaderboard
        self.leaderboard_system = LeaderboardSystem()
        
        # Create initial game world
        self.createTilemap()
        self.create_enemies()
        self.playing = True


    def toggle_pause(self):
        """Toggle the pause state of the game and handle timer accordingly."""
        if not self.in_tutorial:  # Only allow pause outside tutorial
            self.paused = not self.paused
            if self.paused:
                self.pause_timer()
                self.show_pause_menu()
            else:
                self.resume_timer()

    def show_pause_menu(self):
        """Display the pause menu."""
        pause_overlay = pygame.Surface((WIDTH, HEIGHT))
        pause_overlay.fill((0, 0, 0))
        pause_overlay.set_alpha(128)
        
        # Create menu text
        menu_font = pygame.font.Font('LEGEND OF ZAHIR/assets/fonts/nokiafc22.ttf', 36)
        pause_text = menu_font.render("PAUSED", True, WHITE)
        resume_text = self.font.render("Press ESC to Resume", True, WHITE)
        quit_text = self.font.render("Press Q to Quit", True, WHITE)
        
        # Position text
        pause_rect = pause_text.get_rect(center=(WIDTH/2, HEIGHT/2 - 50))
        resume_rect = resume_text.get_rect(center=(WIDTH/2, HEIGHT/2 + 20))
        quit_rect = quit_text.get_rect(center=(WIDTH/2, HEIGHT/2 + 60))
        
        while self.paused and self.running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                    self.paused = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        self.paused = False
                        self.resume_timer()  # Make sure to resume timer when exiting pause menu
                    elif event.key == pygame.K_q:
                        self.running = False
                        self.paused = False
            
            # Draw pause menu
            self.screen.blit(pause_overlay, (0, 0))
            self.screen.blit(pause_text, pause_rect)
            self.screen.blit(resume_text, resume_rect)
            self.screen.blit(quit_text, quit_rect)
            
            pygame.display.flip()
            self.clock.tick(30)

    def game_loop(self):
        """Main game loop with integrated dialogue and tutorial systems."""
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
                
                # Handle tutorial system input
                self.tutorial_system.handle_input(events)
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    self.player.shoot(pygame.mouse.get_pos())
                    sound_manager.play_sound('bullet')
                
                # Check if tutorial is completed
                if self.tutorial_system.tutorial_completed:
                    self.end_tutorial()  # Start timing after tutorial
                    self.createTilemap()  # Recreate map with enemies
                    self.create_enemies()  # Add random enemies
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
        
        # Main game sequence loop with proper bounds checking
        while self.running and self.current_sequence_index < len(self.game_sequence):
            try:
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
                        # Show appropriate dialogue based on sequence index
                        if self.current_sequence_index == 0:
                            self.dialogue_system.show_dialogue('after_tutorial')
                        elif self.current_sequence_index == 2:
                            self.dialogue_system.show_dialogue('after_memory')
                        elif self.current_sequence_index == 4:
                            self.dialogue_system.show_dialogue('after_timezone')
                        elif self.current_sequence_index == 6:
                            self.dialogue_system.show_dialogue('after_language')
                        elif self.current_sequence_index == 8:
                            self.dialogue_system.show_dialogue('after_continent')
                            self.dialogue_system.show_dialogue('before_boss')
                    
                    # Safely increment sequence index
                    if self.current_sequence_index < len(self.game_sequence) - 1:
                        self.current_sequence_index += 1
                    else:
                        break
                        
                elif result == "died":
                    if not self.restart_level_prompt():
                        self.running = False
                        break
                        
            except IndexError as e:
                print(f"Sequence index error: {e}")
                self.current_sequence_index = len(self.game_sequence) - 1
                break
            except Exception as e:
                print(f"Unexpected error in game loop: {e}")
                self.running = False
                break
        
        # Game completion check - Modified to handle victory properly
        if self.running and self.current_sequence_index >= len(self.game_sequence) - 1:
            # Check if the last sequence was completed successfully
            if self.game_sequence[-1] == 'boss' and result == "completed":
                self.dialogue_system.show_dialogue('victory')  # Show victory dialogue once
                self.show_final_results(victory=True)  # Pass victory flag
            else:
                self.show_final_results(victory=False)  # Regular game over

    def name_entry_screen(self):
        """
        Display a screen for the player to enter their name.
        Returns the entered name.
        """
        input_box = pygame.Rect(WIDTH/2 - 150, HEIGHT/2, 200, 36)
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

    def show_production_screen(self):
        """Display the production company screen with fade effects."""
        # Setup fade effect
        fade_surface = pygame.Surface((WIDTH, HEIGHT))
        fade_surface.fill(BLACK)
        
        # Create the text
        font_large = pygame.font.Font('LEGEND OF ZAHIR/assets/fonts/nokiafc22.ttf', 48)  # Larger font for production text
        production_text = font_large.render("Produced by", True, WHITE)
        team_text = font_large.render("Learning Team 7", True, WHITE)
        
        production_rect = production_text.get_rect(center=(WIDTH/2, HEIGHT/2 - 40))
        team_rect = team_text.get_rect(center=(WIDTH/2, HEIGHT/2 + 40))
        
        # Fade in
        for alpha in range(0, 255, 5):
            self.screen.fill(BLACK)
            
            # Draw text
            self.screen.blit(production_text, production_rect)
            self.screen.blit(team_text, team_rect)
            
            # Apply fade
            fade_surface.set_alpha(255 - alpha)
            self.screen.blit(fade_surface, (0, 0))
            
            pygame.display.flip()
            pygame.time.delay(20)
        
        # Hold the screen
        pygame.time.delay(2000)  # Show for 2 seconds
        
        # Fade out
        for alpha in range(0, 255, 5):
            self.screen.fill(BLACK)
            
            # Draw text
            self.screen.blit(production_text, production_rect)
            self.screen.blit(team_text, team_rect)
            
            # Apply fade
            fade_surface.set_alpha(alpha)
            self.screen.blit(fade_surface, (0, 0))
            
            pygame.display.flip()
            pygame.time.delay(20)

    def start_game_sequence(self):
        """Handle the complete game startup sequence."""
        self.show_production_screen()  # Show production company screen first
        self.loading_screen()  # Then show loading screen
        self.main_menu()  # Then show main menu
    

    def loading_screen(self):
        """Display a loading screen with a progress bar."""
        self.screen.fill(BLACK)
        
        # Create loading text
        loading_text = self.font.render("Loading...", True, WHITE)
        loading_rect = loading_text.get_rect(center=(WIDTH/2, HEIGHT/2 - 50))
        
        # Create progress bar background
        bar_width = 400
        bar_height = 40
        bar_bg_rect = pygame.Rect(WIDTH/2 - bar_width/2, HEIGHT/2, bar_width, bar_height)
        
        # Simulate loading with progress bar
        for progress in range(101):
            # Calculate progress bar fill width
            fill_width = (progress / 100) * bar_width
            fill_rect = pygame.Rect(WIDTH/2 - bar_width/2, HEIGHT/2, fill_width, bar_height)
            
            # Draw loading screen
            self.screen.fill(BLACK)
            self.screen.blit(loading_text, loading_rect)
            pygame.draw.rect(self.screen, GRAY, bar_bg_rect, 2)  # Border
            pygame.draw.rect(self.screen, WHITE, fill_rect)
            
            # Add percentage text
            percent_text = self.font.render(f"{progress}%", True, WHITE)
            percent_rect = percent_text.get_rect(center=(WIDTH/2, HEIGHT/2 + bar_height + 20))
            self.screen.blit(percent_text, percent_rect)
            
            pygame.display.flip()
            pygame.time.delay(10)  # Control loading speed

    def main_menu(self):
        """Display the main menu with proper font sizes and game logo."""
        try:
            background = pygame.image.load('LEGEND OF ZAHIR/menu_background.png')
            background = pygame.transform.scale(background, (WIDTH, HEIGHT))
        except:
            print("Could not load menu background image")
            background = None

        # Create fonts of different sizes for the title and menu items
        button_font = pygame.font.Font('LEGEND OF ZAHIR/assets/fonts/nokiafc22.ttf', 20)

        # Colors
        BUTTON_BG = (67, 56, 202)  # Base color
        BUTTON_HOVER = (99, 102, 241)  # Hover color
        BUTTON_BORDER = (129, 140, 248)  # Border color
        BUTTON_SHADOW = (30, 27, 75)  # Shadow color

        
        # Button settings
        button_width = 200  # Reduced width to match font size
        button_height = 40  # Reduced height to match font size
        button_spacing = 20
        start_y = HEIGHT/2 + 50
        shadow_offset = 3  # Slightly reduced shadow for smaller buttons
        
        buttons = {
            'new_game': {
                'rect': pygame.Rect(WIDTH/2 - button_width/2, start_y, button_width, button_height),
                'text': 'New Game',
                'action': self.start_new_game
            },
            'leaderboard': {
                'rect': pygame.Rect(WIDTH/2 - button_width/2, start_y + button_height + button_spacing, 
                                button_width, button_height),
                'text': 'Leaderboard',
                'action': self.show_leaderboard_screen
            },
            'quit': {
                'rect': pygame.Rect(WIDTH/2 - button_width/2, start_y + (button_height + button_spacing) * 2, 
                                button_width, button_height),
                'text': 'Quit',
                'action': self.quit_game
            }
        }

        def draw_button(surface, rect, text, is_selected, is_pressed=False):
            """Draw a single button with proper sizing and styling."""
            # Shadow/3D effect
            shadow_rect = rect.copy()
            shadow_rect.y += shadow_offset
            pygame.draw.rect(surface, BUTTON_SHADOW, shadow_rect, border_radius=8)
            
            # Main button
            button_rect = rect.copy()
            if is_pressed:
                button_rect.y += shadow_offset
                color = BUTTON_HOVER
            else:
                color = BUTTON_HOVER if is_selected else BUTTON_BG
            
            pygame.draw.rect(surface, color, button_rect, border_radius=8)
            
            # Gradient effect
            gradient_rect = button_rect.copy()
            gradient_rect.height = button_rect.height // 2
            pygame.draw.rect(surface, (*[min(c + 20, 255) for c in color], 50), 
                            gradient_rect, border_radius=8)
            
            # Border
            pygame.draw.rect(surface, BUTTON_BORDER, button_rect, 2, border_radius=8)
            
            # Inner glow when selected
            if is_selected:
                glow_rect = button_rect.inflate(-4, -4)
                pygame.draw.rect(surface, (*BUTTON_BORDER, 100), glow_rect, 2, border_radius=6)
            
            # Text
            text_surface = button_font.render(text, True, WHITE)
            text_rect = text_surface.get_rect(center=button_rect.center)
            if is_pressed:
                text_rect.y += shadow_offset
            
            # Text shadow
            text_shadow = button_font.render(text, True, BUTTON_SHADOW)
            shadow_text_rect = text_rect.copy()
            shadow_text_rect.y += 2
            surface.blit(text_shadow, shadow_text_rect)
            
            # Main text
            surface.blit(text_surface, text_rect)
        # Main menu loop
        selected_button = None
        pressed_button = None
        menu_running = True
        while menu_running and self.running:
            mouse_pos = pygame.mouse.get_pos()
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                    return
                
                if event.type == pygame.MOUSEBUTTONDOWN:
                    for button_key, button in buttons.items():
                        if button['rect'].collidepoint(mouse_pos):
                            pressed_button = button_key
                            sound_manager.play_sound('button_click')
                
                if event.type == pygame.MOUSEBUTTONUP:
                    if pressed_button:
                        if buttons[pressed_button]['rect'].collidepoint(mouse_pos):
                            buttons[pressed_button]['action']()
                            if pressed_button == 'new_game':
                                menu_running = False
                            elif pressed_button == 'quit':
                                self.running = False
                                return
                        pressed_button = None
            
            # Update selected button
            selected_button = None
            for button_key, button in buttons.items():
                if button['rect'].collidepoint(mouse_pos):
                    selected_button = button_key
            
            # Draw menu
            if background:
                self.screen.blit(background, (0, 0))
            else:
                self.screen.fill((30, 27, 75))
        
            # Draw buttons
            for button_key, button in buttons.items():
                is_selected = button_key == selected_button
                is_pressed = button_key == pressed_button
                draw_button(self.screen, button['rect'], button['text'], 
                        is_selected, is_pressed)
            
            pygame.display.flip()
            self.clock.tick(FPS)

    def start_new_game(self):
        """Handle starting a new game."""
        self.loading_screen()  # Show loading screen
        self.player_name = self.name_entry_screen()  # Get player name
        return

    def show_leaderboard_screen(self):
        """Display the leaderboard screen with sound effects."""
        viewing = True
        while viewing and self.running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                    return
                if event.type == pygame.KEYDOWN:
                    if event.key in (pygame.K_ESCAPE, pygame.K_RETURN):
                        sound_manager.play_sound('button_click')
                        viewing = False
            
            self.screen.fill(BLACK)
            draw_leaderboard(self.screen, self.font, self.leaderboard_system)
            pygame.display.flip()
            self.clock.tick(FPS)

    def quit_game(self):
        """Handle quitting the game."""
        self.running = False
    
    def createTilemap(self):
        """Create the game world with door position fixed in the middle and ensure player creation."""
        # Clear existing sprites
        self.allsprites.empty()
        self.blocks.empty()
        self.enemies.empty()
        self.attacks.empty()
        self.bullets.empty()
        
        # Find the player's initial spawn position from the TILEMAP
        initial_pos = None
        for i, row in enumerate(TILEMAP):
            for j, column in enumerate(row):
                if column == "P":
                    initial_pos = (j, i)
                    break
            if initial_pos:
                break
        
        if not initial_pos:
            # If no player position found in TILEMAP, use a default position
            initial_pos = (1, len(TILEMAP) // 2)  # Left side, middle of map
        
        # Set door position to the center
        map_height = len(TILEMAP)
        map_width = len(TILEMAP[0])
        self.door_position = (map_width // 2, map_height // 2)
        
        # Create the player first to ensure it exists
        self.player = Player(self, initial_pos[0], initial_pos[1])
        self.player.name = self.player_name  # Make sure this line is present
        
        # Create actual tilemap
        for i, row in enumerate(TILEMAP):
            for j, column in enumerate(row):
                # Skip creating wall if it's where the door will be
                if (j, i) == self.door_position:
                    continue
                    
                if column == "W":
                    Block(self, j, i)
                if column == "E" and not self.in_tutorial:
                    Enemy(self, j, i)
        
        # Ensure player is added to sprite group
        self.allsprites.add(self.player)

    def show_door(self):
        """Create and show the door sprite at the fixed center position."""
        if not self.door_visible and not self.enemies_defeated:
            # Verify door position is valid
            if self.door_position is None:
                print("Error: Door position not set")
                return
                
            x, y = self.door_position
            
            # Create door sprite
            self.door_sprite = Door(self, x, y)
            self.allsprites.add(self.door_sprite)
            self.door_visible = True
            self.door_prompt_visible = False
            self.enemies_defeated = True
            
            # Remove any blocks at door position
            for block in self.blocks.copy():
                block_x = block.rect.x // TILESIZE
                block_y = block.rect.y // TILESIZE
                if block_x == x and block_y == y:
                    block.kill()
            
            self.show_message("A door has appeared!", 2.0)
            sound_manager.play_sound('door_appear')
    
    
    def ensure_door_accessibility(self):
        """Ensure there's space around the door for the player to access it."""
        if not self.door_position:
            return
            
        x, y = self.door_position
        
        # Check and remove blocks that might block door access
        for block in self.blocks.copy():
            block_x = block.rect.x // TILESIZE
            block_y = block.rect.y // TILESIZE
            
            # Remove blocks immediately adjacent to door
            if (abs(block_x - x) == 1 and (block_y == y or block_y == y + 1)):
                block.kill()

    def check_door_interaction(self):
        """Check if player is near the door and handle interaction."""
        if self.door_visible and self.door_sprite:
            # Calculate distance between player and door
            player_pos = pygame.math.Vector2(self.player.rect.center)
            door_pos = pygame.math.Vector2(self.door_sprite.rect.center)
            distance = player_pos.distance_to(door_pos)
            
            # Show prompt if player is near door
            if distance < 100:  # Adjust distance as needed
                self.show_door_prompt()
                # Check for interaction key (E)
                keys = pygame.key.get_pressed()
                if keys[pygame.K_e]:
                    try:
                        # Safely check next sequence
                        next_sequence_index = self.current_sequence_index + 1
                        if next_sequence_index < len(self.game_sequence):
                            next_sequence = self.game_sequence[next_sequence_index]
                            if next_sequence != 'main':
                                self.show_message(f"Entering the {next_sequence.title()} challenge...", 2.0)
                            else:
                                self.show_message("Entering the next area...", 2.0)
                        else:
                            self.show_message("Congratulations! You've completed the game!", 2.0)
                        return True
                    except IndexError:
                        print("Reached end of game sequences")
                        return True
            else:
                self.door_prompt_visible = False
        return False
    
    def show_door_prompt(self):
        """Display prompt to enter door."""
        if self.door_prompt_visible:
            prompt_text = self.font.render("Press E to enter door", True, WHITE)
            prompt_rect = prompt_text.get_rect(center=(WIDTH/2, HEIGHT - 50))
            self.screen.blit(prompt_text, prompt_rect)

    def new(self):
        """Set up new game state while preserving necessary data."""
        # Store the current name
        current_name = self.player_name
        
        # Initialize sprite groups
        self.allsprites = pygame.sprite.LayeredUpdates()
        self.blocks = pygame.sprite.LayeredUpdates()
        self.enemies = pygame.sprite.LayeredUpdates()
        self.attacks = pygame.sprite.LayeredUpdates()
        self.bullets = pygame.sprite.LayeredUpdates()
        
        # Reset door state
        self.door_visible = False
        self.door_prompt_visible = False
        self.door_sprite = None
        self.enemies_defeated = False
        
        # Create game world
        self.createTilemap()
        
        # Ensure player name is maintained
        self.player_name = current_name
        if hasattr(self, 'player'):
            self.player.name = current_name
        
        # Create enemies
        self.create_enemies()
        self.playing = True

# Replace the existing events method with this:
    def events(self):
        """Handle game events with pause functionality."""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.playing = False
                self.running = False
                
            # Handle key press events
            elif event.type == pygame.KEYDOWN:
                self.keys_pressed.add(event.key)
                
                # Handle pause with Escape key
                if event.key == pygame.K_ESCAPE:
                    self.toggle_pause()
                    
            # Handle key release events
            elif event.type == pygame.KEYUP:
                self.keys_pressed.discard(event.key)
                
            # Handle shooting when not paused
            if event.type == pygame.MOUSEBUTTONDOWN and not self.paused:
                if event.button == 1 and not self.tutorial_system.active:
                    if self.player.shoot(pygame.mouse.get_pos()):
                        sound_manager.play_sound('bullet')


# Replace the existing update method with this:
    def update(self):
        """Update game state with modified door logic."""
        if not self.paused:
            self.allsprites.update()
            self.elapsed_time = self.get_elapsed_time()
            
            # Check player health
            if self.player.health <= 0:
                self.playing = False
                return "died"
            
            # Check for bullet collisions
            hits = pygame.sprite.groupcollide(self.bullets, self.enemies, True, True)
            
            # Show door when all enemies are defeated
            if len(self.enemies) == 0 and not self.door_visible and not self.enemies_defeated:
                self.show_door()
                self.enemies_defeated = True
            
            # Handle door interaction
            if self.door_visible and self.door_sprite:
                player_pos = pygame.math.Vector2(self.player.rect.center)
                door_pos = pygame.math.Vector2(self.door_sprite.rect.center)
                distance = player_pos.distance_to(door_pos)
                
                if distance < 100:
                    self.door_prompt_visible = True
                    keys = pygame.key.get_pressed()
                    if keys[pygame.K_e]:
                        self.playing = False
                        return "completed"
                else:
                    self.door_prompt_visible = False
            
            return None
                    
    def draw(self):
        """Draw game state with all elements including door and prompts."""
        # Fill with background first
        if hasattr(self, 'background'):
            self.background.draw(self.screen)
        else:
            self.screen.fill(BACKGROUND_COLOR)
        
        # Draw all sprites
        self.allsprites.draw(self.screen)
        
        # Draw player UI elements
        self.player.draw_stats(self.screen)  # This now includes the player name
        self.draw_timer()
        
        # Draw door prompt if active
        if self.door_prompt_visible and self.door_visible:
            self.show_door_prompt()
        
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
        if not self.in_tutorial:
            self.is_paused = True
            self.pause_start = time.time()

    def resume_timer(self):
        """Resume the game timer and update total pause time."""
        if self.is_paused:
            pause_duration = time.time() - self.pause_start
            self.pause_time += pause_duration
            self.is_paused = False
            self.pause_start = 0

    def get_elapsed_time(self):
        """
        Calculate actual elapsed time, excluding tutorial and accounting for pauses and minigames.
        Returns the true elapsed time by subtracting all pause durations.
        """
        if self.game_start_time is None or self.in_tutorial:
            return 0
            
        current_time = time.time()
        
        # If currently paused, include the current pause duration
        current_pause_duration = (current_time - self.pause_start) if self.is_paused else 0
        
        # Calculate total time minus all pauses
        total_paused_time = self.pause_time + current_pause_duration
        elapsed = current_time - self.game_start_time - total_paused_time
        
        return max(0, elapsed)  # Ensure we never return negative time
        
    def end_tutorial(self):
        """Called when tutorial ends to start the actual game timer."""
        self.in_tutorial = False
        self.game_start_time = time.time()  # Start counting time only after tutorial
        self.elapsed_time = 0  # Reset elapsed time
        self.pause_time = 0   # Reset pause time
        self.is_paused = False
        self.pause_start = 0

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
        """Create enemies only if not in tutorial."""
        # Skip enemy creation during tutorial
        if self.in_tutorial:
            return
            
        for _ in range(3):
            enemy = Enemy.create_random(self)
            self.enemies.add(enemy)
            self.allsprites.add(enemy)

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
        dialogue_box = pygame.Surface((600, 120))
        dialogue_box.fill(WHITE)
        dialogue_box_rect = dialogue_box.get_rect(center=(WIDTH/2, HEIGHT/2))

        # Use slightly smaller font for potentially long messages
        dialogue_font = pygame.font.Font('LEGEND OF ZAHIR/assets/fonts/nokiafc22.ttf', 20)
        text = dialogue_font.render(message, True, BLACK)
        text_rect = text.get_rect(center=(300, 60))  # Centered in the dialogue box

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
        Each minigame's result is properly handled and door state is managed appropriately.
        """
        try:
            # Store the current pause state and time
            was_paused = self.is_paused
            if was_paused:
                self.resume_timer()
            
            # Record minigame start time
            minigame_start_time = time.time()
            
            # Run the appropriate minigame
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
            
            # Handle minigame completion
            if result == "completed":
                # Only adjust main game state if it wasn't the boss battle
                if minigame_type != 'boss':
                    # Reset door and enemy state for the next main game sequence
                    self.door_visible = False
                    self.door_prompt_visible = False
                    self.door_sprite = None
                    self.enemies_defeated = False
                else:
                    # For boss battle completion, keep the completed state
                    self.enemies_defeated = True
                    
                # Add minigame duration to elapsed time
                minigame_duration = time.time() - minigame_start_time
                self.game_start_time -= minigame_duration

                # Show appropriate completion message
                if minigame_type == 'boss':
                    self.show_message("Boss defeated! Victory!", 2.0)
                else:
                    self.show_message(f"{minigame_type.title()} challenge completed!", 2.0)
                    
            elif result == "died" or result == "failed":
                # Handle minigame failure
                if minigame_type == 'boss':
                    self.show_message("Defeated by the boss...", 2.0)
                else:
                    self.show_message(f"{minigame_type.title()} challenge failed!", 2.0)
            
            # Restore pause state if it was paused before
            if was_paused:
                self.pause_timer()
            
            # Return the minigame result
            return result

        except Exception as e:
            print(f"Error in minigame sequence: {e}")
            return "quit"

    def run_main_game_sequence(self):
        """Run main game sequence with proper door reset."""
        try:
            # Reset game state including door
            self.new()
            
            while self.playing and self.running:
                self.events()
                if not self.paused:
                    result = self.update()
                    if result == "completed":
                        return "completed"
                self.draw()
                self.clock.tick(FPS)

                if self.player.health <= 0:
                    return "died"
            
            if self.enemies_defeated:
                return "completed"
            return "quit"
            
        except Exception as e:
            print(f"Error in main sequence: {e}")
            return "quit"

    def show_door(self):
        """Create and show the door sprite in center position."""
        if not self.door_visible and not self.enemies_defeated:
            # Create door sprite at center position
            self.door_sprite = Door(self, self.door_position[0], self.door_position[1])
            self.allsprites.add(self.door_sprite)
            self.door_visible = True
            self.door_prompt_visible = False
            self.enemies_defeated = True
            
            # Ensure no collision blocks where door spawns
            for block in self.blocks:
                if (block.rect.x // TILESIZE == self.door_position[0] and 
                    block.rect.y // TILESIZE in [self.door_position[1], self.door_position[1] - 1]):
                    block.kill()
            
            self.show_message("A door has appeared!", 2.0)
            sound_manager.play_sound('door_appear')

    def check_door_interaction(self):
        """Simplified door interaction check."""
        if self.door_visible and self.door_sprite:
            player_pos = pygame.math.Vector2(self.player.rect.center)
            door_pos = pygame.math.Vector2(self.door_sprite.rect.center)
            distance = player_pos.distance_to(door_pos)
            
            if distance < 100:
                self.door_prompt_visible = True
                keys = pygame.key.get_pressed()
                if keys[pygame.K_e]:
                    return True
            else:
                self.door_prompt_visible = False
        return False

    def show_door_prompt(self):
        """Display prompt to enter door."""
        if self.door_prompt_visible:
            prompt_text = self.font.render("Press E to enter door", True, WHITE)
            prompt_rect = prompt_text.get_rect(center=(WIDTH/2, HEIGHT - 50))
            self.screen.blit(prompt_text, prompt_rect)

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
        """Display a prompt asking if the player wants to restart the level after dying."""
        prompt_box = pygame.Surface((400, 150))
        prompt_box.fill(WHITE)
        prompt_box_rect = prompt_box.get_rect(center=(WIDTH/2, HEIGHT/2))

        button_font = pygame.font.Font('LEGEND OF ZAHIR/assets/fonts/nokiafc22.ttf', 20)
        text = self.font.render("You died! Restart level?", True, BLACK)
        text_rect = text.get_rect(center=(200, 50))
        prompt_box.blit(text, text_rect)

        yes_button = pygame.Rect(50, 100, 100, 40)
        no_button = pygame.Rect(250, 100, 100, 40)

        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return False
                if event.type == pygame.MOUSEBUTTONDOWN:
                    mouse_pos = pygame.mouse.get_pos()
                    adjusted_pos = (mouse_pos[0] - prompt_box_rect.x, mouse_pos[1] - prompt_box_rect.y)
                    if yes_button.collidepoint(adjusted_pos):
                        sound_manager.play_sound('button_click')
                        return True
                    elif no_button.collidepoint(adjusted_pos):
                        sound_manager.play_sound('button_click')
                        return False

            # Draw buttons
            pygame.draw.rect(prompt_box, GREEN, yes_button)
            pygame.draw.rect(prompt_box, RED, no_button)

            yes_text = button_font.render("Yes", True, BLACK)
            no_text = button_font.render("No", True, BLACK)

            prompt_box.blit(yes_text, (85, 110))
            prompt_box.blit(no_text, (285, 110))

            self.screen.blit(prompt_box, prompt_box_rect)
            pygame.display.update()
            self.clock.tick(FPS)

    def show_final_results(self, victory=False):
        """
        Display the final results screen showing total cumulative time and score.
        Modified to properly handle victory condition.
        """
        final_time = int(self.get_elapsed_time())
        
        # Calculate time string for display
        if final_time < 3600:  # Less than an hour
            time_str = f"{final_time // 60:02d}:{final_time % 60:02d}"
        else:  # More than an hour
            hours = final_time // 3600
            minutes = (final_time % 3600) // 60
            seconds = final_time % 60
            time_str = f"{hours:02d}:{minutes:02d}:{seconds:02d}"
        
        # Check victory condition
        game_completed = victory and self.current_sequence_index >= len(self.game_sequence) - 1
        
        if game_completed:
            # Add to leaderboard if game was won
            rank = self.leaderboard_system.get_rank(final_time)
            if rank is not None:
                show_new_highscore(self.screen, self.font, rank, final_time)
                self.leaderboard_system.add_score(self.player_name, final_time)
        
        # Show completion or game over text
        if victory:
            text = self.font.render('Congratulations! Game Complete!', True, (255, 215, 0))  # Golden color
        else:
            text = self.font.render('Game Over', True, RED)
        text_rect = text.get_rect(center=(WIDTH/2, HEIGHT/2 - 50))
        
        # Show time text
        time_text = self.font.render(f'Total Time: {time_str}', True, WHITE)
        time_rect = time_text.get_rect(center=(WIDTH/2, HEIGHT/2))
        
        show_leaderboard = True
        while show_leaderboard and self.running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                    return
                if event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN:
                    show_leaderboard = False
            
            self.screen.fill(BLACK)
            self.screen.blit(text, text_rect)
            self.screen.blit(time_text, time_rect)
            
            if game_completed:
                # Show leaderboard for completed game
                draw_leaderboard(self.screen, self.font, self.leaderboard_system)
            else:
                # Show appropriate message based on victory state
                if victory:
                    msg = self.font.render('Game completed! Press ENTER to continue', True, GREEN)
                else:
                    msg = self.font.render('Game over! Press ENTER to continue', True, RED)
                msg_rect = msg.get_rect(center=(WIDTH/2, HEIGHT/2 + 50))
                self.screen.blit(msg, msg_rect)
            
            pygame.display.update()
            self.clock.tick(FPS)

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
        font = pygame.font.Font('LEGEND OF ZAHIR/assets/fonts/nokiafc22.ttf', 28)
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
if __name__ == "__main__":
    g = Game()  # Create a new Game instance
    g.start_game_sequence()  # Start the complete game sequence
    g.game_loop()  # Start the main game loop if a new game was started
    pygame.quit()  # Quit pygame
    sys.exit()  # Exit the program