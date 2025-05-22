"""
Unit tests for the Ball class.
"""
import unittest
import pygame
import sys
import os

# Adjust path to import from parent directory
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from ball import Ball

class TestBall(unittest.TestCase):
    """Test cases for the Ball class."""

    @classmethod
    def setUpClass(cls):
        """Initialize Pygame for all tests in this class."""
        pygame.init()

    def setUp(self):
        """Set up a common Ball instance for tests."""
        self.initial_x = 100
        self.initial_y = 100
        self.radius = 10
        self.color = (255, 0, 0)  # Red
        self.speed_x = 5
        self.speed_y = 5
        self.ball = Ball(
            self.initial_x,
            self.initial_y,
            self.radius,
            self.color,
            self.speed_x,
            self.speed_y)
        # Define screen dimensions for collision tests
        self.screen_width = 800
        self.screen_height = 600

    def test_ball_creation(self):
        """Test if a Ball object is created with correct initial attributes."""
        self.assertEqual(self.ball.radius, self.radius)
        self.assertEqual(self.ball.color, self.color)
        self.assertEqual(self.ball.rect.centerx, self.initial_x)
        self.assertEqual(self.ball.rect.centery, self.initial_y)
        self.assertEqual(self.ball.speed_x, self.speed_x)
        self.assertEqual(self.ball.speed_y, self.speed_y)
        self.assertEqual(self.ball.initial_x, self.initial_x)
        self.assertEqual(self.ball.initial_y, self.initial_y)

    def test_ball_move(self):
        """Test if ball.rect updates correctly after update() calls."""
        initial_rect_x = self.ball.rect.x
        initial_rect_y = self.ball.rect.y

        # Simulate two updates without collisions
        self.ball.update(self.screen_width, self.screen_height, [], pygame.sprite.Group())
        self.ball.update(self.screen_width, self.screen_height, [], pygame.sprite.Group())

        expected_x = initial_rect_x + 2 * self.speed_x
        expected_y = initial_rect_y + 2 * self.speed_y

        self.assertEqual(self.ball.rect.x, expected_x)
        self.assertEqual(self.ball.rect.y, expected_y)

    def test_ball_wall_collision_left_right(self):
        """Test if speed_x inverts when hitting left/right walls."""
        # Test right wall collision
        self.ball.rect.right = self.screen_width + 5  # Move ball to hit the right wall
        initial_speed_x = self.ball.speed_x
        self.ball.update(self.screen_width, self.screen_height, [], pygame.sprite.Group())
        self.assertEqual(self.ball.speed_x, -initial_speed_x)
        self.assertTrue(self.ball.rect.right <= self.screen_width) # Check clamped

        # Reset speed_x to positive for left wall test
        self.ball.speed_x = abs(initial_speed_x)
        self.ball.rect.left = -5  # Move ball to hit the left wall
        self.ball.update(self.screen_width, self.screen_height, [], pygame.sprite.Group())
        self.assertEqual(self.ball.speed_x, -abs(initial_speed_x)) # Speed should be negative now
        self.assertTrue(self.ball.rect.left >= 0) # Check clamped

    def test_ball_wall_collision_top(self):
        """Test if speed_y inverts when hitting the top wall."""
        self.ball.rect.top = -5  # Move ball to hit the top wall
        initial_speed_y = self.ball.speed_y
        self.ball.update(self.screen_width, self.screen_height, [], pygame.sprite.Group())
        self.assertEqual(self.ball.speed_y, -initial_speed_y)
        self.assertTrue(self.ball.rect.top >= 0) # Check clamped

    def test_ball_reset(self):
        """Test if ball.rect.center is reset to its initial position."""
        # Move the ball
        self.ball.rect.x += 50
        self.ball.rect.y += 50
        # Reset the ball
        self.ball.reset()
        self.assertEqual(self.ball.rect.centerx, self.initial_x)
        self.assertEqual(self.ball.rect.centery, self.initial_y)

    @classmethod
    def tearDownClass(cls):
        """Quit Pygame after all tests in this class have run."""
        pygame.quit()

if __name__ == '__main__':
    unittest.main()
