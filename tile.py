import pygame
import sys

# --- Tile Class ---
class Tile:
    def __init__(self, x, y, size, color=(0, 255, 0)):
        # Store grid position (x, y) and tile size
        self.x = x
        self.y = y
        self.size = size
        self.color = color

        # Create a rectangle representing the tile's position and dimensions in pixels
        # Multiplying x and y by size converts grid coordinates into screen coordinates
        self.rect = pygame.Rect(x * size, y * size, size, size)

    def draw(self, surface):
        # Draw the filled tile rectangle
        pygame.draw.rect(surface, self.color, self.rect)
        # Draw a thin border around the tile for visual separation
        pygame.draw.rect(surface, (50, 50, 50), self.rect, 1)

