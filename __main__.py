import pygame, sys
from button import Button
import json
import subprocess

# --- Game Constants ---
WIDTH, HEIGHT = 800, 600
TITLE = "Empty Pockets"
TILE_SIZE = 40  

# --- Pygame Initialization ---
pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption(TITLE)
clock = pygame.time.Clock()
running = True

# --- Background ---
title_image = pygame.image.load("images/TITLE_SCREEN.gif")
title_image = pygame.transform.scale(title_image, (WIDTH, HEIGHT))

#--- Play Function ---
data = { "factories": [], "mines": [], "connections": [], "port_connections": [], "level": 1, "tutorial": True}
def start_game():
    global running
    with open("savegame.json", "r+") as f:
        contents = f.read().strip()
        if contents != "":
            level = json.loads(contents)["level"]
        else:
            level = None
        if contents == "":
            json.dump(data, f, indent=4)
            subprocess.Popen([sys.executable, "./pittsburg.py"])
            running = False
        if level == 1:
            subprocess.Popen([sys.executable, "./pittsburg.py"])
            running = False
        if level == 2:
            subprocess.Popen([sys.executable, "./san_diego.py"])
            running = False

# --- Play Button ---
play_button = Button(
    top_left_tile=(7, 12),
    bottom_right_tile=(11, 13),  # spans 5 tiles wide, 2 tiles tall
    tile_size=TILE_SIZE,
    color=(0, 255, 0),
    image=None,
    on_click_function=start_game
)

# --- Main loop ---
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit(); sys.exit()
        play_button.is_clicked(event)

    # Draw background first
    screen.blit(title_image, (0, 0))

    # Draw Play button on top
    play_button.draw(screen)

    pygame.display.flip()
    clock.tick(60)
