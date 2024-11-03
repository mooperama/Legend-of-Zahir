import pygame
import os
import pickle
from datetime import datetime
import time

# UI Constants
GRAY = (128, 128, 128)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GREEN = (0, 255, 0)
RED = (255, 0, 0)
YELLOW = (255, 255, 0)

class GameState:
    """Class to hold all saveable game state data."""
    def __init__(self, game):
        # Basic game state - Add version tracking
        self.save_version = "1.0"  # Add version tracking to handle backwards compatibility
        self.player_name = game.player_name
        self.current_sequence_index = game.current_sequence_index
        self.elapsed_time = game.elapsed_time
        self.in_tutorial = game.in_tutorial
        self.tutorial_completed = game.tutorial_system.tutorial_completed if hasattr(game.tutorial_system, 'tutorial_completed') else False
        self.start_time = game.game_start_time
        self.pause_time = game.pause_time
        self.is_paused = game.is_paused
        
        # Player stats - Add error handling
        if hasattr(game, 'player'):
            try:
                self.player_stats = {
                    'health': getattr(game.player, 'health', 100),
                    'max_health': getattr(game.player, 'max_health', 100),
                    'experience': getattr(game.player, 'experience', 0),
                    'level': getattr(game.player, 'level', 1),
                    'position': (game.player.rect.x, game.player.rect.y) if hasattr(game.player, 'rect') else (0, 0)
                }
            except AttributeError:
                self.player_stats = None
        else:
            self.player_stats = None
        
        # Game progress state
        self.running = getattr(game, 'running', True)
        self.playing = getattr(game, 'playing', True)
        
        # Save timestamp
        self.save_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

class SaveSystem:
    """Handles saving and loading game states."""
    def __init__(self):
        self.save_directory = "saves"
        self.ensure_save_directory()
    
    def ensure_save_directory(self):
        """Create saves directory if it doesn't exist."""
        if not os.path.exists(self.save_directory):
            os.makedirs(self.save_directory)
    
    def get_save_path(self, save_name):
        """Get the full path for a save file."""
        return os.path.join(self.save_directory, f"{save_name}.sav")
    
    def save_game(self, game, save_name=None):
        """Save the current game state."""
        try:
            # Create game state
            game_state = GameState(game)
            
            # Generate save name if none provided
            if save_name is None:
                save_name = f"{game.player_name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            
            # Save to file
            save_path = self.get_save_path(save_name)
            with open(save_path, 'wb') as f:
                pickle.dump(game_state, f)
            
            return True, "Game saved successfully!"
            
        except Exception as e:
            print(f"Error saving game: {e}")
            return False, f"Could not save game: {str(e)}"

    def load_game(self, save_name, game):
        """Load a saved game state with improved error handling and backwards compatibility."""
        try:
            save_path = self.get_save_path(save_name)
            
            if not os.path.exists(save_path):
                return False, "Save file not found", None
            
            with open(save_path, 'rb') as f:
                try:
                    game_state = pickle.load(f)
                    
                    # Check if it's an old save format
                    if not hasattr(game_state, 'save_version'):
                        # Convert old save format to new format
                        game_state = self._convert_old_save_format(game_state)
                    
                    # Create timer data before applying state
                    timer_data = {
                        'elapsed_time': getattr(game_state, 'elapsed_time', 0),
                        'start_time': getattr(game_state, 'start_time', time.time()),
                        'pause_time': getattr(game_state, 'pause_time', 0)
                    }
                    
                    # Apply the game state with error handling
                    self._apply_game_state(game_state, game)
                    
                    return True, "Game loaded successfully!", timer_data
                    
                except (AttributeError, pickle.UnpicklingError) as e:
                    print(f"Error unpickling save file: {e}")
                    return False, "Save file is corrupted or incompatible", None
                
        except Exception as e:
            print(f"Error loading game: {e}")
            return False, f"Could not load save file: {str(e)}", None

    def list_saves(self):
        """Get list of available save files."""
        saves = []
        try:
            for filename in os.listdir(self.save_directory):
                if filename.endswith('.sav'):
                    save_path = os.path.join(self.save_directory, filename)
                    try:
                        with open(save_path, 'rb') as f:
                            game_state = pickle.load(f)
                            # Handle old save formats that might not have all attributes
                            saves.append({
                                'name': filename[:-4],  # Remove .sav extension
                                'date': getattr(game_state, 'save_date', 'Unknown Date'),
                                'player': getattr(game_state, 'player_name', 'Unknown Player'),
                                'sequence': getattr(game_state, 'current_sequence_index', 0)
                            })
                    except Exception as e:
                        print(f"Error reading save {filename}: {e}")
                        # Add the save with default values if it can't be read
                        saves.append({
                            'name': filename[:-4],
                            'date': 'Error Reading Save',
                            'player': 'Unknown',
                            'sequence': 0
                        })
        except Exception as e:
            print(f"Error listing saves: {e}")
        return sorted(saves, key=lambda x: x['date'], reverse=True)

    def delete_save(self, save_name):
        """Delete a save file."""
        try:
            save_path = self.get_save_path(save_name)
            if os.path.exists(save_path):
                os.remove(save_path)
                return True, "Save file deleted successfully!"
            return False, "Save file not found"
        except Exception as e:
            print(f"Error deleting save: {e}")
            return False, f"Error deleting save: {str(e)}"

    def _convert_old_save_format(self, old_state):
        """Convert old save format to new format."""
        new_state = GameState.__new__(GameState)  # Create new state without calling __init__
        new_state.save_version = "1.0"
        
        # Copy all existing attributes
        for attr in dir(old_state):
            if not attr.startswith('__'):
                setattr(new_state, attr, getattr(old_state, attr))
        
        # Set default values for new attributes
        if not hasattr(new_state, 'tutorial_completed'):
            new_state.tutorial_completed = False
        if not hasattr(new_state, 'pause_time'):
            new_state.pause_time = 0
        if not hasattr(new_state, 'is_paused'):
            new_state.is_paused = False
            
        return new_state

    def _apply_game_state(self, game_state, game):
        """Apply loaded game state to current game instance with error handling."""
        try:
            # Apply basic game state with safe attribute setting
            game.player_name = getattr(game_state, 'player_name', game.player_name)
            game.current_sequence_index = getattr(game_state, 'current_sequence_index', 0)
            game.elapsed_time = getattr(game_state, 'elapsed_time', 0)
            game.in_tutorial = getattr(game_state, 'in_tutorial', True)
            
            if hasattr(game, 'tutorial_system'):
                game.tutorial_system.tutorial_completed = getattr(game_state, 'tutorial_completed', False)
                
            game.game_start_time = getattr(game_state, 'start_time', time.time())
            game.pause_time = getattr(game_state, 'pause_time', 0)
            game.is_paused = getattr(game_state, 'is_paused', False)
            
            # Apply player stats if they exist
            if game_state.player_stats and hasattr(game, 'player'):
                stats = game_state.player_stats
                game.player.health = stats.get('health', game.player.health)
                game.player.max_health = stats.get('max_health', game.player.max_health)
                game.player.experience = stats.get('experience', game.player.experience)
                game.player.level = stats.get('level', game.player.level)
                if 'position' in stats:
                    game.player.rect.x = stats['position'][0]
                    game.player.rect.y = stats['position'][1]
            
            # Apply game progress state
            game.running = getattr(game_state, 'running', True)
            game.playing = getattr(game_state, 'playing', True)
            
        except Exception as e:
            print(f"Error applying game state: {e}")
            raise

class SaveLoadMenu:
    """UI for saving and loading games."""
    def __init__(self, game):
        self.game = game
        self.save_system = game.save_system
        self.font = pygame.font.Font(None, 32)
        self.selected_index = 0
        self.mode = 'main'
        self.screen_width = game.screen.get_width()
        self.screen_height = game.screen.get_height()
        
        # Create persistent background surface
        self.background = pygame.Surface((self.screen_width, self.screen_height))
        self.background.fill(BLACK)
        self.background.set_alpha(128)
        
        # Store the original game screen
        self.original_screen = None
        
    def draw(self):
        """Draw the save/load menu."""
        if self.original_screen is None:
            self.original_screen = self.game.screen.copy()
        
        # Reset the screen to the original game state
        self.game.screen.blit(self.original_screen, (0, 0))
        self.game.screen.blit(self.background, (0, 0))
        
        # Title
        title = "Save/Load Game"
        title_surf = self.font.render(title, True, WHITE)
        title_rect = title_surf.get_rect(center=(self.screen_width/2, 50))
        self.game.screen.blit(title_surf, title_rect)
        
        # Draw current menu
        if self.mode == 'main':
            self.draw_main_menu()
        elif self.mode == 'save':
            self.draw_save_menu()
        elif self.mode == 'load':
            self.draw_load_menu()
            
        # Draw controls help
        self.draw_controls_help()
        pygame.display.flip()
    
    def draw_main_menu(self):
        """Draw main menu options."""
        options = ['Save Game', 'Load Game', 'Back']
        self.draw_menu_options(options, 150, 50)
    
    def draw_save_menu(self):
        """Draw save game interface."""
        saves = self.save_system.list_saves()
        options = ['New Save'] + [f"{save['name']} - Level {save['sequence']+1} ({save['date']})" 
                                for save in saves] + ['Back']
        self.draw_menu_options(options, 150, 40)
    
    def draw_load_menu(self):
        """Draw load game interface."""
        saves = self.save_system.list_saves()
        if not saves:
            text = self.font.render('No saves found', True, WHITE)
            rect = text.get_rect(center=(self.screen_width/2, 150))
            self.game.screen.blit(text, rect)
            self.draw_menu_options(['Back'], 200, 50)
        else:
            options = [f"{save['name']} - Level {save['sequence']+1} ({save['date']})" 
                      for save in saves] + ['Back']
            self.draw_menu_options(options, 150, 40)
    
    def draw_menu_options(self, options, start_y, spacing):
        """Draw menu options with proper spacing and highlighting."""
        menu_width = self.screen_width * 0.8
        menu_x = self.screen_width * 0.1
        
        for i, option in enumerate(options):
            y_pos = start_y + i * spacing
            
            if i == self.selected_index:
                highlight_rect = pygame.Rect(
                    menu_x - 10,
                    y_pos - 17,
                    menu_width + 20,
                    40
                )
                pygame.draw.rect(self.game.screen, (50, 50, 50), highlight_rect)
            
            color = WHITE if i == self.selected_index else GRAY
            text = self.font.render(option, True, color)
            rect = text.get_rect(center=(self.screen_width/2, y_pos))
            self.game.screen.blit(text, rect)
    
    def draw_controls_help(self):
        """Draw control instructions."""
        help_text = "↑/↓: Navigate   Enter: Select   Esc: Back"
        text = self.font.render(help_text, True, GRAY)
        rect = text.get_rect(center=(self.screen_width/2, self.screen_height - 30))
        self.game.screen.blit(text, rect)
    
    def handle_input(self, event):
        """Handle menu input."""
        if event.type != pygame.KEYDOWN:
            return None
            
        if event.key == pygame.K_ESCAPE:
            if self.mode == 'main':
                self.cleanup()
                return 'back'
            else:
                self.mode = 'main'
                self.selected_index = 0
                return None
                
        elif event.key in (pygame.K_UP, pygame.K_w):
            self.selected_index = max(0, self.selected_index - 1)
            
        elif event.key in (pygame.K_DOWN, pygame.K_s):
            max_index = self.get_max_index()
            self.selected_index = min(max_index, self.selected_index + 1)
            
        elif event.key == pygame.K_RETURN:
            action = self.handle_selection()
            if action in ('back', 'save', 'load'):
                self.cleanup()
            return action
            
        return None
    
    def cleanup(self):
        """Clean up resources when closing the menu."""
        self.original_screen = None
        self.selected_index = 0
        self.mode = 'main'
    
    def get_max_index(self):
        """Get the maximum selectable index for current mode."""
        if self.mode == 'main':
            return 2
        elif self.mode == 'save':
            return len(self.save_system.list_saves()) + 1
        elif self.mode == 'load':
            saves = self.save_system.list_saves()
            return len(saves) if saves else 0
        return 0
    
    def handle_selection(self):
        """Handle menu selection."""
        if self.mode == 'main':
            if self.selected_index == 0:
                self.mode = 'save'
                self.selected_index = 0
            elif self.selected_index == 1:
                self.mode = 'load'
                self.selected_index = 0
            else:
                return 'back'
        
        elif self.mode == 'save':
            saves = self.save_system.list_saves()
            if self.selected_index == 0:
                return 'save'
            elif self.selected_index <= len(saves):
                return 'save'
            else:
                self.mode = 'main'
                self.selected_index = 0
        
        elif self.mode == 'load':
            saves = self.save_system.list_saves()
            if saves and self.selected_index < len(saves):
                return 'load'
            else:
                self.mode = 'main'
                self.selected_index = 0
        
        return None
    
    def handle_save_action(self):
        """Handle save game action."""
        try:
            success, message = self.save_system.save_game(self.game)
            self.game.show_message(message, duration=1.5)
            return success
        except Exception as e:
            print(f"Error saving game: {e}")
            self.game.show_message("Error saving game!", duration=1.5)
            return False

    def handle_load_action(self):
        """Handle load game action."""
        try:
            saves = self.save_system.list_saves()
            if not saves or self.selected_index >= len(saves):
                self.game.show_message("No save file selected", duration=1.5)
                return False

            success, message, timer_data = self.save_system.load_game(
                saves[self.selected_index]['name'], 
                self.game
            )
            
            if success and timer_data is not None:
                # Restore timer state
                self.game.elapsed_time = timer_data['elapsed_time']
                self.game.game_start_time = timer_data['start_time']
                self.game.pause_time = timer_data['pause_time']
                self.game.show_message("Game loaded successfully!", duration=1.5)
                return True
                
            self.game.show_message(message, duration=1.5)
            return False
            
        except Exception as e:
            print(f"Error loading game: {e}")
            self.game.show_message("Error loading game!", duration=1.5)
            return False
class QuickSaveLoad:
    """Handles quick save and load functionality."""
    def __init__(self, game):
        self.game = game
        self.save_system = game.save_system
        self.quick_save_name = None

    def quick_save(self):
        """Perform a quick save."""
        try:
            # Generate quick save name
            self.quick_save_name = f"quicksave_{self.game.player_name}"
            success, message = self.save_system.save_game(self.game, self.quick_save_name)
            self.game.show_message(message, duration=1.0)
            return success
        except Exception as e:
            print(f"Error in quick save: {e}")
            self.game.show_message("Quick save failed!", duration=1.0)
            return False

    def quick_load(self):
        """Load the most recent quick save."""
        try:
            if self.quick_save_name:
                success, message, timer_data = self.save_system.load_game(
                    self.quick_save_name,
                    self.game
                )
                if success and timer_data is not None:
                    # Restore timer state
                    self.game.elapsed_time = timer_data['elapsed_time']
                    self.game.game_start_time = timer_data['start_time']
                    self.game.pause_time = timer_data['pause_time']
                    self.game.show_message("Game loaded successfully!", duration=1.0)
                    return True
                else:
                    self.game.show_message("No quick save found!", duration=1.0)
            else:
                self.game.show_message("No quick save available!", duration=1.0)
            return False
        except Exception as e:
            print(f"Error in quick load: {e}")
            self.game.show_message("Quick load failed!", duration=1.0)
            return False