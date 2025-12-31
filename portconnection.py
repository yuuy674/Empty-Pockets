import pygame

class PortConnection:
    def __init__(self, producer, port, capacity=50):
        self.producer = producer   # factory or mine
        self.port = port           # Port instance
        self.capacity = capacity   # max units per tick
        self.active = True

    def transfer(self):
        # capacity grows with producer level
        capacity = self.capacity * self.producer.lvl
        resource, _ = list(self.producer.output_product.items())[0]
        available = self.producer.inventory.get(resource, 0)
        to_send = min(available, capacity)
        if to_send > 0:
            self.producer.inventory[resource] -= to_send
            earned = self.port.receive(resource, to_send)
            return earned
        return 0

    def draw(self, surface, tile_size=40):
        if getattr(self.producer, "position", None) and getattr(self.port, "position", None):
            px, py = self.producer.position
            qx, qy = self.port.position
            pygame.draw.line(
                surface, (0, 0, 255),
                (px*tile_size + tile_size//2, py*tile_size + tile_size//2),
                (qx*tile_size + tile_size//2, qy*tile_size + tile_size//2),
                2
            )
