"""
Defines the PowerUp class for the Pysnake Break game.
"""
import pygame

POWER_UP_TYPES = ["wider_paddle", "slow_ball"]
POWER_UP_COLORS = {
    "wider_paddle": (0, 255, 255),  # Cyan
    "slow_ball": (255, 105, 180)  # Hot Pink
}
POWER_UP_SIZE = (15, 15)
POWER_UP_SPEED = 3

class PowerUp(pygame.sprite.Sprite):
    """
    Represents a power-up item that can be collected by the player.

    Attributes:
        type (str): The type of power-up (e.g., "wider_paddle", "slow_ball").
        image (pygame.Surface): The visual representation of the power-up.
        rect (pygame.Rect): The rectangular area of the power-up.
        speed_y (int): The speed at which the power-up falls.
    """
    def __init__(self, x, y, type):
        """
        Initializes the PowerUp object.

        Args:
            x (int): The initial x-coordinate of the power-up's center.
            y (int): The initial y-coordinate of the power-up's center.
            type (str): The type of the power-up. Must be one of POWER_UP_TYPES.
        """
        super().__init__()
        if type not in POWER_UP_TYPES:
            raise ValueError(f"Unknown power-up type: {type}")
        self.type = type
        self.color = POWER_UP_COLORS.get(type, (128, 128, 128)) # Default to gray if type somehow invalid

        self.image = pygame.Surface([POWER_UP_SIZE[0], POWER_UP_SIZE[1]])
        self.image.fill(self.color)
        self.rect = self.image.get_rect(center=(x, y))
        self.speed_y = POWER_UP_SPEED

    def update(self, screen_height):
        """
        Moves the power-up down the screen.

        If the power-up moves off the bottom of the screen, it is removed.

        Args:
            screen_height (int): The height of the game screen.
        """
        self.rect.y += self.speed_y
        if self.rect.top > screen_height:
            self.kill()  # Remove sprite from all groups

    def draw(self, surface):
        """
        Draws the power-up on the given surface.

        Args:
            surface (pygame.Surface): The surface to draw the power-up on.
        """
        surface.blit(self.image, self.rect)

[end of powerup.py]
