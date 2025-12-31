import pygame

class Button:
    def __init__(self, top_left_tile, bottom_right_tile, tile_size, color=(0, 255, 0), image=None, on_click_function=None):
        x1, y1 = top_left_tile
        x2, y2 = bottom_right_tile

        # Convert tile coordinates into pixel coordinates
        px = x1 * tile_size
        py = y1 * tile_size
        width = (x2 - x1 + 1) * tile_size
        height = (y2 - y1 + 1) * tile_size

        self.rect = pygame.Rect(px, py, width, height)
        self.color = color
        self.image = image
        self.on_click_function = on_click_function
        self.visible = True

    def draw(self, surface):
        if not self.visible:
            return  # skip drawing if hidden
        pygame.draw.rect(surface, self.color, self.rect)
        if self.image:
            image_rect = self.image.get_rect(center=self.rect.center)
            surface.blit(self.image, image_rect)

    def is_clicked(self, event):
        if not self.visible:
            return  # ignore clicks if hidden
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.rect.collidepoint(event.pos):
                self.on_click_function()

    def show(self):
        self.visible = True
    def hide(self):
        self.visible = False
    def toggle(self):
        self.visible = not self.visible
