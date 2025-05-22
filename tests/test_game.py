"""
Unit tests for the Game class from main.py.
"""
import unittest
import pygame
import sys
import os

# Adjust path to import from parent directory
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from main import Game, SCREEN_WIDTH, SCREEN_HEIGHT, FPS, BRICK_ROWS, BRICK_COLS, SNAKE_MOVE_INTERVAL
from ball import Ball
from brick import Brick
from snake import Snake

class TestGame(unittest.TestCase):
    """Test cases for the Game class."""

    @classmethod
    def setUpClass(cls):
        """Initialize Pygame for all tests in this class."""
        pygame.init()
        pygame.font.init() # Game class initializes fonts

    def setUp(self):
        """Set up a common Game instance for tests."""
        self.game = Game(SCREEN_WIDTH, SCREEN_HEIGHT, FPS)

    def test_game_creation_and_initial_reset(self):
        """Test if Game object initializes correctly and reset_game works."""
        self.assertIsNotNone(self.game.player_snake)
        self.assertTrue(len(self.game.all_bricks) > 0) # Bricks should be created
        self.assertIsNotNone(self.game.game_ball)
        self.assertEqual(self.game.score, 0)
        self.assertFalse(self.game.game_over)
        self.assertEqual(self.game.snake_move_counter, 0)
        
        # Check if bricks were created according to constants
        expected_brick_count = BRICK_ROWS * BRICK_COLS
        self.assertEqual(len(self.game.all_bricks), expected_brick_count)


    def test_game_reset_method(self):
        """Test the reset_game method explicitly."""
        # Modify some game state
        self.game.score = 100
        self.game.game_over = True
        if self.game.all_bricks: # Ensure there are bricks to remove one
             first_brick = self.game.all_bricks.sprites()[0]
             first_brick.is_active = False # "Break" a brick
        
        self.game.reset_game() # Call reset

        self.assertEqual(self.game.score, 0)
        self.assertFalse(self.game.game_over)
        self.assertIsNotNone(self.game.player_snake)
        self.assertIsNotNone(self.game.game_ball)
        
        expected_brick_count = BRICK_ROWS * BRICK_COLS
        self.assertEqual(len(self.game.all_bricks), expected_brick_count)
        # All bricks should be active after reset
        all_active = all(brick.is_active for brick in self.game.all_bricks)
        self.assertTrue(all_active, "Not all bricks are active after game reset.")


    def test_score_increase_on_brick_break(self):
        """Test if score increases when a brick is broken (simulated)."""
        initial_score = self.game.score
        
        # Simulate a brick break by directly deactivating one
        # This assumes the scoring logic in Game.update() correctly counts active bricks
        if not self.game.all_bricks:
            self.fail("No bricks available to test score increase.")

        brick_to_break = self.game.all_bricks.sprites()[0]
        brick_to_break.is_active = False # Manually "break" a brick

        self.game.update() # Call update to trigger score recalculation

        # Score is calculated as (total_bricks - active_bricks)
        # So, if one brick is broken, score should be 1
        self.assertEqual(self.game.score, initial_score + 1, "Score did not increase by 1 after a brick break.")

    def test_game_over_ball_bottom(self):
        """Test game over when ball goes below the screen."""
        self.assertFalse(self.game.game_over)
        self.game.game_ball.rect.top = SCREEN_HEIGHT + 1  # Move ball below screen
        self.game.game_ball.speed_y = abs(self.game.game_ball.speed_y)  # Ensure it's moving down or horizontal
        if self.game.game_ball.speed_y == 0: # If horizontal, make it move down slightly
            self.game.game_ball.speed_y = 1

        self.game.update()
        self.assertTrue(self.game.game_over, "Game did not end when ball fell off bottom.")

    def test_game_over_snake_self_collision(self):
        """Test game over when snake collides with itself."""
        self.assertFalse(self.game.game_over)
        # Manually create a self-collision scenario for the snake
        # This requires the snake to be at least 4 segments long to turn back on itself
        self.game.player_snake.grow(2) # Grow to 5 segments
        self.game.player_snake.move()
        self.game.player_snake.move()

        self.game.player_snake.direction = pygame.K_RIGHT # Ensure it's moving
        self.game.player_snake.move()
        self.game.player_snake.direction = pygame.K_DOWN
        self.game.player_snake.move()
        self.game.player_snake.direction = pygame.K_LEFT
        self.game.player_snake.move()
        self.game.player_snake.direction = pygame.K_UP # This move should cause collision
        # The Game.update() method calls snake.move() internally after some frames,
        # so we need to ensure the snake's state is such that its *next* move (triggered by Game.update)
        # will cause a collision.
        # The check_collision_self() is called in Game.update() *after* player_snake.move()
        # So, we set up the collision, then let game.update() make the move and check.
        
        # To ensure the move happens in this update cycle:
        self.game.snake_move_counter = SNAKE_MOVE_INTERVAL -1 
        
        self.game.update() # This will call snake.move() and then check_collision_self()
        self.assertTrue(self.game.player_snake.check_collision_self(), "Snake did not register self-collision as expected.")
        self.assertTrue(self.game.game_over, "Game did not end on snake self-collision.")


    def test_game_over_snake_wall_collision(self):
        """Test game over when snake hits a wall."""
        self.assertFalse(self.game.game_over)
        self.game.player_snake.body[0].x = SCREEN_WIDTH - self.game.player_snake.segment_size
        self.game.player_snake.direction = pygame.K_RIGHT
        
        # Ensure snake moves in this update cycle
        self.game.snake_move_counter = SNAKE_MOVE_INTERVAL -1
        
        self.game.update() # This will move the snake and then check wall collision
        self.assertTrue(self.game.game_over, "Game did not end when snake hit a wall.")

    @classmethod
    def tearDownClass(cls):
        """Quit Pygame after all tests in this class have run."""
        pygame.quit()

if __name__ == '__main__':
    unittest.main()
