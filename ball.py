import pygame

class Ball(pygame.sprite.Sprite):
    def __init__(self, x, y, radius, color, speed_x, speed_y):
        super().__init__()
        self.radius = radius
        self.color = color
        self.image = pygame.Surface([radius * 2, radius * 2], pygame.SRCALPHA) # SRCALPHA for transparency
        pygame.draw.circle(self.image, self.color, (radius, radius), radius)
        self.rect = self.image.get_rect(center=(x, y))
        self.speed_x = speed_x
        self.speed_y = speed_y
        self.initial_x = x # Store initial position for reset
        self.initial_y = y

    def update(self, screen_width, screen_height, snake_body_rects, bricks_group):
        self.rect.x += self.speed_x
        self.rect.y += self.speed_y

        # Wall collision
        if self.rect.left <= 0 or self.rect.right >= screen_width:
            self.speed_x *= -1
            self.rect.clamp_ip(pygame.Rect(0, 0, screen_width, screen_height)) # Clamp to screen
        if self.rect.top <= 0:
            self.speed_y *= -1
            self.rect.clamp_ip(pygame.Rect(0, 0, screen_width, screen_height)) # Clamp to screen
        # if self.rect.bottom >= screen_height: # Lose condition - handle in main game loop
            # self.reset() # Or handle game over

        # Snake collision (treat snake head as paddle)
        # For simplicity, we'll check collision with all snake segments for now.
        # A more refined approach might only consider the head or a specific part.
        for segment_rect in snake_body_rects:
            if self.rect.colliderect(segment_rect):
                self.speed_y *= -1 # Simple vertical bounce for now
                # More complex bounce logic can be added here (e.g., based on hit position)
                self.rect.bottom = segment_rect.top # Prevent sticking
                break # Avoid multiple collisions in one frame

        # Brick collision
        collided_bricks = pygame.sprite.spritecollide(self, bricks_group, False) # False means don't kill
        for brick in collided_bricks:
            if brick.is_active:
                self.speed_y *= -1 # Bounce off brick
                brick.is_active = False # "Break" the brick
                # Could add scoring here
                # To prevent phasing, adjust ball position slightly after collision
                if self.speed_y > 0: # Moving down, hit top of brick
                    self.rect.bottom = brick.rect.top
                else: # Moving up, hit bottom of brick
                    self.rect.top = brick.rect.bottom
                break # Only handle one brick collision per frame to simplify bounce

    def draw(self, surface):
        surface.blit(self.image, self.rect)

    def reset(self):
        self.rect.center = (self.initial_x, self.initial_y)
        # Could also reset speed to a default if it changes 