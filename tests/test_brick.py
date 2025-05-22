"""
Unit tests for the Brick class.
"""
import unittest
import pygame
import sys
import os

# Adjust path to import from parent directory
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from brick import Brick

class TestBrick(unittest.TestCase):
    """Test cases for the Brick class."""

    @classmethod
    def setUpClass(cls):
        """Initialize Pygame for all tests in this class."""
        pygame.init() # Brick uses pygame.Surface

    def setUp(self):
        """Set up a common Brick instance for tests."""
        self.x = 50
        self.y = 50
        self.width = 75
        self.height = 20
        self.color = (0, 0, 255)  # Blue
        self.brick = Brick(self.x, self.y, self.width, self.height, self.color)

    def test_brick_creation(self):
        """Test if a Brick object is created with correct initial attributes."""
        self.assertEqual(self.brick.rect.x, self.x)
        self.assertEqual(self.brick.rect.y, self.y)
        self.assertEqual(self.brick.rect.width, self.width)
        self.assertEqual(self.brick.rect.height, self.height)
        self.assertEqual(self.brick.color, self.color)
        self.assertTrue(self.brick.is_active)
        self.assertIsNotNone(self.brick.image)
        self.assertEqual(self.brick.image.get_size(), (self.width, self.height))

    def test_brick_break(self):
        """Test the state change of a brick when it's broken."""
        self.assertTrue(self.brick.is_active)
        # Simulate the brick being broken (this is usually done by the Ball class)
        self.brick.is_active = False
        self.assertFalse(self.brick.is_active)

    def test_brick_draw_active(self):
        """Test that an active brick draws itself."""
        surface = pygame.Surface((100, 100))
        surface.fill((0,0,0)) # Fill with black
        self.brick.is_active = True
        self.brick.draw(surface)
        # Check if the brick's color is present on the surface
        # This is a simple check; more complex checks could look at specific pixels
        self.assertTrue(surface.get_at((self.x + 5, self.y + 5)) == self.color)

    def test_brick_draw_inactive(self):
        """Test that an inactive brick does not draw itself."""
        surface = pygame.Surface((self.x + self.width + 10, self.y + self.height + 10))
        initial_color = (1, 2, 3) # Unique color
        surface.fill(initial_color)

        self.brick.is_active = False
        self.brick.draw(surface)

        # Check that the area where the brick would be is still the initial_color
        # This implies the brick did not draw over it.
        # Check a few points within the brick's area.
        points_to_check = [
            (self.brick.rect.left, self.brick.rect.top),
            (self.brick.rect.centerx, self.brick.rect.centery),
            (self.brick.rect.right -1, self.brick.rect.bottom -1)
        ]
        for point_x, point_y in points_to_check:
             # Ensure points are within surface bounds for get_at
            if 0 <= point_x < surface.get_width() and 0 <= point_y < surface.get_height():
                self.assertEqual(surface.get_at((point_x, point_y)), initial_color,
                                 f"Inactive brick drew at ({point_x}, {point_y})")


    @classmethod
    def tearDownClass(cls):
        """Quit Pygame after all tests in this class have run."""
        pygame.quit()

if __name__ == '__main__':
    unittest.main()
