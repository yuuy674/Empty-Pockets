import pygame
import sys

# --- Tile Class ---
class Tile:
    def __init__(self, x, y, size, color=(0, 255, 0)):
        #nessacary parameters
        self.x = x
        self.y = y
        self.size = size
        self.color = color
        #creates a rectangle to draw
        self.rect = pygame.Rect(x * size, y * size, size, size)

    def draw(self, surface):
        pygame.draw.rect(surface, self.color, self.rect)
        pygame.draw.rect(surface, (50, 50, 50), self.rect, 1)  # border


        
