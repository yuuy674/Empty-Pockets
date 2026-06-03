import json
import pittsburg
import san_diego
import pygame

# -- Find level and tutorial --
start = 0
tutorial = True
with open("savegame.json", "r+") as f:
    contents = f.read().strip()
    #If there is nothing in json file start is 0
    if contents == "" or contents == "{}":
        start = 0
    else:
        # Load JSON once to prevent repetitive decoding errors
        data = json.loads(contents)
        level = data.get("level", 1)
        tutorial = data.get("tutorial", True)
        
    if level == 1:
        if tutorial == True:
            #start is 0 if the tutorial and level 1 are not done
            start = 0
        else:
            #start is 1 if the tutorial is done but not level 1
            start = 1
    elif level == 2:
        #start is 2 if if level 1 and tutorial is done
        start = 2

# Variables
WIDTH, HEIGHT = 800, 600
running = True
screen = pygame.display.set_mode((WIDTH, HEIGHT))
FINISHED, UNFINISHED = (0, 225, 0), (225, 0, 0)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (200, 200, 200) # Added color for the rectangle button

# Make Font System
pygame.font.init()
font = pygame.font.SysFont("Arial", 24)

# Create a Pygame Rect for the button (X, Y, Width, Height)
play_button_rect = pygame.Rect(325, 480, 150, 50)

# Main game loop
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
            
        # Check for mouse clicks inside the event loop
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1: # Left click
                # Check if the mouse click position was inside our rectangle
                if play_button_rect.collidepoint(event.pos):
                    if start == 0 or start == 1:
                        pittsburg.run_game()
                    elif start == 2:
                        san_diego.run_game()

    # Clear the screen with a white background
    screen.fill(WHITE)

    # Determine colors for the 3 circles based on the start variable
    circle1_color = FINISHED if start > 0 else UNFINISHED
    circle2_color = FINISHED if start > 1 else UNFINISHED
    circle3_color = FINISHED if start > 2 else UNFINISHED

    # Draw the 3 circles 
    pygame.draw.circle(screen, circle1_color, (200, 300), 40)
    pygame.draw.circle(screen, circle2_color, (400, 300), 40)
    pygame.draw.circle(screen, circle3_color, (600, 300), 40)

    # --- Render Text Labels ---
    text1 = font.render("Tutorial", True, BLACK)
    text2 = font.render("Level 1", True, BLACK)
    text3 = font.render("Level 2", True, BLACK)

    screen.blit(text1, text1.get_rect(center=(200, 360)))
    screen.blit(text2, text2.get_rect(center=(400, 360)))
    screen.blit(text3, text3.get_rect(center=(600, 360)))

    # --- Draw Rectangle Button and Text ---
    # Draw the gray rectangle background
    pygame.draw.rect(screen, GRAY, play_button_rect)
    # Optional: Draw a thin black border around the button
    pygame.draw.rect(screen, BLACK, play_button_rect, 2) 

    # Center the PLAY text directly inside the rectangle
    play_text = font.render("PLAY", True, BLACK)
    screen.blit(play_text, play_text.get_rect(center=play_button_rect.center))

    # Refresh the display window
    pygame.display.flip()

pygame.quit()
