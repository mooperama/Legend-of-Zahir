import pygame
import sys
import os
import time

class ContinentGame:
    def __init__(self):
        pygame.init()
        self.width = 800
        self.height = 600
        self.screen = pygame.display.set_mode((self.width, self.height))
        pygame.display.set_caption("Label the Continents!")

        # Colors
        self.WHITE = (255, 255, 255)
        self.BLACK = (0, 0, 0)
        self.RED = (255, 0, 0)
        self.GREEN = (0, 255, 0)
        self.BLUE = (0, 0, 255)

        # Load and scale map
        self.map_img = pygame.image.load ('LEGEND OF ZAHIR/world_map_blank.png')
        self.map_img = pygame.transform.scale(self.map_img, (600, 400))
        self.map_rect = self.map_img.get_rect(center=(self.width//2, self.height//2))

        # Define continent areas (x, y, width, height)
        self.continent_areas = {
            'North America': pygame.Rect(200, 150, 120, 100),
            'South America': pygame.Rect(250, 280, 80, 100),
            'Europe': pygame.Rect(380, 150, 60, 60),
            'Africa': pygame.Rect(380, 240, 80, 100),
            'Asia': pygame.Rect(460, 150, 120, 100),
            'Australia': pygame.Rect(600, 350, 60, 60),
            'Antarctica': pygame.Rect(320, 480, 160, 30)
        }

        # Continents data
        self.continents = [
            {'name': 'North America', 'pos': (100, 530), 
            'hint': 'Contains Canada and USA'},
            {'name': 'South America', 'pos': (220, 530),
            'hint': 'Home to the Amazon Rainforest'},
            {'name': 'Europe', 'pos': (340, 530),
            'hint': 'Contains France and Germany'},
            {'name': 'Africa', 'pos': (460, 530),
            'hint': 'Largest hot desert in the world'},
            {'name': 'Asia', 'pos': (580, 530),
            'hint': 'Largest continent'},
            {'name': 'Australia', 'pos': (700, 530),
            'hint': 'Smallest continent'},
            {'name': 'Antarctica', 'pos': (400, 560),
            'hint': 'Coldest continent'}
        ]

        self.font = pygame.font.Font(None, 24)
        self.dragging = None
        self.completed = [False] * len(self.continents)
        self.score = 0
        self.show_hint = None
        self.start_time = time.time()
        self.game_time = 0
        
        # Debug mode flag
        self.debug_mode = False

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
                    hint_rect = hint_text.get_rect(center=(self.width//2, self.height - 50))
                    pygame.draw.rect(self.screen, self.WHITE, hint_rect.inflate(10, 5))
                    self.screen.blit(hint_text, hint_rect)

    def check_position(self, continent_idx):
        continent = self.continents[continent_idx]
        name = continent['name']
        pos = continent['pos']
        
        # Create a point rect for collision detection
        point_rect = pygame.Rect(pos[0] - 5, pos[1] - 5, 10, 10)
        
        # Check if the point is within the correct continent area
        if self.continent_areas[name].colliderect(point_rect):
            self.completed[continent_idx] = True
            self.score += 1
            # Center the label in the continent area
            area = self.continent_areas[name]
            self.continents[continent_idx]['pos'] = (area.centerx, area.centery)
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
                    running = False

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
                        self.dragging = None
                        self.show_hint = None

                elif event.type == pygame.MOUSEMOTION:
                    if self.dragging is not None:
                        self.continents[self.dragging]['pos'] = event.pos

                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_r:  # Reset game
                        self.__init__()
                    elif event.key == pygame.K_d:  # Toggle debug mode
                        self.debug_mode = not self.debug_mode

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

            if self.score == len(self.continents):
                win_text = self.font.render(f'Congratulations! Completed in {self.game_time} seconds!', True, self.GREEN)
                win_rect = win_text.get_rect(center=(self.width//2, 50))
                pygame.draw.rect(self.screen, self.BLACK, win_rect.inflate(20, 10))
                self.screen.blit(win_text, win_rect)

            pygame.display.flip()

        pygame.quit()
        sys.exit()

if __name__ == '__main__':
    game = ContinentGame()
    game.run()