import json
import pygame
import os
from datetime import datetime
from config_settings import *

class LeaderboardSystem:
    """
    A system to manage game completion time leaderboards.
    Stores player names, completion times, and dates.
    """
    def __init__(self):
        self.leaderboard_file = "leaderboard.json"
        self.max_entries = 10  # Store top 10 scores
        self.leaderboard = self.load_leaderboard()

    def load_leaderboard(self):
        """
        Load the leaderboard from file. Create new if doesn't exist.
        
        Returns:
            list: List of leaderboard entries
        """
        try:
            if os.path.exists(self.leaderboard_file):
                with open(self.leaderboard_file, 'r') as f:
                    return json.load(f)
            return []
        except Exception as e:
            print(f"Error loading leaderboard: {e}")
            return []

    def save_leaderboard(self):
        """Save the current leaderboard to file."""
        try:
            with open(self.leaderboard_file, 'w') as f:
                json.dump(self.leaderboard, f, indent=2)
        except Exception as e:
            print(f"Error saving leaderboard: {e}")

    def add_score(self, player_name, completion_time):
        """
        Add a new score to the leaderboard.
        
        Args:
            player_name (str): Name of the player
            completion_time (float): Time taken to complete the game
        """
        entry = {
            'name': player_name,
            'time': completion_time,
            'date': datetime.now().strftime('%Y-%m-%d %H:%M')
        }
        
        # Add new entry and sort by completion time
        self.leaderboard.append(entry)
        self.leaderboard.sort(key=lambda x: x['time'])
        
        # Keep only top scores
        if len(self.leaderboard) > self.max_entries:
            self.leaderboard = self.leaderboard[:self.max_entries]
        
        self.save_leaderboard()

    def get_rank(self, completion_time):
        """
        Get the rank of a completion time in the current leaderboard.
        
        Args:
            completion_time (float): Time to check
            
        Returns:
            int: Rank of the time (1-based), or None if not in top 10
        """
        for i, entry in enumerate(self.leaderboard):
            if completion_time <= entry['time']:
                return i + 1
        if len(self.leaderboard) < self.max_entries:
            return len(self.leaderboard) + 1
        return None

def draw_leaderboard(screen, font, leaderboard_system):
    """
    Draw the leaderboard on screen with properly aligned columns.
    Only shows completed game scores.
    """
    # Create semi-transparent overlay
    overlay = pygame.Surface((WIDTH, HEIGHT))
    overlay.fill((0, 0, 0))
    overlay.set_alpha(200)
    screen.blit(overlay, (0, 0))
    
    # Draw title
    title = font.render('LEADERBOARD - COMPLETED GAMES', True, WHITE)
    title_rect = title.get_rect(center=(WIDTH/2, 50))
    screen.blit(title, title_rect)
    
    # Column settings
    col_widths = {
        'rank': 100,    # Width for rank column
        'name': 250,    # Width for name column
        'time': 150,    # Width for time column
        'date': 250    # Width for date column
    }
    
    total_width = sum(col_widths.values())
    start_x = (WIDTH - total_width) // 2
    y_spacing = 50  # Increased spacing
    start_y = 120
    
    # Draw column headers with background
    header_bg = pygame.Surface((total_width, y_spacing))
    header_bg.fill((40, 40, 40))
    screen.blit(header_bg, (start_x, start_y - y_spacing))
    
    headers = [
        ('RANK', col_widths['rank']),
        ('PLAYER NAME', col_widths['name']),
        ('TIME', col_widths['time']),
        ('DATE', col_widths['date'])
    ]
    
    current_x = start_x
    for header_text, width in headers:
        header = font.render(header_text, True, YELLOW)
        # Center text within column
        text_x = current_x + (width - header.get_width()) // 2
        screen.blit(header, (text_x, start_y - y_spacing))
        current_x += width
    
    # Draw separator line
    pygame.draw.line(screen, WHITE, 
                    (start_x, start_y - y_spacing/2 + y_spacing/2),
                    (start_x + total_width, start_y - y_spacing/2 + y_spacing/2), 2)
    
    if not leaderboard_system.leaderboard:
        # Show message if no completed games yet
        no_scores = font.render("No completed games yet!", True, YELLOW)
        no_scores_rect = no_scores.get_rect(center=(WIDTH/2, start_y + y_spacing))
        screen.blit(no_scores, no_scores_rect)
    else:
        # First draw all row backgrounds
        for i in range(len(leaderboard_system.leaderboard)):
            y = start_y + i * y_spacing
            if i % 2 == 0:
                row_bg = pygame.Surface((total_width, y_spacing))
                row_bg.fill((50, 50, 50))
                screen.blit(row_bg, (start_x, y))
        
        # Then draw the text
        for i, entry in enumerate(leaderboard_system.leaderboard):
            y = start_y + i * y_spacing + (y_spacing - font.get_height()) // 2  # Center text vertically
            
            # Rank - Left aligned with padding
            rank_text = font.render(f"#{i+1}", True, WHITE)
            screen.blit(rank_text, (start_x + 20, y))
            
            # Name - Left aligned with padding
            name_text = font.render(entry['name'], True, WHITE)
            screen.blit(name_text, (start_x + col_widths['rank'] + 20, y))
            
            # Time - Center aligned in column
            time_text = font.render(f"{int(entry['time'])}s", True, WHITE)
            time_x = start_x + col_widths['rank'] + col_widths['name'] + (col_widths['time'] - time_text.get_width()) // 2
            screen.blit(time_text, (time_x, y))
            
            # Date - Center aligned in column
            date_text = font.render(entry['date'], True, WHITE)
            date_x = start_x + col_widths['rank'] + col_widths['name'] + col_widths['time'] + (col_widths['date'] - date_text.get_width()) // 2
            screen.blit(date_text, (date_x, y))
    
    # Draw bottom separator line
    if leaderboard_system.leaderboard:
        end_y = start_y + len(leaderboard_system.leaderboard) * y_spacing
        pygame.draw.line(screen, WHITE, 
                        (start_x, end_y),
                        (start_x + total_width, end_y), 2)
    
    # Draw container box
    pygame.draw.rect(screen, WHITE, 
                    (start_x, start_y - y_spacing, 
                     total_width, y_spacing * (len(leaderboard_system.leaderboard) + 1)), 
                    2)
    
    # Draw exit instruction
    exit_text = font.render('Press ENTER to continue', True, WHITE)
    exit_rect = exit_text.get_rect(center=(WIDTH/2, HEIGHT - 50))
    screen.blit(exit_text, exit_rect)
    
    pygame.display.update()

def show_new_highscore(screen, font, rank, completion_time):
    """
    Show a congratulatory message for achieving a high score in a completed game.
    """
    overlay = pygame.Surface((WIDTH, HEIGHT))
    overlay.fill((0, 0, 0))
    overlay.set_alpha(200)
    screen.blit(overlay, (0, 0))
    
    congrats_text = font.render('NEW HIGH SCORE!', True, YELLOW)
    rank_text = font.render(f'Rank: #{rank}', True, WHITE)
    time_text = font.render(f'Time: {int(completion_time)}s', True, WHITE)
    completion_text = font.render('Game Completed!', True, GREEN)
    
    congrats_rect = congrats_text.get_rect(center=(WIDTH/2, HEIGHT/2 - 90))
    rank_rect = rank_text.get_rect(center=(WIDTH/2, HEIGHT/2 - 30))
    time_rect = time_text.get_rect(center=(WIDTH/2, HEIGHT/2 + 30))
    completion_rect = completion_text.get_rect(center=(WIDTH/2, HEIGHT/2 + 90))
    
    screen.blit(congrats_text, congrats_rect)
    screen.blit(rank_text, rank_rect)
    screen.blit(time_text, time_rect)
    screen.blit(completion_text, completion_rect)
    
    pygame.display.update()
    pygame.time.delay(3000)  # Show for 3 seconds