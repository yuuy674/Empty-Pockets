import pygame, sys
from tile import Tile
from button import Button
from factory import Factory
from mine import Mine
from connection import Connection
from port import Port
from portconnection import PortConnection
import json
import subprocess

pygame.init()

# --- Error system ---
error_font = pygame.font.SysFont(None, 32)
error_msg = ""
error_time = 0


def show_error(message):
    global error_msg, error_time
    error_msg = message
    error_time = pygame.time.get_ticks()


def clear_error():
    global error_msg, error_time
    error_msg = ""
    error_time = 0


# Config
HEIGHT, WIDTH, TILE_SIZE = 730, 1000, 40
SEA_ROW = 17
GRID_COLS, GRID_ROWS = WIDTH // TILE_SIZE, HEIGHT // TILE_SIZE
TICK_MS = 1000
PORT_TILE = (12, SEA_ROW - 2)
LEVEL = 1

# Image assets
construct_btn_img = pygame.image.load("images/CONSTRUCT.png"); construct_btn_img = pygame.transform.scale(construct_btn_img, (TILE_SIZE * 2, TILE_SIZE * 2))
mine_btn_img      = pygame.image.load("images/MINE.png");      mine_btn_img      = pygame.transform.scale(mine_btn_img, (TILE_SIZE * 2, TILE_SIZE * 2))
factory_btn_img   = pygame.image.load("images/FACTORY.png");   factory_btn_img   = pygame.transform.scale(factory_btn_img, (TILE_SIZE * 2, TILE_SIZE * 2))
textile_button_img= pygame.image.load("images/TEXTILE_BUTTON.png");   textile_button_img  = pygame.transform.scale(textile_button_img, (TILE_SIZE, TILE_SIZE))
furniture_button_img= pygame.image.load("images/FURNITURE_BUTTON.png"); furniture_button_img= pygame.transform.scale(furniture_button_img, (TILE_SIZE, TILE_SIZE))
steel_button_img  = pygame.image.load("images/STEEL_BUTTON.png"); steel_button_img = pygame.transform.scale(steel_button_img, (TILE_SIZE, TILE_SIZE))
food_button_img   = pygame.image.load("images/FOOD_BUTTON.png");  food_button_img  = pygame.transform.scale(food_button_img, (TILE_SIZE, TILE_SIZE))
tools_button_img  = pygame.image.load("images/TOOLS_BUTTON.png"); tools_button_img = pygame.transform.scale(tools_button_img, (TILE_SIZE, TILE_SIZE))
coal_button_img   = pygame.image.load("images/COAL_BUTTON.png");  coal_button_img  = pygame.transform.scale(coal_button_img, (TILE_SIZE, TILE_SIZE))
iron_button_img   = pygame.image.load("images/IRON_BUTTON.png");  iron_button_img  = pygame.transform.scale(iron_button_img, (TILE_SIZE, TILE_SIZE))
delete_btn_img = pygame.image.load("images/DELETE_BUTTON.png"); delete_btn_img = pygame.transform.scale(delete_btn_img, (TILE_SIZE * 2, TILE_SIZE * 2))
connect_btn_img = pygame.image.load("images/CONNECT_BUTTON.png"); connect_btn_img = pygame.transform.scale(connect_btn_img, (TILE_SIZE * 2, TILE_SIZE * 2))
save_btn_img = pygame.image.load("images/SAVE_BUTTON.png"); save_btn_img = pygame.transform.scale(save_btn_img, (TILE_SIZE * 2, TILE_SIZE * 2))
normal_mode_btn_img = pygame.image.load("images/NORMAL_BUTTON.png"); normal_mode_btn_img = pygame.transform.scale(normal_mode_btn_img, (TILE_SIZE * 2, TILE_SIZE * 2))


# Economy
wage =  5
UPGRADE_COST = 2000
factory_costs = {"TEXTILE": 3000, "FURNITURE": 3000, "STEEL": 7000, "FOOD": 5000, "TOOLS": 4000}
mine_costs = {"IRON": 2000, "COAL": 2000}

# Recipes
RECIPES = {
    "TEXTILE":   {"needs": {"cotton": 2},           "makes": {"textile": 1}},
    "FURNITURE": {"needs": {"wood": 2, "tools": 1}, "makes": {"furniture": 1}},
    "STEEL":     {"needs": {"iron": 1, "coal": 1},  "makes": {"steel": 1}},
    "FOOD":      {"needs": {"tools": 1},            "makes": {"food": 1}},
    "TOOLS":     {"needs": {"wood": 2},             "makes": {"tools": 1}},
    "IRON":      {"needs": {"tools": 2},            "makes": {"iron": 1}},
    "COAL":      {"needs": {"tools": 2},            "makes": {"coal": 1}},
}


# Colors
COL = {
    "SEA": (0, 0, 255), "PORT": (38, 71, 58),
    "TEXTILE": (200, 200, 200), "FURNITURE": (150, 75, 0), "STEEL": (100, 100, 100),
    "FOOD": (34, 139, 34), "TOOLS": (255, 255, 0), "IRON": (255, 255, 255), "COAL": (0, 0, 0),
    "BTN_BROWN": (139, 69, 19), "BTN_RED": (255, 0, 0), "BTN_ORANGE": (255, 165, 0), "BTN_BLACK": (0, 0, 0),
    "POPUP_BG": (50, 50, 50), "POPUP_TEXT": (255, 255, 255), "UPGRADE_BTN": (0, 255, 255),
    "TOOLTIP_BG": (40, 40, 60), "TOOLTIP_BORDER": (200, 200, 200)
}

# UI
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Industry Simulation")
font = pygame.font.SysFont(None, 24)
popup_font = pygame.font.SysFont(None, 16)

# Grid + restricted tiles
tiles = {(x, y): Tile(x, y, TILE_SIZE) for y in range(GRID_ROWS) for x in range(GRID_COLS)}
restricted_tiles = {PORT_TILE} | {(x, y) for x in range(GRID_COLS) for y in range(SEA_ROW - 1, GRID_ROWS)}

# Game state
construct_mode = False
connect_mode = False
delete_mode = False
show_mine_buttons = False
show_factory_buttons = False
track_click_build_factory = False
track_click_build_mine = False
type_to_build = None
selected_building = None
last_tick = pygame.time.get_ticks()

# Popup state
popup_building = None
popup_rect = None
upgrade_btn_rect = None

# Port
port = Port()
port.set_position(PORT_TILE, TILE_SIZE, COL["PORT"])

# Helpers
def get_current_mode():
    if construct_mode:
        return "Mode: Construct"
    elif connect_mode:
        return "Mode: Connect"
    elif delete_mode:
        return "Mode: Delete"
    else:
        return "Mode: Normal"


def get_building_at(pos):
    return next((b for b in factories + mines if b.position == pos), None)


def remove_port_connection(b):
    global port_connections
    port_connections[:] = [pc for pc in port_connections if pc.producer is not b]


def clicked_on_any_button(pos):
    return any(btn.rect.collidepoint(pos) for btn in all_buttons)


def reset_selection():
    global selected_building
    selected_building = None


def clear_popup():
    global popup_building, popup_rect, upgrade_btn_rect
    popup_building = None
    popup_rect = None
    upgrade_btn_rect = None


def show_popup_for(b):
    global popup_building, popup_rect, upgrade_btn_rect
    popup_building = b
    bx, by = b.position
    px, py = bx * TILE_SIZE, by * TILE_SIZE
    pr_w, pr_h = TILE_SIZE * 4, TILE_SIZE * 4
    pr_x = px + TILE_SIZE if px + TILE_SIZE + pr_w <= WIDTH else max(0, px - pr_w)
    pr_y = py if py + pr_h <= HEIGHT else max(0, py - pr_h)
    popup_rect = pygame.Rect(pr_x, pr_y, pr_w, pr_h)
    upgrade_btn_rect = pygame.Rect(popup_rect.right - TILE_SIZE, popup_rect.bottom - TILE_SIZE, TILE_SIZE, TILE_SIZE)


def init_building_metrics(b):
    b.last_revenue = 0
    b.last_expenses = 0
    b.last_output = 0


def place_building(pos, is_factory=True):
    global money, total_employees, tutorial_step
    if pos in restricted_tiles:
        show_error("Cannot build here")
        return

    if get_building_at(pos) is not None:
        show_error("Tile already occupied")
        return

    costs = factory_costs if is_factory else mine_costs
    if type_to_build not in costs:
        show_error("No type selected")
        return
    if money < costs[type_to_build]:
        show_error(f"Not enough money for {type_to_build}!")
        return

    cls = Factory if is_factory else Mine
    b = cls(type_to_build)
    b.set_position(pos, TILE_SIZE, COL[type_to_build])
    b.max_employ()
    init_building_metrics(b)
    (factories if is_factory else mines).append(b)
    money -= costs[type_to_build]
    total_employees += 100

    # Tutorial Step 1 -> 2: placed TOOLS factory
    if tutorial_step == 1 and is_factory and type_to_build == "TOOLS":
        tutorial_step = 2
        show_tutorial("Great!\nNow in NORMAL MODE:\nClick your TOOLS factory,\nthen click the PORT to connect it.")


def remove_building(b):
    global factories, mines, connections, port_connections, total_employees
    if b in factories:
        factories.remove(b)
    elif b in mines:
        mines.remove(b)
    connections[:] = [
        c for c in connections
        if c.producer is not b and c.consumer is not b
    ]

    port_connections[:] = [pc for pc in port_connections if getattr(pc, "producer", None) is not b]
    total_employees = max(0, total_employees - getattr(b, "employees", 100))


def find_connection(a, b):
    return next((c for c in connections if (getattr(c, "a", None) is a and getattr(c, "b", None) is b) or (getattr(c, "a", None) is b and getattr(c, "b", None) is a)), None)


def remove_connection(a, b):
    global connections
    c = find_connection(a, b)
    if c:
        connections.remove(c)
        return True
    return False


# Load Save
with open("savegame.json", "r") as f:
    contents = f.read().strip()

if contents == "" or contents == "{}":
    s = {}
else:
    s = json.loads(contents)


factories, mines, connections, port_connections = [], [], [], []
money = s.get("money", 10000)
tutorial = s.get("tutorial", True)  # default True so tutorial runs if missing
total_employees = 0

for data in s.get("factories", []):
    f_obj = Factory(data["type"])
    pos = tuple(data.get("position", (0, 0)))
    f_obj.set_position(pos, TILE_SIZE, (0, 0, 0))
    f_obj.lvl = data.get("lvl", 1)
    f_obj.update_lvl(0)
    factories.append(f_obj)
    total_employees += f_obj.max_employment

for data in s.get("mines", []):
    m_obj = Mine(data["type"])
    pos = tuple(data.get("position", (0, 0)))
    m_obj.set_position(pos, TILE_SIZE, (0, 0, 0))
    m_obj.lvl = data.get("lvl", 1)
    m_obj.update_lvl(0)
    mines.append(m_obj)
    total_employees += m_obj.max_employment

for data in s.get("connections", []):
    a = get_building_at(tuple(data["producer"]))
    b = get_building_at(tuple(data["consumer"]))
    if a and b:
        connections.append(Connection(a, b, data.get("capacity", 50)))

for data in s.get("port_connections", []):
    producer = get_building_at(tuple(data["producer"]))
    if producer:
        port_connections.append(PortConnection(producer, port, data.get("capacity", 50)))

LEVEL = s.get("level", 1)

# Tutorial state
tutorial_step = 1 if tutorial else 0
tutorial_popup = ""


# Menu actions / tutorial popup
def show_tutorial(text):
    global tutorial_popup
    tutorial_popup = text


def toggle_construct():
    global construct_mode, connect_mode, delete_mode, show_mine_buttons, show_factory_buttons
    construct_mode = not construct_mode
    connect_mode = False
    delete_mode = False
    show_mine_buttons = False
    show_factory_buttons = False
    reset_selection()
    clear_popup()


def toggle_mine_menu():
    global show_mine_buttons, show_factory_buttons
    show_mine_buttons = not show_mine_buttons
    show_factory_buttons = False
    reset_selection()
    clear_popup()


def toggle_factory_menu():
    global show_factory_buttons, show_mine_buttons
    show_factory_buttons = not show_factory_buttons
    show_mine_buttons = False
    reset_selection()
    clear_popup()


def toggle_connect():
    global connect_mode, delete_mode, construct_mode
    connect_mode = not connect_mode
    delete_mode = False
    construct_mode = False
    reset_selection()
    clear_popup()


def toggle_delete():
    global delete_mode, connect_mode, construct_mode, show_mine_buttons, show_factory_buttons
    delete_mode = not delete_mode
    connect_mode = False
    construct_mode = False
    show_mine_buttons = False
    show_factory_buttons = False
    reset_selection()
    clear_popup()


def build_factory(ft):
    global track_click_build_factory, type_to_build
    track_click_build_factory = True
    type_to_build = ft
    reset_selection()
    clear_popup()


def build_mine(mt):
    global track_click_build_mine, type_to_build
    track_click_build_mine = True
    type_to_build = mt
    reset_selection()
    clear_popup()


def save_game():
    global tutorial_step
    tut = True
    # Tutorial Step 5: saving
    if tutorial_step == 5:
        tutorial_step = 0
        show_tutorial("")
        show_error("Tutorial complete!")
        tut = False
    data = {
        "factories": [
            {"type": f.type, "position": f.position, "lvl": f.lvl}
            for f in factories
        ],
        "mines": [
            {"type": m.type, "position": m.position, "lvl": m.lvl}
            for m in mines
        ],
        "connections": [
            {"producer": c.producer.position, "consumer": c.consumer.position, "capacity": c.capacity}
            for c in connections
        ],
        "port_connections": [
            {"producer": pc.producer.position, "capacity": pc.capacity}
            for pc in port_connections
        ],
        "level": LEVEL,
        "money": money,
        "tutorial": tut
    }
    with open("savegame.json", "w") as f:
        json.dump(data, f, indent=4)
    show_error("Game saved!")

def enter_normal_mode():
    global construct_mode, connect_mode, delete_mode
    global show_mine_buttons, show_factory_buttons
    global track_click_build_factory, track_click_build_mine
    global selected_building

    construct_mode = False
    connect_mode = False
    delete_mode = False

    show_mine_buttons = False
    show_factory_buttons = False

    track_click_build_factory = False
    track_click_build_mine = False

    selected_building = None
    clear_popup()


# Buttons
construct_btn = Button((23, 16), (24, 17), TILE_SIZE, COL["BTN_BROWN"], construct_btn_img, toggle_construct)
mine_btn      = Button((21, 16), (22, 17), TILE_SIZE, COL["BTN_RED"],   mine_btn_img,      toggle_mine_menu)
factory_btn   = Button((19, 16), (20, 17), TILE_SIZE, COL["BTN_ORANGE"], factory_btn_img,  toggle_factory_menu)
connect_btn   = Button((14, 16), (15, 17), TILE_SIZE, COL["BTN_BLACK"], connect_btn_img,              toggle_connect)
delete_btn    = Button((0, 16),  (1, 17),  TILE_SIZE, COL["BTN_RED"],   delete_btn_img,    toggle_delete)
save_btn      = Button((2, 16),  (3, 17),  TILE_SIZE, (0, 200, 0),      save_btn_img,      save_game)
normal_mode_btn = Button((4, 16),  (5, 17),  TILE_SIZE, (200, 200, 200),      normal_mode_btn_img, enter_normal_mode)

mine_buttons = [
    Button((17, 16), (18, 16), TILE_SIZE, COL["IRON"], iron_button_img, lambda: build_mine("IRON")),
    Button((17, 17), (18, 17), TILE_SIZE, COL["COAL"], coal_button_img, lambda: build_mine("COAL"))
]
factory_buttons = [
    Button((17, 17), (17, 17), TILE_SIZE, COL["TEXTILE"],   textile_button_img,   lambda: build_factory("TEXTILE")),
    Button((18, 17), (18, 17), TILE_SIZE, COL["FURNITURE"], furniture_button_img, lambda: build_factory("FURNITURE")),
    Button((17, 16), (17, 16), TILE_SIZE, COL["STEEL"],     steel_button_img,     lambda: build_factory("STEEL")),
    Button((18, 16), (18, 16), TILE_SIZE, COL["FOOD"],      food_button_img,      lambda: build_factory("FOOD")),
    Button((16, 16), (16, 16), TILE_SIZE, COL["TOOLS"],     tools_button_img,     lambda: build_factory("TOOLS"))
]

# Attach btype for tooltips
mine_buttons[0].btype = "IRON"; mine_buttons[1].btype = "COAL"
factory_buttons[0].btype = "TEXTILE"; factory_buttons[1].btype = "FURNITURE"
factory_buttons[2].btype = "STEEL";   factory_buttons[3].btype = "FOOD"; factory_buttons[4].btype = "TOOLS"

all_buttons = [normal_mode_btn, save_btn, connect_btn, construct_btn, mine_btn, factory_btn, delete_btn] + mine_buttons + factory_buttons


def draw_recipe_tooltip(btn):
    btype = getattr(btn, "btype", None)
    if not btype or btype not in RECIPES:
        return
    recipe = RECIPES[btype]
    lines = [f"{btype}", "Needs:"]
    if recipe["needs"]:
        for res in recipe["needs"]:
            lines.append(f"- {res}")
    else:
        lines.append("- none")
    lines.append("Makes:")
    for res in recipe["makes"]:
        lines.append(f"- {res}")

    w = max(popup_font.size(line)[0] for line in lines) + 12
    h = 6 + len(lines) * 14
    rect = pygame.Rect(btn.rect.right + 6, btn.rect.top, w, h)
    if rect.right > WIDTH:
        rect.x = btn.rect.left - w - 6
    if rect.bottom > HEIGHT:
        rect.y = max(0, HEIGHT - h - 6)

    pygame.draw.rect(screen, COL["TOOLTIP_BG"], rect, border_radius=6)
    pygame.draw.rect(screen, COL["TOOLTIP_BORDER"], rect, width=1, border_radius=6)
    y = rect.y + 6
    for line in lines:
        screen.blit(popup_font.render(line, True, COL["POPUP_TEXT"]), (rect.x + 6, y))
        y += 14


# Main loop
running = True

# Welcome message
welcome_font = pygame.font.SysFont(None, 36)
welcome_text = (
    " Historical context: Pittsburgh was a known for being an industrial"
    "\n hub that produced lots of steel."
    "\n however, during the Great Depression, many factories were "
    "\nshut down and people lost their jobs."
    "\n in 1932 Frankkin D. Roosevelt was elected president and created"
    "\n New Deal programs to help"
    "\n You work in one of these programs."
    "\n Your job is to hire at least 15,000 workers and build "
    "\n at least 3 steel factories."
    "\n Dont go below 10,000 dollars in debt or you will go bankrupt!"
)
lines = welcome_text.split("\n")
screen.fill((0, 0, 0))
y = HEIGHT // 2 - 40
for line in lines:
    surf = welcome_font.render(line, True, (255, 255, 0))
    screen.blit(surf, (WIDTH // 2 - surf.get_width() // 2, y))
    y += 40
pygame.display.flip()
pygame.time.delay(15000)

# Initial tutorial text
if tutorial_step == 1:
    show_tutorial("Tutorial Step 1:\nPlace a TOOLS factory.")

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        # Button clicks
        for btn in all_buttons:
            btn.is_clicked(event)

        # Upgrade click
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1 and popup_building and upgrade_btn_rect:
            if upgrade_btn_rect.collidepoint(event.pos):
                current_lvl = int(getattr(popup_building, "lvl", 1))
                if current_lvl >= 10:
                    show_error("Max level reached (10)")
                elif money >= UPGRADE_COST:
                    popup_building.update_lvl(1)      
                    print("UPGRADE DEBUG:", popup_building.type, popup_building.lvl)
                    money -= UPGRADE_COST
                    total_employees += 50
                    show_popup_for(popup_building)
                        
                else:
                    show_error(f"Not enough money to upgrade! Need ${UPGRADE_COST}, have ${money}")
                continue

        # Grid interactions
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1 and not clicked_on_any_button(event.pos):
            pos = (event.pos[0] // TILE_SIZE, event.pos[1] // TILE_SIZE)
            b = get_building_at(pos)

            # Placement
            if track_click_build_factory:
                place_building(pos, True)
                track_click_build_factory = False
                clear_popup()
                continue
            if track_click_build_mine:
                place_building(pos, False)
                track_click_build_mine = False
                clear_popup()
                continue

            # Delete mode
            if delete_mode:
                if b and not selected_building:
                    remove_building(b); reset_selection(); clear_popup()
                elif selected_building and b and selected_building is not b:
                    if not remove_connection(selected_building, b): show_error("No connection to delete")
                    reset_selection(); clear_popup()
                elif selected_building and pos == PORT_TILE:
                    remove_port_connection(selected_building); reset_selection(); clear_popup()
                else:
                    if b and not selected_building:
                        selected_building = b
                continue

            # Connect mode (building to building)
            if connect_mode:
                if not b:
                    reset_selection()
                else:
                    if not selected_building:
                        selected_building = b
                    else:
                        if selected_building is not b:
                            try:
                                c = Connection(selected_building, b, 50)
                                connections.append(c)

                                # Tutorial Step 4: TOOLS -> IRON
                                if tutorial_step == 4:
                                    if getattr(selected_building, "type", "") == "TOOLS" and getattr(b, "type", "") == "IRON":
                                        tutorial_step = 4.5
                                        show_tutorial("Great!\nNow in NORMAL MODE:\nConnect the IRON mine to the PORT.")
                            except Exception:
                                show_error("Failed to connect")
                        reset_selection()
                clear_popup()
                continue

            # Producer to port (normal mode)
            if selected_building and pos == PORT_TILE:
                try:
                    pc = PortConnection(selected_building, port, capacity=50)
                    port_connections.append(pc)
        
                except Exception:
                    show_error("Failed to connect to port")

                reset_selection()
                clear_popup()
                continue

            # Normal selection / popup
            if b and not selected_building:
                selected_building = b
                show_popup_for(b)
            elif not b and pos != PORT_TILE:
                reset_selection()
                clear_popup()
            else:
                if b: show_popup_for(b)

    # Tick
    now = pygame.time.get_ticks()
    if now - last_tick >= TICK_MS:
        last_tick = now

        for m in mines:
            try:
                produced = m.produce()
                m.last_output = produced if produced else 0
                m.employ(10)
                expenses = m.pay(wage)
                money -= expenses
                m.last_expenses = int(expenses); m.last_revenue = 0
            except Exception:
                print("Mine error")

        for f in factories:
            try:
                produced = f.produce()
                f.last_output = produced if produced else 0
                f.employ(10)
                expenses = f.pay(wage)
                money -= expenses
                f.last_expenses = int(expenses); f.last_revenue = 0
            except Exception:
                print("Factory error")

        for pc in port_connections:
            try:
                earned = pc.transfer()
                if earned and earned > 0:
                    money += earned
                    pc.producer.last_revenue = int(earned)
            except Exception:
                show_error("Port transfer error")

        for c in connections:
            try:
                c.transfer()
            except Exception as e:
                print ("TRANSFER ERROR DEBUG:", e)
                show_error("Connection transfer error")

    # Auto-clear error
    if error_msg and pygame.time.get_ticks() - error_time > 1000:
        clear_error()

    # Draw grid
    for tile in tiles.values():
        tile.draw(screen)

    # Sea rows
    for i in range(GRID_COLS):
        tiles[(i, SEA_ROW)].color = COL["SEA"]
        tiles[(i, SEA_ROW - 1)].color = COL["SEA"]

    # Visibility logic for build menus
    if construct_mode:
        mine_btn.show()
        factory_btn.show()
        for b in mine_buttons:
            b.show() if show_mine_buttons else b.hide()
        for b in factory_buttons:
            b.show() if show_factory_buttons else b.hide()
    else:
        mine_btn.hide()
        factory_btn.hide()
        for b in mine_buttons:
            b.hide()
        for b in factory_buttons:
            b.hide()

    # Draw buttons
    for btn in all_buttons:
        btn.draw(screen)

    # Hover tooltips
    mouse_pos = pygame.mouse.get_pos()
    if show_mine_buttons:
        for btn in mine_buttons:
            if btn.rect.collidepoint(mouse_pos):
                draw_recipe_tooltip(btn)
    if show_factory_buttons:
        for btn in factory_buttons:
            if btn.rect.collidepoint(mouse_pos):
                draw_recipe_tooltip(btn)

    # Draw buildings and links
    for f in factories:
        f.draw(screen)
    for m in mines:
        m.draw(screen)
    for c in connections:
        try:
            c.draw(screen)
        except TypeError:
            c.draw(screen, TILE_SIZE)
    for pc in port_connections:
        try:
            pc.draw(screen)
        except TypeError:
            pc.draw(screen, TILE_SIZE)
    port.draw(screen)

    # Popup
    if popup_building and popup_rect:
        pygame.draw.rect(screen, COL["POPUP_BG"], popup_rect)
        revenue = int(getattr(popup_building, "last_revenue", 0))
        expenses = int(getattr(popup_building, "last_expenses", 0))
        profit = revenue - expenses
        output = int(getattr(popup_building, "last_output", 0))
        lines = [
            f"Type: {getattr(popup_building,'type','')}",
            f"Lvl: {int(getattr(popup_building,'lvl',1))}",
            f"Employment: {int(getattr(popup_building,'employees',0))}",
            f"Productivity: {getattr(popup_building,'productivity',0)}",
            f"Output: {output} units/sec",
            f"Revenue: ${revenue}",
            f"Expenses: ${expenses}",
            f"Profit: ${profit}"
        ]
        for r in getattr(popup_building, "req_resources", []):
            res, amt = r
            lines.append(f"Needs {amt} {res} per cycle")

        x = popup_rect.x + 6; y = popup_rect.y + 6
        for line in lines:
            screen.blit(popup_font.render(line, True, COL["POPUP_TEXT"]), (x, y))
            y += 13

        if upgrade_btn_rect:
            pygame.draw.rect(screen, COL["UPGRADE_BTN"], upgrade_btn_rect)
            screen.blit(popup_font.render("UP", True, (0, 0, 0)), (upgrade_btn_rect.x + 6, upgrade_btn_rect.y + 6))

    # HUD
    screen.blit(pygame.font.SysFont(None, 36).render(f"Money: ${int(money)}", True, (255, 255, 255)), (10, 10))
    screen.blit(pygame.font.SysFont(None, 24).render(f"Total Employees: {total_employees}", True, (255, 255, 255)), (10, 50))

    # Error
    if error_msg:
        screen.blit(error_font.render(error_msg, True, (255, 0, 0)), (WIDTH // 2 - 150, 400))

    # Mode
    mode_text = get_current_mode()
    mode_surface = pygame.font.SysFont(None, 36).render(mode_text, True, (225, 255, 255))
    screen.blit(mode_surface, (WIDTH // 2 - mode_surface.get_width() // 2, 10))

    # Tutorial popup
    if tutorial_step > 0 and tutorial_popup:
        rect = pygame.Rect(100, 100, WIDTH - 200, 220)
        pygame.draw.rect(screen, (20, 20, 20), rect)
        pygame.draw.rect(screen, (255, 255, 0), rect, 3)
        lines = tutorial_popup.split("\n")
        y = rect.y + 15
        for line in lines:
            surf = font.render(line, True, (255, 255, 0))
            screen.blit(surf, (rect.x + 15, y))
            y += 30

    # Tutorial step 2: any building connected to port
    if tutorial_step == 2 and len(port_connections) > 0:
        tutorial_step = 3
        show_tutorial("Good!\nNow upgrade your TOOLS factory\nby clicking it then clicking its UP button in the popup.")

    # Tutorial step 4.5
    if tutorial_step == 4.5:
        up1 = False
        up2 = False
        for p in port_connections:
            producer = getattr(p, "producer", None)
            if producer and getattr(producer, "type", "") == "iron":
                up1 = True
                break
        for i in connections:
            producer = getattr(i, "producer", None)
            consumer = getattr(i, "consumer", None)

            if producer.type == "tools" and consumer.type == "iron":
                up2 = True
        if up1 and up2:
            tutorial_step = 5
            show_tutorial("Great!\nNow click the save button\n And remember theres also the delete button in case you want to delete a building")

    for b in factories:
        if tutorial_step == 3 and b.type == "tools" and b.lvl > 1:
            tutorial_step = 4
            show_tutorial("Good!\nNow in CONSTRUCT MODE:\nBuild an IRON mine.")

    for m in mines:
        if tutorial_step == 4 and m.type == "iron":
            tutorial_step = 4.5
            show_tutorial("Great!\nNow in CONNECT MODE:\nConnect the Tool factory to the IRON mine. \n By pressing the connect button then tool factory then iron mine \n then in Normal mode connect it to the port")

    # Lose logic
    if money < -10000:
        show_error("You lost! You ran out of money.")

        #force screen update so player sees the message
        screen.fill((0, 0, 0))
        screen.blit(error_font.render(error_msg, True, (255,0,0)), (WIDTH//2 - 150, 400))
        pygame.display.flip()

        pygame.time.delay(2000)

        with open("savegame.json", "w") as f:
            json.dump({}, f)
        pygame.time.delay(2000)
        running = False

    # Win logic
    if total_employees >= 15000 and len([f for f in factories if f.type == "steel"]) >= 3:
        show_error("You won! You built enough steel""\n factories and employed enough people.")

        #force screen update so player sees the message
        screen.fill((0, 0, 0))
        screen.blit(error_font.render(error_msg, True, (255,0,0)), (WIDTH//2 - 150, 400))
        pygame.display.flip()

        pygame.time.delay(2000)
        with open("savegame.json", "w") as f:
            json.dump({}, f)
        pygame.time.delay(2000)
        subprocess.run(["python", "san_diego.py"])
        running = False

    pygame.display.flip()

pygame.quit()
sys.exit()
