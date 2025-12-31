import pygame

class Connection:
    def __init__(self, producer, consumer, capacity):
        
        #producer: Factory or Mine object that produces resources
        #consumer: Factory object that consumes resources
        #amount: how much resource to transfer per tick
        
        self.producer = producer
        self.consumer = consumer
        self.capacity = capacity
        self.building_a = producer
        self.building_b = consumer
        self.amount = capacity

        # Determine which resource is produced
        if not producer.output_product:
            self.active = False
            raise ValueError(f"{producer.type} has no output_product defined")

        # For simplicity assume one output resource per producer
        self.resource = list(producer.output_product.keys())[0]

        # Validate that consumer requires this resource
        if self.resource not in consumer.input_resources:
            raise ValueError(f"{consumer.type} does not require {self.resource}")

    def transfer(self):
        # Move resources from producer.inventory to consumer.inventory.
        available = self.producer.inventory.get(self.resource, 0)
        if available <= 0:
            print(f"{self.producer.type} has no {self.resource} to transfer.")
            return

        # Scale transfer by producer's level or productivity
        lvl = getattr(self.producer, "lvl", 1)
        productivity = getattr(self.producer, "productivity", 1)

        # Decide how much to transfer: base amount * level * productivity
        dynamic_amount = self.amount * lvl * productivity

        transfer_amount = min(dynamic_amount, available)

        # Deduct from producer
        self.producer.inventory[self.resource] = available - transfer_amount

        # Add to consumer
        self.consumer.inventory[self.resource] = (
            self.consumer.inventory.get(self.resource, 0) + transfer_amount
        )

        print(f"Transferred {transfer_amount} {self.resource} "
            f"from {self.producer.type} to {self.consumer.type}")

        
    def draw(self, surface, tile_size=40, color=(0,0,0)):
        if not self.building_a.position or not self.building_b.position:
            return

        # Convert grid positions to pixel centers
        ax, ay = self.building_a.position
        bx, by = self.building_b.position

        a_px = (ax * tile_size + tile_size // 2, ay * tile_size + tile_size // 2)
        b_px = (bx * tile_size + tile_size // 2, by * tile_size + tile_size // 2)

        # Draw a very thin line (width=1)
        pygame.draw.line(surface, color, a_px, b_px, 1)
