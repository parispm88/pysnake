"""
Defines the Snake class, used as the player-controlled paddle in Pysnake Break.
"""
import pygame


class Snake:
    """
    Represents the player-controlled snake, which acts as the paddle.

    The snake consists of a series of rectangular segments. It moves in one of
    four cardinal directions. The snake can "grow" by adding segments, though
    this feature might not be actively used in the brick breaker game context.
    It is controlled by player input to change its direction.

    Attributes:
        segment_size (int): Width and height of each segment.
        color (tuple): Color of the snake (R, G, B).
        body (list[pygame.Rect]): List of Rects for snake segments. Head is at
                                   index 0.
        direction (int): Current movement direction (pygame key constants).
        grow_pending (int): Number of segments to add on next move.
        initial_x (int): Initial x-coordinate of the snake's head.
        initial_y (int): Initial y-coordinate of the snake's head.
    """

    def __init__(self, x, y, segment_size=20, color=(0, 255, 0)):
        """
        Initializes the Snake object.

        Sets up the snake's initial position, size, color, and direction.
        The snake starts with three segments.

        Args:
            x (int): The initial x-coordinate for the head of the snake.
            y (int): The initial y-coordinate for the head of the snake.
            segment_size (int, optional): The size (width and height) of each
                                          snake segment. Defaults to 20.
            color (tuple, optional): The color of the snake (R, G, B).
                                     Defaults to green (0, 255, 0).
        """
        self.segment_size = segment_size
        self.color = color
        # Initial snake with 3 segments
        self.body = [
            pygame.Rect(x, y, segment_size, segment_size),
            pygame.Rect(x - segment_size, y, segment_size, segment_size),
            pygame.Rect(x - (2 * segment_size), y, segment_size, segment_size),
        ]
        # Initial direction (e.g., moving right)
        # We'll use pygame key constants for directions for consistency later
        self.direction = pygame.K_RIGHT
        self.grow_pending = 0  # Number of segments to add
        # For controlling movement speed
        self.initial_x = x
        self.initial_y = y

    def move(self):
        """
        Moves the snake one step in its current direction.

        A new head segment is added in the direction of movement. If no growth
        is pending, the tail segment is removed. If growth is pending, the
        tail is not removed, and `grow_pending` is decremented.
        """
        head = self.body[0].copy()
        if self.direction == pygame.K_UP:
            head.y -= self.segment_size
        elif self.direction == pygame.K_DOWN:
            head.y += self.segment_size
        elif self.direction == pygame.K_LEFT:
            head.x -= self.segment_size
        elif self.direction == pygame.K_RIGHT:
            head.x += self.segment_size

        self.body.insert(0, head)

        if self.grow_pending > 0:
            self.grow_pending -= 1
        else:
            self.body.pop()

    def reset(self):
        """
        Resets the snake to its initial state and position.

        Body is reconstructed at `initial_x`, `initial_y`, facing right,
        with three segments and no pending growth.
        """
        self.body = [
            pygame.Rect(
                self.initial_x,
                self.initial_y,
                self.segment_size,
                self.segment_size),
            pygame.Rect(
                self.initial_x -
                self.segment_size,
                self.initial_y,
                self.segment_size,
                self.segment_size),
            pygame.Rect(
                self.initial_x -
                (
                    2 *
                    self.segment_size),
                self.initial_y,
                self.segment_size,
                self.segment_size),
        ]
        self.direction = pygame.K_RIGHT
        self.grow_pending = 0

    def grow(self, segments=1):
        """
        Marks a specified number of segments to be added to the snake.

        The actual growth happens during the `move` method. This method
        increments the `grow_pending` counter.

        Args:
            segments (int, optional): The number of segments to add.
                                      Defaults to 1.
        """
        self.grow_pending += segments

    def draw(self, surface):
        """
        Draws the snake on the given surface.

        Each segment of the snake is drawn as a colored rectangle with a
        slightly darker border.

        Args:
            surface (pygame.Surface): The surface to draw the snake on.
        """
        for segment in self.body:
            pygame.draw.rect(surface, self.color, segment)
            pygame.draw.rect(surface, (0, 100, 0), segment,
                             2)  # Border for segments

    def handle_input(self, event):
        """
        Changes the snake's direction based on keyboard input.

        Responds to arrow key presses (K_UP, K_DOWN, K_LEFT, K_RIGHT) to
        change the snake's direction. Prevents the snake from immediately
        reversing onto itself.

        Args:
            event (pygame.event.Event): The Pygame event to process.
        """
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP and self.direction != pygame.K_DOWN:
                self.direction = pygame.K_UP
            elif event.key == pygame.K_DOWN and self.direction != pygame.K_UP:
                self.direction = pygame.K_DOWN
            elif event.key == pygame.K_LEFT and self.direction != pygame.K_RIGHT:
                self.direction = pygame.K_LEFT
            elif event.key == pygame.K_RIGHT and self.direction != pygame.K_LEFT:
                self.direction = pygame.K_RIGHT

    def check_collision_self(self):
        """
        Checks if the snake's head has collided with any part of its body.

        Returns:
            bool: True if a collision with itself is detected, False otherwise.
        """
        head = self.body[0]
        for segment in self.body[1:]:
            if head.colliderect(segment):
                return True
        return False

    def check_collision_walls(self, screen_width, screen_height):
        """
        Checks if the snake's head has collided with screen boundaries.

        Args:
            screen_width (int): Width of the game screen.
            screen_height (int): Height of the game screen.

        Returns:
            bool: True if wall collision detected, False otherwise.
        """
        head = self.body[0]
        if not (0 <= head.x < screen_width and 0 <= head.y < screen_height):
            return True
        return False
