import pygame

class Snake:
    def __init__(self, x, y, segment_size=20, color=(0, 255, 0)):
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
        self.grow_pending = 0 # Number of segments to add
        # For controlling movement speed
        self.initial_x = x
        self.initial_y = y

    def move(self):
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
        self.body = [
            pygame.Rect(self.initial_x, self.initial_y, self.segment_size, self.segment_size),
            pygame.Rect(self.initial_x - self.segment_size, self.initial_y, self.segment_size, self.segment_size),
            pygame.Rect(self.initial_x - (2 * self.segment_size), self.initial_y, self.segment_size, self.segment_size),
        ]
        self.direction = pygame.K_RIGHT
        self.grow_pending = 0

    def grow(self, segments=1):
        self.grow_pending += segments

    def draw(self, surface):
        for segment in self.body:
            pygame.draw.rect(surface, self.color, segment)
            pygame.draw.rect(surface, (0,100,0), segment, 2) # Border for segments

    def handle_input(self, event):
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
        head = self.body[0]
        for segment in self.body[1:]:
            if head.colliderect(segment):
                return True
        return False

    def check_collision_walls(self, screen_width, screen_height):
        head = self.body[0]
        if not (0 <= head.x < screen_width and 0 <= head.y < screen_height):
            return True
        return False 