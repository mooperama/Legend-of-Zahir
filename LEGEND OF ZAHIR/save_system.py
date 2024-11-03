import pygame
import os
import json
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
        # Basic game state
        self.save_version = "1.0"
        self.player_name = game.player_name
        self.current_sequence_index = game.current_sequence_index
        self.elapsed_time = game.elapsed_time
        self.in_tutorial = game.in_tutorial
        self.tutorial_completed = game.tutorial_system.tutorial_completed if hasattr(game.tutorial_system, 'tutorial_completed') else False
        self.start_time = game.game_start_time
        self.pause_time = game.pause_time
        self.is_paused = game.is_paused
        
        # Player stats
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
    
    def to_dict(self):
        """Convert GameState to dictionary for JSON serialization."""
        return {
            'save_version': self.save_version,
            'player_name': self.player_name,
            'current_sequence_index': self.current_sequence_index,
            'elapsed_time': self.elapsed_time,
            'in_tutorial': self.in_tutorial,
            'tutorial_completed': self.tutorial_completed,
            'start_time': self.start_time,
            'pause_time': self.pause_time,
            'is_paused': self.is_paused,
            'player_stats': self.player_stats,
            'running': self.running,
            'playing': self.playing,
            'save_date': self.save_date
        }
    
    @classmethod
    def from_dict(cls, data):
        """Create GameState instance from dictionary."""
        state = cls.__new__(cls)
        for key, value in data.items():
            setattr(state, key, value)
        return state

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
        return os.path.join(self.save_directory, f"{save_name}.json")
    
    def save_game(self, game, save_name=None):
        """Save the current game state."""
        try:
            # Create game state
            game_state = GameState(game)
            
            # Generate save name if none provided
            if save_name is None:
                save_name = f"{game.player_name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            
            # Save to JSON file
            save_path = self.get_save_path(save_name)
            with open(save_path, 'w', encoding='utf-8') as f:
                json.dump(game_state.to_dict(), f, indent=4)
            
            return True, "Game saved successfully!"
            
        except Exception as e:
            print(f"Error saving game: {e}")
            return False, f"Could not save game: {str(e)}"

    def load_game(self, save_name, game):
        """Load a saved game state."""
        try:
            save_path = self.get_save_path(save_name)
            
            if not os.path.exists(save_path):
                return False, "Save file not found", None
            
            with open(save_path, 'r', encoding='utf-8') as f:
                try:
                    data = json.load(f)
                    game_state = GameState.from_dict(data)
                    
                    # Check version compatibility
                    if not hasattr(game_state, 'save_version'):
                        game_state = self._convert_old_save_format(game_state)
                    
                    # Create timer data
                    timer_data = {
                        'elapsed_time': game_state.elapsed_time,
                        'start_time': game_state.start_time,
                        'pause_time': game_state.pause_time
                    }
                    
                    # Apply the game state
                    self._apply_game_state(game_state, game)
                    
                    return True, "Game loaded successfully!", timer_data
                    
                except json.JSONDecodeError as e:
                    print(f"Error decoding save file: {e}")
                    return False, "Save file is corrupted", None
                
        except Exception as e:
            print(f"Error loading game: {e}")
            return False, f"Could not load save file: {str(e)}", None

    def list_saves(self):
        """Get list of available save files."""
        saves = []
        try:
            for filename in os.listdir(self.save_directory):
                if filename.endswith('.json'):
                    save_path = os.path.join(self.save_directory, filename)
                    try:
                        with open(save_path, 'r', encoding='utf-8') as f:
                            data = json.load(f)
                            saves.append({
                                'name': filename[:-5],  # Remove .json extension
                                'date': data.get('save_date', 'Unknown Date'),
                                'player': data.get('player_name', 'Unknown Player'),
                                'sequence': data.get('current_sequence_index', 0)
                            })
                    except Exception as e:
                        print(f"Error reading save {filename}: {e}")
                        saves.append({
                            'name': filename[:-5],
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
        new_state = GameState.__new__(GameState)
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
        """Apply loaded game state to current game instance."""
        try:
            # Apply basic game state
            game.player_name = game_state.player_name
            game.current_sequence_index = game_state.current_sequence_index
            game.elapsed_time = game_state.elapsed_time
            game.in_tutorial = game_state.in_tutorial
            
            if hasattr(game, 'tutorial_system'):
                game.tutorial_system.tutorial_completed = game_state.tutorial_completed
                
            game.game_start_time = game_state.start_time
            game.pause_time = game_state.pause_time
            game.is_paused = game_state.is_paused
            
            # Apply player stats if they exist
            if game_state.player_stats and hasattr(game, 'player'):
                stats = game_state.player_stats
                for key, value in stats.items():
                    if key != 'position':
                        setattr(game.player, key, value)
                if 'position' in stats and hasattr(game.player, 'rect'):
                    game.player.rect.x, game.player.rect.y = stats['position']
            
            # Update player name in the player object if it exists
            if hasattr(game, 'player'):
                game.player.name = game_state.player_name
            
            # Apply game progress state
            game.running = game_state.running
            game.playing = game_state.playing
            
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