import pygame
import sys
from snake import Snake # Import the Snake class
from brick import Brick # Import the Brick class
from ball import Ball # Import the Ball class

# Constants
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
FPS = 30 # Increase FPS a bit for smoother ball movement
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GREEN = (0, 255, 0)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0) # Ball color

# Brick constants
BRICK_WIDTH = 75
BRICK_HEIGHT = 20
BRICK_PADDING = 5
BRICK_OFFSET_TOP = 50
BRICK_OFFSET_LEFT = 50
BRICK_ROWS = 5
BRICK_COLS = (SCREEN_WIDTH - (2 * BRICK_OFFSET_LEFT)) // (BRICK_WIDTH + BRICK_PADDING)

# Ball constants
BALL_RADIUS = 10
BALL_SPEED_X_INITIAL = 4
BALL_SPEED_Y_INITIAL = -4

# Snake movement control
SNAKE_MOVE_INTERVAL = 5  # Move snake every 5 game frames

# Global game state variables (makes reset easier)
player_snake = None
all_bricks = None
game_ball = None
game_over = False
score = 0
snake_move_counter = 0

def create_bricks_layout(): # Renamed to avoid conflict, more descriptive
    bricks = pygame.sprite.Group()
    brick_colors = [RED, (255, 165, 0), YELLOW, GREEN, BLUE] # More colors
    for row in range(BRICK_ROWS):
        for col in range(BRICK_COLS):
            x = BRICK_OFFSET_LEFT + col * (BRICK_WIDTH + BRICK_PADDING)
            y = BRICK_OFFSET_TOP + row * (BRICK_HEIGHT + BRICK_PADDING)
            brick_color = brick_colors[row % len(brick_colors)]
            brick = Brick(x, y, BRICK_WIDTH, BRICK_HEIGHT, brick_color)
            bricks.add(brick)
    return bricks

def reset_game_state():
    global player_snake, all_bricks, game_ball, game_over, score, snake_move_counter

    snake_start_x = SCREEN_WIDTH // 2
    snake_start_y = SCREEN_HEIGHT - 50
    player_snake = Snake(snake_start_x, snake_start_y, color=GREEN)

    all_bricks = create_bricks_layout()

    ball_start_x = SCREEN_WIDTH // 2
    ball_start_y = player_snake.body[0].top - BALL_RADIUS - 5
    game_ball = Ball(ball_start_x, ball_start_y, BALL_RADIUS, YELLOW, BALL_SPEED_X_INITIAL, BALL_SPEED_Y_INITIAL)
    
    game_over = False
    score = 0
    snake_move_counter = 0

def main():
    global player_snake, all_bricks, game_ball, game_over, score, snake_move_counter

    pygame.init()
    pygame.font.init() # Ensure font module is initialized

    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Pysnake Break")
    clock = pygame.time.Clock()
    font = pygame.font.Font(None, 36) # For score and messages
    game_over_font = pygame.font.Font(None, 74)
    restart_font = pygame.font.Font(None, 50)

    reset_game_state() # Initialize game state for the first time

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if game_over:
                if event.type == pygame.KEYDOWN and event.key == pygame.K_r:
                    reset_game_state()
            else:
                player_snake.handle_input(event)

        if not game_over:
            snake_move_counter += 1
            if snake_move_counter >= SNAKE_MOVE_INTERVAL:
                player_snake.move()
                snake_move_counter = 0
            
            game_ball.update(SCREEN_WIDTH, SCREEN_HEIGHT, player_snake.body, all_bricks)
            
            # Update score based on broken bricks
            # A better way: Ball.update could return points for broken bricks
            new_score = BRICK_ROWS * BRICK_COLS - len([b for b in all_bricks if b.is_active])
            if new_score > score:
                score = new_score # Simple scoring: 1 point per brick

            if player_snake.check_collision_self() or \
               player_snake.check_collision_walls(SCREEN_WIDTH, SCREEN_HEIGHT):
                game_over = True
            
            if game_ball.rect.top > SCREEN_HEIGHT:
                game_over = True 

        screen.fill(BLACK)
        player_snake.draw(screen)
        all_bricks.draw(screen)
        game_ball.draw(screen)

        # Display Score
        score_text = font.render(f"Score: {score}", True, WHITE)
        screen.blit(score_text, (10, 10))

        if game_over:
            text = game_over_font.render("GAME OVER", True, RED)
            text_rect = text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 50))
            screen.blit(text, text_rect)
            
            restart_text_surface = restart_font.render("Press 'R' to Restart", True, WHITE)
            restart_text_rect = restart_text_surface.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 50))
            screen.blit(restart_text_surface, restart_text_rect)

        pygame.display.flip()
        clock.tick(FPS)

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
