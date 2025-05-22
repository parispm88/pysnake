"""
Defines the Brick class for the Pysnake Break game.
"""
import pygame


class Brick(pygame.sprite.Sprite):
    """
    Represents a destructible brick in the game.

    Attributes:
        image (pygame.Surface): The surface representing the brick.
        rect (pygame.Rect): The rectangular area of the brick.
        color (tuple): The color of the brick (R, G, B).
        is_active (bool): True if brick is present, False if broken.
                          Becomes False when hit by the ball.
    """

    def __init__(self, x, y, width, height, color, power_up_type=None):
        """
        Initializes the Brick object.

        Args:
            x (int): The x-coordinate of the top-left corner of the brick.
            y (int): The y-coordinate of the top-left corner of the brick.
            width (int): The width of the brick.
            height (int): The height of the brick.
            color (tuple): The color of the brick (R, G, B).
            power_up_type (str, optional): The type of power-up this brick holds.
                                           Defaults to None.
        """
        super().__init__()
        self.image = pygame.Surface([width, height])
        self.image.fill(color)
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        # Store color for potential future use (e.g. different point values)
        self.color = color
        self.is_active = True  # To mark if the brick is broken or not
        self.power_up_type = power_up_type

    def draw(self, surface):
        """
        Draws the brick on the given surface if it is active.

        If `self.is_active` is False, this method does nothing.

        Args:
            surface (pygame.Surface): The surface to draw the brick on.
        """
        if self.is_active:
            surface.blit(self.image, self.rect)
