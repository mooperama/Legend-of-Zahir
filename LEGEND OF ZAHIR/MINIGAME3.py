import pygame
import sys
import os
import time
from config_settings import *

class ContinentGame:
    def __init__(self, screen, clock):
        self.screen = screen
        self.clock = clock
        self.width = WIDTH
        self.height = HEIGHT

        # Colors
        self.WHITE = WHITE
        self.BLACK = BLACK
        self.RED = RED
        self.GREEN = GREEN
        self.BLUE = BLUE

        # Load and scale map
        self.map_img = pygame.image.load('LEGEND OF ZAHIR/world_map_blank.png')
        self.map_img = pygame.transform.scale(self.map_img, (600, 400))
        self.map_rect = self.map_img.get_rect(center=(self.width//2, self.height//2))

        # Adjust the continent areas to be relative to the map position
        map_x = self.map_rect.x
        map_y = self.map_rect.y
        
        # Define continent areas relative to the map position
        self.continent_areas = {
            'North America': pygame.Rect(map_x + 50, map_y + 50, 200, 120),
            'South America': pygame.Rect(map_x + 150, map_y + 200, 100, 150),
            'Europe': pygame.Rect(map_x + 280, map_y + 65, 110, 100),
            'Africa': pygame.Rect(map_x + 260, map_y + 170, 100, 140),
            'Asia': pygame.Rect(map_x + 395, map_y + 60, 200, 180),
            'Australia': pygame.Rect(map_x + 460, map_y + 250, 110, 80),  
            'Antarctica': pygame.Rect(map_x + 130, map_y + 350, 350, 80)
        }

        # Continents data
        self.continents = [
            {'name': 'North America', 'pos': (90, 530), 
            'hint': 'Contains Canada and USA'},
            {'name': 'South America', 'pos': (240, 530),
            'hint': 'Home to the Amazon Rainforest'},
            {'name': 'Europe', 'pos': (355, 530),
            'hint': 'Contains France and Germany'},
            {'name': 'Africa', 'pos': (430, 530),
            'hint': 'Largest hot desert in the world'},
            {'name': 'Asia', 'pos': (490, 530),
            'hint': 'Largest continent'},
            {'name': 'Australia', 'pos': (565, 530),
            'hint': 'Smallest continent'},
            {'name': 'Antarctica', 'pos': (670, 530),
            'hint': 'Coldest continent'}
        ]

        self.font = pygame.font.Font('LEGEND OF ZAHIR/assets/fonts/nokiafc22.ttf', 15)
        self.dragging = None
        self.completed = [False] * len(self.continents)
        self.score = 0
        self.show_hint = None
        self.start_time = time.time()
        self.game_time = 0
        self.debug_mode = False
        self.game_complete = False
        self.completion_time = 0

    def show_completion_screen(self):
        overlay = pygame.Surface((self.width, self.height))
        overlay.fill(self.BLACK)
        overlay.set_alpha(200)
        self.screen.blit(overlay, (0, 0))

        # Draw congratulations text
        congrats_font = pygame.font.Font('LEGEND OF ZAHIR/assets/fonts/nokiafc22.ttf', 30)
        texts = [
            f"Congratulations!",
            f"You've mastered all continents!",
            f"Time: {self.completion_time} seconds",
            "Press ENTER to continue"
        ]

        y_offset = self.height//2 - (len(texts) * 40)
        for i, text in enumerate(texts):
            if i == 0:  # Main congratulations text
                text_surface = congrats_font.render(text, True, self.GREEN)
            else:  # Other text
                text_surface = self.font.render(text, True, self.WHITE)
            text_rect = text_surface.get_rect(center=(self.width//2, y_offset + i * 40))
            self.screen.blit(text_surface, text_rect)

        pygame.display.flip()
        
        # Wait for ENTER key
        waiting = True
        while waiting:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return "quit"
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_RETURN:
                        waiting = False
                        if self.score >= len(self.continents):  # All continents placed correctly
                            return "completed"
                        else:
                            return "failed"
        return "completed" if self.score >= len(self.continents) else "failed"

    def draw_labels(self):
        # Draw continent areas in debug mode
        if self.debug_mode:
            for name, area in self.continent_areas.items():
                pygame.draw.rect(self.screen, (255, 0, 0, 128), area, 1)

        for i, continent in enumerate(self.continents):
            if not self.completed[i]:
                text = self.font.render(continent['name'], True, self.BLACK)
                text_rect = text.get_rect(center=continent['pos'])
                pygame.draw.rect(self.screen, self.WHITE, text_rect.inflate(10, 10))
                pygame.draw.rect(self.screen, self.BLACK, text_rect.inflate(10, 10), 1)
                self.screen.blit(text, text_rect)

                if self.show_hint == i:
                    hint_text = self.font.render(continent['hint'], True, self.BLUE)
                    hint_rect = hint_text.get_rect(center=(self.width//2, self.height - 40))
                    pygame.draw.rect(self.screen, self.WHITE, hint_rect.inflate(10, 5))
                    self.screen.blit(hint_text, hint_rect)

    def check_position(self, continent_idx):
        continent = self.continents[continent_idx]
        name = continent['name']
        mouse_pos = pygame.mouse.get_pos()
        
        # Check if the mouse position is within the continent's area
        if self.continent_areas[name].collidepoint(mouse_pos):
            self.completed[continent_idx] = True
            self.score += 1
            # Set the continent label to the center of its area
            area = self.continent_areas[name]
            self.continents[continent_idx]['pos'] = (area.centerx, area.centery)
            if self.score == len(self.continents):
                self.completion_time = self.game_time
                self.game_complete = True
            return True
        return False

    def draw_correct_feedback(self):
        feedback_text = self.font.render('Correct!', True, self.GREEN)
        feedback_rect = feedback_text.get_rect(center=(self.width//2, 30))
        pygame.draw.rect(self.screen, self.BLACK, feedback_rect.inflate(20, 10))
        self.screen.blit(feedback_text, feedback_rect)
        pygame.display.flip()
        pygame.time.wait(500)

    def run(self):
        running = True
        while running:
            current_time = time.time()
            self.game_time = int(current_time - self.start_time)

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return "quit"
                    
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_r:  # Reset game
                        self.__init__(self.screen, self.clock)
                    elif event.key == pygame.K_d:  # Toggle debug mode
                        self.debug_mode = not self.debug_mode

                elif event.type == pygame.MOUSEBUTTONDOWN:
                    for i, continent in enumerate(self.continents):
                        if not self.completed[i]:
                            text_rect = self.font.render(continent['name'], True, self.BLACK).get_rect(center=continent['pos'])
                            if text_rect.collidepoint(event.pos):
                                self.dragging = i
                                self.show_hint = i

                elif event.type == pygame.MOUSEBUTTONUP:
                    if self.dragging is not None:
                        if self.check_position(self.dragging):
                            self.draw_correct_feedback()
                            if self.game_complete:
                                return self.show_completion_screen()
                        self.dragging = None
                        self.show_hint = None

                elif event.type == pygame.MOUSEMOTION:
                    if self.dragging is not None:
                        self.continents[self.dragging]['pos'] = event.pos

            # Drawing
            self.screen.fill(self.BLACK)
            self.screen.blit(self.map_img, self.map_rect)
            self.draw_labels()

            # Draw score and time
            score_text = self.font.render(f'Score: {self.score}/{len(self.continents)}', True, self.WHITE)
            time_text = self.font.render(f'Time: {self.game_time}s', True, self.WHITE)
            self.screen.blit(score_text, (10, 10))
            self.screen.blit(time_text, (10, 40))

            # Draw instructions
            reset_text = self.font.render('Press R to reset | D for debug mode', True, self.WHITE)
            self.screen.blit(reset_text, (10, 70))

            pygame.display.flip()
            self.clock.tick(FPS)

        return "quit"

def run_continent_game(screen, clock):
    """
    Wrapper function to run the continent game
    Returns "completed", "quit"
    """
    game = ContinentGame(screen, clock)
    return game.run()

if __name__ == '_main_':
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    clock = pygame.time.Clock()
    result = run_continent_game(screen, clock)
    pygame.quit()
    sys.exit()