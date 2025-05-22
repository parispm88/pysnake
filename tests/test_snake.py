"""
Unit tests for the Snake class.
"""
import unittest
import pygame
import sys
import os

# Adjust path to import from parent directory
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from snake import Snake

class TestSnake(unittest.TestCase):
    """Test cases for the Snake class."""

    @classmethod
    def setUpClass(cls):
        """Initialize Pygame for all tests in this class."""
        pygame.init()

    def setUp(self):
        """Set up a common Snake instance for tests."""
        self.initial_x = 100
        self.initial_y = 100
        self.segment_size = 20
        self.snake = Snake(self.initial_x, self.initial_y, self.segment_size)
        self.screen_width = 800
        self.screen_height = 600


    def test_snake_creation(self):
        """Test if a Snake object is created with correct initial attributes."""
        self.assertEqual(len(self.snake.body), 3)
        self.assertEqual(self.snake.body[0].topleft, (self.initial_x, self.initial_y))
        self.assertEqual(self.snake.direction, pygame.K_RIGHT)
        self.assertEqual(self.snake.segment_size, self.segment_size)

    def test_snake_move_right(self):
        """Test snake movement to the right."""
        initial_head_pos_x = self.snake.body[0].x
        self.snake.direction = pygame.K_RIGHT
        self.snake.move()
        self.assertEqual(self.snake.body[0].x, initial_head_pos_x + self.segment_size)

    def test_snake_move_left(self):
        """Test snake movement to the left."""
        # First, move right to allow left movement
        self.snake.direction = pygame.K_RIGHT
        self.snake.move()
        initial_head_pos_x = self.snake.body[0].x
        self.snake.direction = pygame.K_LEFT
        self.snake.move()
        self.assertEqual(self.snake.body[0].x, initial_head_pos_x - self.segment_size)

    def test_snake_move_up(self):
        """Test snake movement upwards."""
        initial_head_pos_y = self.snake.body[0].y
        self.snake.direction = pygame.K_UP
        self.snake.move()
        self.assertEqual(self.snake.body[0].y, initial_head_pos_y - self.segment_size)

    def test_snake_move_down(self):
        """Test snake movement downwards."""
        initial_head_pos_y = self.snake.body[0].y
        self.snake.direction = pygame.K_DOWN
        self.snake.move()
        self.assertEqual(self.snake.body[0].y, initial_head_pos_y + self.segment_size)

    def test_snake_grow(self):
        """Test if the snake grows in length."""
        initial_length = len(self.snake.body)
        self.snake.grow()
        self.snake.move()  # Growth happens on move
        self.assertEqual(len(self.snake.body), initial_length + 1)

    def test_snake_grow_multiple(self):
        """Test if the snake grows by multiple segments."""
        initial_length = len(self.snake.body)
        growth_amount = 3
        self.snake.grow(growth_amount)
        for _ in range(growth_amount):
            self.snake.move() # Each move should consume one grow_pending
        self.assertEqual(len(self.snake.body), initial_length + growth_amount)


    def test_snake_reset(self):
        """Test if the snake resets to its initial state."""
        # Change snake state
        self.snake.direction = pygame.K_DOWN
        self.snake.move()
        self.snake.grow()
        self.snake.move()

        self.snake.reset()

        self.assertEqual(len(self.snake.body), 3)
        self.assertEqual(self.snake.body[0].topleft, (self.initial_x, self.initial_y))
        self.assertEqual(self.snake.direction, pygame.K_RIGHT)
        self.assertEqual(self.snake.grow_pending, 0)

    def test_snake_self_collision(self):
        """Test snake self-collision detection."""
        # Manually create a collision scenario
        # Snake needs to be long enough and turn back on itself
        self.snake.grow(2) # Make snake 5 segments long
        self.snake.move()
        self.snake.move()
        
        # Move sequence: R, R, D, L, U (should cause collision)
        self.snake.direction = pygame.K_RIGHT
        self.snake.move() # Head at initial_x + 3*seg_size
        self.snake.direction = pygame.K_DOWN
        self.snake.move() # Head at (initial_x + 3*seg_size, initial_y + seg_size)
        self.snake.direction = pygame.K_LEFT
        self.snake.move() # Head at (initial_x + 2*seg_size, initial_y + seg_size)
        self.snake.direction = pygame.K_UP # This move will collide with the segment that was at (initial_x + 2*seg_size, initial_y)
        self.snake.move() # Head at (initial_x + 2*seg_size, initial_y) - this is where the 3rd segment (index 2) was
        
        self.assertTrue(self.snake.check_collision_self())


    def test_snake_no_self_collision(self):
        """Test no self-collision for a normal snake."""
        self.snake.move()
        self.snake.move()
        self.assertFalse(self.snake.check_collision_self())

    def test_snake_wall_collision(self):
        """Test snake collision with walls."""
        # Test collision with right wall
        self.snake.body[0].x = self.screen_width - self.segment_size
        self.snake.direction = pygame.K_RIGHT
        self.snake.move() # This move should take it out of bounds
        self.assertTrue(self.snake.check_collision_walls(self.screen_width, self.screen_height))

        self.snake.reset() # Reset for next test
        # Test collision with left wall
        self.snake.body[0].x = 0
        self.snake.direction = pygame.K_LEFT
        self.snake.move()
        self.assertTrue(self.snake.check_collision_walls(self.screen_width, self.screen_height))

        self.snake.reset()
        # Test collision with top wall
        self.snake.body[0].y = 0
        self.snake.direction = pygame.K_UP
        self.snake.move()
        self.assertTrue(self.snake.check_collision_walls(self.screen_width, self.screen_height))

        self.snake.reset()
        # Test collision with bottom wall
        self.snake.body[0].y = self.screen_height - self.segment_size
        self.snake.direction = pygame.K_DOWN
        self.snake.move()
        self.assertTrue(self.snake.check_collision_walls(self.screen_width, self.screen_height))

    def test_snake_no_wall_collision(self):
        """Test no wall collision for snake within bounds."""
        self.snake.move() # Move once to ensure it's within typical play area
        self.assertFalse(self.snake.check_collision_walls(self.screen_width, self.screen_height))

    def test_handle_input_change_direction(self):
        """Test if snake direction changes correctly on input, avoiding reversal."""
        # Initial direction is K_RIGHT
        # Try to go K_LEFT (should not change)
        left_event = pygame.event.Event(pygame.KEYDOWN, key=pygame.K_LEFT)
        self.snake.handle_input(left_event)
        self.assertEqual(self.snake.direction, pygame.K_RIGHT)

        # Try to go K_UP (should change)
        up_event = pygame.event.Event(pygame.KEYDOWN, key=pygame.K_UP)
        self.snake.handle_input(up_event)
        self.assertEqual(self.snake.direction, pygame.K_UP)

        # Try to go K_DOWN (should not change from K_UP)
        down_event = pygame.event.Event(pygame.KEYDOWN, key=pygame.K_DOWN)
        self.snake.handle_input(down_event) # Current dir is UP
        self.assertEqual(self.snake.direction, pygame.K_UP) # Should still be UP

        # Change to K_LEFT, then try K_RIGHT
        self.snake.direction = pygame.K_LEFT
        right_event = pygame.event.Event(pygame.KEYDOWN, key=pygame.K_RIGHT)
        self.snake.handle_input(right_event)
        self.assertEqual(self.snake.direction, pygame.K_LEFT)


    @classmethod
    def tearDownClass(cls):
        """Quit Pygame after all tests in this class have run."""
        pygame.quit()

if __name__ == '__main__':
    unittest.main()
