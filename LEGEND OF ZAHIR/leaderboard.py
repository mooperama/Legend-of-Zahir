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
    Draw the leaderboard on screen.
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
    
    # Draw entries
    y_spacing = 40
    start_y = 120
    
    headers = font.render("Rank  Name           Time     Date", True, WHITE)
    screen.blit(headers, (WIDTH/2 - 200, start_y - y_spacing))
    
    if not leaderboard_system.leaderboard:
        # Show message if no completed games yet
        no_scores = font.render("No completed games yet!", True, YELLOW)
        no_scores_rect = no_scores.get_rect(center=(WIDTH/2, start_y + y_spacing))
        screen.blit(no_scores, no_scores_rect)
    else:
        # Show completed game scores
        for i, entry in enumerate(leaderboard_system.leaderboard):
            # Format the entry text
            rank_text = f"{i+1:2d}"
            name_text = f"{entry['name']:<15}"
            time_text = f"{int(entry['time']):>4d}s"
            date_text = entry['date']
            
            entry_text = f"{rank_text}.  {name_text} {time_text}  {date_text}"
            entry_surface = font.render(entry_text, True, WHITE)
            screen.blit(entry_surface, (WIDTH/2 - 200, start_y + i * y_spacing))
    
    # Draw exit instruction
    exit_text = font.render('Press ENTER to continue', True, WHITE)
    exit_rect = exit_text.get_rect(center=(WIDTH/2, HEIGHT - 50))
    screen.blit(exit_text, exit_rect)


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