import pygame

class Brick(pygame.sprite.Sprite):
    def __init__(self, x, y, width, height, color):
        super().__init__()
        self.image = pygame.Surface([width, height])
        self.image.fill(color)
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.color = color # Store color for potential future use (e.g. different point values)
        self.is_active = True # To mark if the brick is broken or not

    def draw(self, surface):
        if self.is_active:
            surface.blit(self.image, self.rect) 