import pygame
from MINIGAME3 import FruitCatcher

class MainGame:
    """
    MainGame class represents the primary game structure,
    integrating both the main game and a mini-game (Fruit Catcher).
    """

    def __init__(self):
        """
        Initialize the MainGame object.
        Sets up the Pygame window, clock, and game states.
        """
        pygame.init()
        self.screen = pygame.display.set_mode((800, 600))
        pygame.display.set_caption("Main Game with Mini-Game")
        self.clock = pygame.time.Clock()
        self.fruit_catcher = FruitCatcher(800, 600)
        self.game_state = "main_menu"  # Can be "main_menu", "main_game", "mini_game"

    def run(self):
        """
        Main game loop.
        Handles events, updates game state, and renders the appropriate screen.
        """
        running = True
        while running:
            events = pygame.event.get()
            for event in events:
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN:
                    self.handle_keydown(event)

            self.update_current_state(events)
            self.render_current_state()

            pygame.display.flip()
            self.clock.tick(60)

        pygame.quit()

    def handle_keydown(self, event):
        """
        Handle keyboard input events.
        
        Args:
            event (pygame.event.Event): The keyboard event to handle.
        """
        if event.key == pygame.K_m:
            self.game_state = "mini_game"
            self.fruit_catcher.reset()
        elif event.key == pygame.K_ESCAPE:
            self.game_state = "main_menu"

    def update_current_state(self, events):
        """
        Update the current game state.
        
        Args:
            events (list): List of pygame events to process.
        """
        if self.game_state == "main_game":
            self.update_main_game()
        elif self.game_state == "mini_game":
            self.fruit_catcher.update(events)
            if self.fruit_catcher.game_over:
                self.game_state = "main_game"

    def render_current_state(self):
        """
        Render the current game state to the screen.
        """
        if self.game_state == "main_menu":
            self.draw_main_menu()
        elif self.game_state == "main_game":
            self.draw_main_game()
        elif self.game_state == "mini_game":
            self.fruit_catcher.draw(self.screen)

    def draw_main_menu(self):
        """
        Draw the main menu screen.
        """
        self.screen.fill((0, 0, 0))  # Black background
        font = pygame.font.Font(None, 36)
        title = font.render("Main Game", True, (255, 255, 255))
        instructions = font.render("Press SPACE to start, M for mini-game", True, (255, 255, 255))
        self.screen.blit(title, (400 - title.get_width() // 2, 200))
        self.screen.blit(instructions, (400 - instructions.get_width() // 2, 300))

    def update_main_game(self):
        """
        Update the main game logic.
        """
        # Add your main game update logic here
        pass

    def draw_main_game(self):
        """
        Draw the main game screen.
        """
        self.screen.fill((0, 100, 0))  # Green background for main game
        font = pygame.font.Font(None, 36)
        text = font.render("Main Game Running", True, (255, 255, 255))
        self.screen.blit(text, (400 - text.get_width() // 2, 300))

if __name__ == "__main__":
    game = MainGame()
    game.run()