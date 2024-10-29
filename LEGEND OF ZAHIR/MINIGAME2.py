import pygame
import random
from config_settings import *

def generate_expression():
    operators = ['+', '-', '*', '/']
    expression = []
    
    # Generate the first number
    expression.append(str(random.randint(1, 10)))
    
    for _ in range(3):
        operator = random.choice(operators)
        number = str(random.randint(1, 10))
        
        # Randomly add parentheses
        if random.random() < 0.3:  # 30% chance to add parentheses
            if len(expression) > 1:
                insert_pos = random.randint(0, len(expression) - 1)
                expression.insert(insert_pos, '(')
                expression.append(')')
        
        expression.append(operator)
        expression.append(number)
    
    return ' '.join(expression)

def evaluate_expression(expression):
    try:
        return eval(expression)
    except:
        return None

def run_pemdas_game(screen, clock):
    WIDTH, HEIGHT = screen.get_size()
    font = pygame.font.Font(None, 36)

    score = 0
    fails = 0
    current_expression = generate_expression()
    input_text = ""
    
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return "quit"
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    try:
                        user_answer = float(input_text)
                        correct_answer = evaluate_expression(current_expression)
                        if correct_answer is not None and abs(user_answer - correct_answer) < 0.001:
                            score += 1
                            if score >= 1:  # Change this to the desired win condition
                                return "completed"
                            else:
                                current_expression = generate_expression()
                        else:
                            fails += 1
                        input_text = ""
                    except ValueError:
                        pass
                elif event.key == pygame.K_BACKSPACE:
                    input_text = input_text[:-1]
                elif event.key == pygame.K_ESCAPE:
                    return "quit"
                else:
                    input_text += event.unicode
        
        if fails >= 5:
            return "died"
        
        screen.fill(BLACK)
        
        # Draw the expression
        expression_surface = font.render(f"Solve: {current_expression}", True, WHITE)
        screen.blit(expression_surface, (WIDTH // 2 - expression_surface.get_width() // 2, 100))
        
        # Draw the input box
        pygame.draw.rect(screen, WHITE, (WIDTH // 2 - 200, 200, 400, 50), 2)
        input_surface = font.render(input_text, True, WHITE)
        screen.blit(input_surface, (WIDTH // 2 - 190, 210))
        
        # Draw the score and fails
        score_surface = font.render(f"Score: {score}/10", True, GREEN)
        screen.blit(score_surface, (10, 10))
        fails_surface = font.render(f"Fails: {fails}/5", True, RED)
        screen.blit(fails_surface, (WIDTH - fails_surface.get_width() - 10, 10))
        
        # Draw instructions
        instructions = font.render("Press ESC to quit", True, WHITE)
        screen.blit(instructions, (WIDTH // 2 - instructions.get_width() // 2, HEIGHT - 50))
        
        pygame.display.flip()
        clock.tick(30)
    
    # Display final screen
    screen.fill(BLACK)
    if score >= 1:
        final_text = font.render("Congratulations! You won!", True, GREEN)
    else:
        final_text = font.render(f"Game Over. Final Score: {score}", True, WHITE)
    screen.blit(final_text, (WIDTH // 2 - final_text.get_width() // 2, HEIGHT // 2))
    pygame.display.flip()
    pygame.time.wait(2000)  # Wait for 2 seconds before returning to the main game
    
    return True  # Return True to indicate successful completion