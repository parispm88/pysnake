"""
Defines the Ball class for the Pysnake Break game.
"""
import pygame
from powerup import PowerUp # Import PowerUp class


class Ball(pygame.sprite.Sprite):
    """
    Represents the game ball.

    Attributes:
        radius (int): The radius of the ball.
        color (tuple): The color of the ball (R, G, B).
        image (pygame.Surface): The surface representing the ball.
        rect (pygame.Rect): The rectangular area of the ball.
        speed_x (int): The horizontal speed of the ball.
        speed_y (int): The vertical speed of the ball.
        initial_x (int): The initial x-coordinate of the ball.
        initial_y (int): The initial y-coordinate of the ball.

    The ball moves and bounces off walls, the snake (paddle), and bricks.
    Breaking a brick causes it to disappear.
    """

    def __init__(self, x, y, radius, color, speed_x, speed_y):
        """
        Initializes the Ball object.

        Args:
            x (int): The initial x-coordinate of the ball's center.
            y (int): The initial y-coordinate of the ball's center.
            radius (int): The radius of the ball.
            color (tuple): The color of the ball (R, G, B).
            speed_x (int): The initial horizontal speed of the ball.
            speed_y (int): The initial vertical speed of the ball.
        """
        super().__init__()
        self.radius = radius
        self.color = color
        # SRCALPHA for transparency
        self.image = pygame.Surface([radius * 2, radius * 2], pygame.SRCALPHA)
        pygame.draw.circle(self.image, self.color, (radius, radius), radius)
        self.rect = self.image.get_rect(center=(x, y))
        self.speed_x = speed_x
        self.speed_y = speed_y
        self.initial_x = x  # Store initial position for reset
        self.initial_y = y

    def update(
            self,
            screen_width,
            screen_height,
            snake_body_rects,
            bricks_group): # Removed power_ups_group from signature
        """
        Updates the ball's position and handles collisions.

        Moves the ball according to its speed. Reverses direction upon hitting
        screen boundaries (walls). Bounces off the snake (paddle) and breaks
        bricks upon collision. Spawns power-ups if a brick has one.

        Args:
            screen_width (int): The width of the game screen.
            screen_height (int): The height of the game screen.
            snake_body_rects (list[pygame.Rect]): List of snake's body segment
                                                  rectangles.
            bricks_group (pygame.sprite.Group): A sprite group containing the bricks.
        
        Returns:
            tuple: (points_from_bricks, spawned_power_ups_list)
                   points_from_bricks (int): Score obtained from breaking bricks.
                   spawned_power_ups_list (list): List of PowerUp objects spawned.
        """
        spawned_power_ups = []
        points_from_bricks = 0

        self.rect.x += self.speed_x
        self.rect.y += self.speed_y

        # Wall collision
        if self.rect.left <= 0 or self.rect.right >= screen_width:
            self.speed_x *= -1
            self.rect.clamp_ip(
                pygame.Rect(
                    0,
                    0,
                    screen_width,
                    screen_height))  # Clamp to screen
        if self.rect.top <= 0:
            self.speed_y *= -1
            self.rect.clamp_ip(
                pygame.Rect(
                    0,
                    0,
                    screen_width,
                    screen_height))  # Clamp to screen
        # if self.rect.bottom >= screen_height: # Lose condition - handle in main game loop
            # self.reset() # Or handle game over

        # Snake collision
        # We check collision with all snake segments.
        # A more refined approach might only consider the head.
        for segment_rect in snake_body_rects:
            if self.rect.colliderect(segment_rect):
                self.speed_y *= -1  # Simple vertical bounce
                # More complex bounce logic can be added (e.g., based on hit position)
                self.rect.bottom = segment_rect.top  # Prevent sticking
                break  # Avoid multiple collisions

        # Brick collision
        collided_bricks = pygame.sprite.spritecollide(
            self, bricks_group, False)  # False: don't kill bricks on collision
        for brick in collided_bricks:
            if brick.is_active:
                self.speed_y *= -1  # Bounce off brick
                brick.is_active = False  # "Break" the brick
                points_from_bricks += 1 # Simple scoring: 1 point per brick

                if hasattr(brick, 'power_up_type') and brick.power_up_type:
                    new_power_up = PowerUp(brick.rect.centerx, brick.rect.centery, brick.power_up_type)
                    spawned_power_ups.append(new_power_up)

                # To prevent phasing, adjust ball position slightly
                if self.speed_y > 0:  # Moving down
                    self.rect.bottom = brick.rect.top
                else:  # Moving up
                    self.rect.top = brick.rect.bottom
                break  # Handle one brick collision per frame
        
        return points_from_bricks, spawned_power_ups

    def draw(self, surface):
        """
        Draws the ball on the given surface.

        Args:
            surface (pygame.Surface): The surface to draw the ball on.
        """
        surface.blit(self.image, self.rect)

    def reset(self):
        """
        Resets the ball to its initial position.

        The ball's center is moved back to its stored initial_x and initial_y.
        Speed is not reset by this method.
        """
        self.rect.center = (self.initial_x, self.initial_y)
        # Could also reset speed to a default
