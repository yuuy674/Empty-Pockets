import pygame

class Port:
    def __init__(self):
        self.lvl = 1
        self.inventory = {}
        self.profit = 0
        self.position = None
        self.rect = None
        self.color = None

        # Define base prices for resources (you can expand this)
        self.prices = {
            "textile": 28,
            "furniture": 30,
            "steel": 50,   
            "food": 20,
            "tools": 22,
            "iron": 30,
            "coal": 15,
        }


    def set_position(self, tile, tile_size, color):
        self.position = tile
        x, y = tile
        px = x * tile_size
        py = y * tile_size
        self.rect = pygame.Rect(px, py, tile_size, tile_size)
        self.color = color

    def draw(self, surface):
        if self.rect:
            pygame.draw.rect(surface, self.color, self.rect)

    def receive(self, resource, amount):
        price = self.prices.get(resource, 1)
        earned = price * amount
        self.profit += earned
        print(f"Auto-sold {amount} {resource} for ${earned} profit.")
        return earned


    def sell(self):
        """Sell all goods in inventory and return profit earned this round."""
        total_sale = 0
        for resource, amount in list(self.inventory.items()):
            if amount > 0:
                price = self.prices.get(resource, 1)
                earned = price * amount
                total_sale += earned
                self.profit += earned
                print(f"Sold {amount} {resource} for {earned} profit.")
                self.inventory[resource] = 0
        return total_sale


    def report(self):
        return {
            "Level": self.lvl,
            "Inventory": self.inventory,
            "Profit": self.profit
        }
