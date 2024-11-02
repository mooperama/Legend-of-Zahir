import pygame
import os
import pickle
from datetime import datetime

# UI Constants
GRAY = (128, 128, 128)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GREEN = (0, 255, 0)
RED = (255, 0, 0)

class GameState:
    """Class to hold all saveable game state data."""
    def __init__(self, game):
        self.player_name = game.player_name
        self.current_sequence_index = game.current_sequence_index
        self.elapsed_time = game.elapsed_time
        self.in_tutorial = game.in_tutorial
        self.tutorial_completed = game.tutorial_system.tutorial_completed
        
        # Player stats
        if hasattr(game, 'player'):
            self.player_stats = {
                'health': game.player.health,
                'max_health': game.player.max_health,
                'experience': game.player.experience,
                'level': game.player.level,
                'position': (game.player.rect.x, game.player.rect.y)
            }
        else:
            self.player_stats = None
        
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
            game_state = GameState(game)
            
            if save_name is None:
                save_name = f"{game.player_name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            
            save_path = self.get_save_path(save_name)
            with open(save_path, 'wb') as f:
                pickle.dump(game_state, f)
            return True
        except Exception as e:
            print(f"Error saving game: {e}")
            return False
    
    def load_game(self, save_name, game):
        """Load a saved game state."""
        try:
            save_path = self.get_save_path(save_name)
            
            if not os.path.exists(save_path):
                return False
            
            with open(save_path, 'rb') as f:
                game_state = pickle.load(f)
            
            self._apply_game_state(game_state, game)
            return True
        except Exception as e:
            print(f"Error loading game: {e}")
            return False
    
    def _apply_game_state(self, game_state, game):
        """Apply loaded game state to current game instance."""
        game.player_name = game_state.player_name
        game.current_sequence_index = game_state.current_sequence_index
        game.elapsed_time = game_state.elapsed_time
        game.in_tutorial = game_state.in_tutorial
        game.tutorial_system.tutorial_completed = game_state.tutorial_completed
        
        if game_state.player_stats and hasattr(game, 'player'):
            game.player.health = game_state.player_stats['health']
            game.player.max_health = game_state.player_stats['max_health']
            game.player.experience = game_state.player_stats['experience']
            game.player.level = game_state.player_stats['level']
            game.player.rect.x = game_state.player_stats['position'][0]
            game.player.rect.y = game_state.player_stats['position'][1]
    
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
                        saves.append({
                            'name': filename[:-4],
                            'date': game_state.save_date,
                            'player': game_state.player_name
                        })
                    except:
                        continue
        except Exception as e:
            print(f"Error listing saves: {e}")
        return saves

    def delete_save(self, save_name):
        """Delete a save file."""
        try:
            save_path = self.get_save_path(save_name)
            if os.path.exists(save_path):
                os.remove(save_path)
                return True
            return False
        except Exception as e:
            print(f"Error deleting save: {e}")
            return False

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
        # Store the current game screen if not stored
        if self.original_screen is None:
            self.original_screen = self.game.screen.copy()
        
        # Reset the screen to the original game state
        self.game.screen.blit(self.original_screen, (0, 0))
        
        # Draw semi-transparent background
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
        
        # Update display
        pygame.display.flip()
    
    def draw_main_menu(self):
        """Draw main menu options."""
        options = ['Save Game', 'Load Game', 'Back']
        self.draw_menu_options(options, 150, 50)
    
    def draw_save_menu(self):
        """Draw save game interface."""
        saves = self.save_system.list_saves()
        options = ['New Save'] + [f"{save['name']} ({save['date']})" for save in saves] + ['Back']
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
            options = [f"{save['name']} ({save['date']})" for save in saves] + ['Back']
            self.draw_menu_options(options, 150, 40)
    
    def draw_menu_options(self, options, start_y, spacing):
        """Draw menu options with proper spacing and highlighting."""
        menu_width = self.screen_width * 0.8  # 80% of screen width
        menu_x = self.screen_width * 0.1  # 10% margin on each side
        
        for i, option in enumerate(options):
            y_pos = start_y + i * spacing
            
            # Draw selection highlight
            if i == self.selected_index:
                highlight_rect = pygame.Rect(
                    menu_x - 10,
                    y_pos - 17,
                    menu_width + 20,
                    40
                )
                pygame.draw.rect(self.game.screen, (50, 50, 50), highlight_rect)
            
            # Draw option text
            color = WHITE if i == self.selected_index else GRAY
            text = self.font.render(option, True, color)
            rect = text.get_rect(center=(self.screen_width/2, y_pos))
            self.game.screen.blit(text, rect)
    
    def draw_controls_help(self):
        """Draw control instructions at the bottom of the screen."""
        help_text = "↑/↓: Navigate   Enter: Select   Esc: Back"
        text = self.font.render(help_text, True, GRAY)
        rect = text.get_rect(center=(self.screen_width/2, self.screen_height - 30))
        self.game.screen.blit(text, rect)
    
    def handle_input(self, event):
        """Handle menu input with improved state management."""
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
        """Handle menu selection with improved state transitions."""
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