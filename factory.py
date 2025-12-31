# FACTORY CLASS
# TYPES: TEXTILE, FURNITURE, STEEL, FOOD, TOOLS

import pygame

class Factory():
    def __init__(self, type):
        self.lvl = 1
        self.productivity = .2
        self.max_employment = 100
        self.position = None
        self.employees = 0
        self.skilled_worker_ratio = .05
        self.upkeep_mod = 0
        self.last_output = 0
        self.req_resources = []
        self.image = None
        self.inventory = {
            "wood": float('inf'),
            "cotton": float('inf')
        }
        t = type.upper()
        if t == "TEXTILE":
            self.type = "textile"
            self.input_resources = {"cotton": 2}
            self.output_product = {"textile": 1}
            self.image = pygame.image.load("./images/TEXTILE_BUTTON.png")
            self.image = pygame.transform.scale(self.image, (40, 40))
        elif t == "FURNITURE":
            self.type = "furniture"
            self.input_resources = {"wood": 3, "tools": 1}
            self.output_product = {"furniture": 1}
            self.image = pygame.image.load("./images/FURNITURE_BUTTON.png")
            self.image = pygame.transform.scale(self.image, (40, 40))
        elif t == "STEEL":
            self.type = "steel"
            self.input_resources = {"iron": 2, "coal": 1}
            self.output_product = {"steel": 1}
            self.image = pygame.image.load("./images/STEEL_BUTTON.png")
            self.image = pygame.transform.scale(self.image, (40, 40))
        elif t == "FOOD":
            self.type = "food"
            self.input_resources = {"tools": 1}
            self.upkeep_mod += 200
            self.output_product = {"food": 2}
            self.image = pygame.image.load("./images/FOOD_BUTTON.png")
            self.image = pygame.transform.scale(self.image, (40, 40))
        elif t == "TOOLS":
            self.type = "tools"
            self.input_resources = {"wood": 1}
            self.upkeep_mod += 200
            self.output_product = {"tools": 3}
            self.image = pygame.image.load("./images/TOOLS_BUTTON.png")
            self.image = pygame.transform.scale(self.image, (40, 40))
        elif t == "OIL":
            self.type = "oil"
            self.input_resources = {"tools": 3, "iron": 1}
            self.output_product = {"oil": 1}
            self.image = pygame.image.load("./images/OIL_BUTTON.png")
            self.image = pygame.transform.scale(self.image, (40, 40))

    def update_lvl(self, lvl_increment):
        self.lvl += lvl_increment
        self.productivity = round(1.1 ** self.lvl, 2)

        # Map level range [1, 10] to ratio range [0.05, 0.25]
        def linear_map(value, in_min, in_max, out_min, out_max):
            return out_min + (float(value - in_min) / (in_max - in_min)) * (out_max - out_min)

        self.skilled_worker_ratio = linear_map(self.lvl, 1, 10, 0.05, 0.25)

        self.max_employment = 100 + (self.lvl - 1) * 50

    def max_employ(self):
        self.employees = self.max_employment

    def employ(self, employees):
        self.employees = min(self.employees + employees, self.max_employment)


    def pay(self, wage):
        self.wage = wage
        self.skilled_cost = self.wage * (self.employees * self.skilled_worker_ratio) * 1.3
        self.unskilled_cost = self.wage * (self.employees * (1 - self.skilled_worker_ratio))
        self.upkeep = self.lvl * 70 + self.upkeep_mod
        self.expenses = self.skilled_cost + self.unskilled_cost + self.upkeep
        return self.expenses
    
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
            if self.image:
                surface.blit(self.image, self.rect)


    def produce(self):
        # Scale factor based on workforce and productivity
        scale = max(1, self.employees) * self.productivity
        self.req_resources = []  # reset each cycle

        # Check if enough inputs are available
        for resource, required_amount in self.input_resources.items():
            total_required = int(required_amount * scale)
            if self.inventory.get(resource, 0) < total_required:
                print(f"Not enough {resource} to produce {self.type}.")
                return False
            # record demand (skip wood/cotton if you want)
            if resource.lower() not in ["wood", "cotton"]:
                self.req_resources.append((resource, total_required))

        # Deduct scaled input resources
        for resource, required_amount in self.input_resources.items():
            total_required = int(required_amount * scale)
            self.inventory[resource] -= total_required

        # Add scaled output
        output_resource, base_output = list(self.output_product.items())[0]
        production_amount = int(base_output * scale)
        self.last_output = production_amount
        self.inventory[output_resource] = self.inventory.get(output_resource, 0) + production_amount

        print(
            f"Produced {production_amount} {output_resource} in {self.type} factory "
            f"using {', '.join([f'{amt} {res}' for res, amt in self.req_resources])}."
        )
        return self.last_output
