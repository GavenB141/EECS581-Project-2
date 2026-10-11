#gui.py

import pygame as pg
from defs import *
from backend import *
from ai import *
from pathlib import Path
from settings import GameSettings

SCALE = 4
SCREEN_WIDTH = 192 # ten 16px tiles + four 8px tiles = 192
SCREEN_HEIGHT = 232 # ten 16px tiles + nine 8px tiles = 232

# top-left position to draw the start screen panel in center of screen
PANEL_X = (SCREEN_WIDTH - 176) // 2
PANEL_Y = (SCREEN_HEIGHT - 216) // 2

START_BUTTON_POS = (44, 136)
START_BUTTON_SIZE = (88, 24)

SETTINGS_BUTTON_POS = (44, 76)
SETTINGS_BUTTON_SIZE = (88, 24)
BOARD_SIZE_OPTIONS = (8, 10, 12)
SETTINGS_PANEL_POS = (8, 10)
SETTINGS_PANEL_SIZE = (176, 211)
SETTINGS_MENU_ART_SIZE = (176, 329)
SETTINGS_MENU_PANEL_SOURCE = pg.Rect(0, 118, 176, 211)
SETTING_ARROW_SIZE = (9, 9)
MINE_UP_POS = (79, 59)
MINE_DOWN_POS = (88, 59)
BOARD_UP_POS = (79, 87)
BOARD_DOWN_POS = (88, 87)
STRENGTH_UP_POS = (79, 132)
STRENGTH_DOWN_POS = (88, 132)
MODE_UP_POS = (79, 151)
MODE_DOWN_POS = (88, 151)
MINE_COUNT_DIGITS_POS = (102, 60)
BOARD_SIZE_VALUE_POS = (102, 88)
STRENGTH_VALUE_POS = (102, 127)
MODE_VALUE_POS = (102, 146)
# The strength glyphs have different source baselines; align their visible ink.
STRENGTH_VALUE_PIXEL_OFFSETS = {"hard": 0, "medium": 5, "easy": -4}
MODE_TEXT_AREAS = {
    "none": pg.Rect(2, 29, 56, 18),
    "interactive": pg.Rect(58, 29, 61, 18),
    "auto": pg.Rect(119, 29, 55, 18),
}
SETTINGS_START_POS = (18, 171)
SETTINGS_START_SIZE = (82, 23)

# game over panel constants
GAME_OVER_SOURCE_RECT = pg.Rect(250, 814, 498, 320)
GAME_OVER_SIZE = (97, 62)

GAME_OVER_RECT = pg.Rect(
    ((SCREEN_WIDTH - GAME_OVER_SIZE[0]) // 2) * SCALE,
    (((SCREEN_HEIGHT - GAME_OVER_SIZE[1]) // 2) + 20) * SCALE,
    GAME_OVER_SIZE[0] * SCALE,
    GAME_OVER_SIZE[1] * SCALE
)

MENU_BUTTON_RELATIVE_POS = (14, 30)
MENU_BUTTON_NATIVE_SIZE = (68, 18)

MENU_BUTTON_RECT = pg.Rect(
    GAME_OVER_RECT[0] + MENU_BUTTON_RELATIVE_POS[0] * SCALE,
    GAME_OVER_RECT[1] + MENU_BUTTON_RELATIVE_POS[1] * SCALE,
    MENU_BUTTON_NATIVE_SIZE[0] * SCALE,
    MENU_BUTTON_NATIVE_SIZE[1] * SCALE
)

# game over blinking interval
GAME_OVER_BLINK_MS = 500

FACE_POS = (88, 24)

# dict for storing all sprite items
sprites = {}
screen = pg.display.set_mode((SCALE * SCREEN_WIDTH, SCALE * SCREEN_HEIGHT))

# which screen is currently active between menu or playing
game_state = "menu"

# Menu choices persist when returning from a finished game.
selected_settings = GameSettings()


def ai_turn_configuration(mode):
    if mode == "auto":
        return False, True
    if mode == "none":
        return False, False
    if mode == "interactive":
        return True, True
    raise ValueError(f"Unknown game mode: {mode}")


def scaled_rect(pos, size):
    return pg.Rect(pos[0] * SCALE, pos[1] * SCALE, size[0] * SCALE, size[1] * SCALE)


def settings_rect(pos, size):
    panel_pos = (SETTINGS_PANEL_POS[0] + pos[0], SETTINGS_PANEL_POS[1] + pos[1])
    return scaled_rect(panel_pos, size)


# Function written by John Rader
# return a pg surface scaled by SCALE
def scale_surface(surface):
    return pg.transform.scale_by(surface, SCALE)

# Function written by John Rader
# blit a given surface to screen
# should only be used to draw the tile sprites
def draw_to_tile(surface, tile_coords):
    # determine upper left corner coords of the tile at tile_coords

    # top left tile's top left coord is (16, 56)
    pixel_coords = [16 + tile_coords[0] * 16, 56 + tile_coords[1] * 16]

    # scale
    pixel_coords[0] *= SCALE
    pixel_coords[1] *= SCALE

    screen.blit(surface, pixel_coords)


# helper that returns tile coords for a given mouse position on click
# authored by: Sina Asheghalishahi
# date created: 9/18/26
def get_clicked_tile(mouse_pos):

    # convert mouse pos to tile coords
    x, y = mouse_pos

    # scale down to original size
    x //= SCALE
    y //= SCALE

    # adjust for the offset of the top left tile
    x -= 16
    y -= 56

    # if the click is outside of the board, return None
    if (x < 0 or y < 0 or x >= SCREEN_WIDTH - 32 or y >= SCREEN_HEIGHT - 72):
        return None

    # convert to tile coords
    x //= 16
    y //= 16

    # return (col, row) as a tuple
    col = x
    row = y

    return (col, row)


# load all sprites into memory (sprites dict), then scale
def init_sprites():
    # all images drawn to sprites are done so at (0,0), so they fill the entire surface
    dest = (0,0)

    # load entire sprite sheet
    sprite_sheet = pg.image.load(str(Path(__file__).parent / "assets/minesweeper_sheet.png"))

    # special sized sprites
    # background is 192x232px
    # get sprite by making a surface of the same size as the sprite, then drawing the image to it
    bg_surf = pg.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
    bg_sheet_location = (1, 77, SCREEN_WIDTH, SCREEN_HEIGHT)
    bg_surf.blit(sprite_sheet, dest, area=bg_sheet_location)

    bg_surf = scale_surface(bg_surf)

    sprites[Sprite.BACKGROUND] = bg_surf

    # load start screen panel
    start_screen_sheet = pg.image.load(str(Path(__file__).parent / "assets/start_screen.png"))

    panel_surf = pg.Surface((176,216))
    panel_sheet_location = (9, 85, 176, 216)
    panel_surf.blit(start_screen_sheet, dest, area=panel_sheet_location)

    panel_surf = scale_surface(panel_surf)

    sprites[Sprite.START_PANEL.value] = panel_surf

    settings_menu_sheet = pg.image.load("./assets/settings_menu.png")
    settings_menu_scaled = pg.transform.scale(settings_menu_sheet, SETTINGS_MENU_ART_SIZE)
    settings_panel = settings_menu_scaled.subsurface(SETTINGS_MENU_PANEL_SOURCE).copy()
    sprites["settings_panel"] = scale_surface(settings_panel)
    strength_text_areas = {
        "hard": pg.Rect(3, 8, 56, 16),
        "medium": pg.Rect(61, 8, 55, 16),
        "easy": pg.Rect(120, 8, 54, 16),
    }
    for strength, text_area in strength_text_areas.items():
        strength_text = settings_menu_scaled.subsurface(text_area).copy()
        sprites[f"strength_{strength}"] = scale_surface(strength_text)
    for mode, text_area in MODE_TEXT_AREAS.items():
        mode_text = settings_menu_scaled.subsurface(text_area).copy()
        sprites[f"mode_{mode}"] = scale_surface(mode_text)

    # load 16x16 sprites
    # track sprite type and position on sprite sheet
    # (name, pos(r, c))
    name_locations = [(Sprite.UNREVEALED, (0, 0)),
                      (Sprite.REVEALED, (0, 1)),
                      (Sprite.FLAG, (0, 2)),
                      (Sprite.MINE, (0, 3)),
                      (Sprite.CLICKED_MINE, (1, 0)),
                      (Sprite.ONE, (1, 1)),
                      (Sprite.TWO, (1, 2)),
                      (Sprite.THREE, (1, 3)),
                      (Sprite.FOUR, (2, 0)),
                      (Sprite.FIVE, (2, 1)),
                      (Sprite.SIX, (2, 2)),
                      (Sprite.SEVEN, (2, 3)),
                      (Sprite.EIGHT, (3, 0))]

    abs_pos = (2, 2)
    offset = (17, 17)
    size = (16, 16)
    for name, pos in name_locations:
        save_sprites_from_sheet(name, abs_pos, pos, offset, size, sprite_sheet)

    # load 16x16 verities
    name_locations = [(Sprite.VERITY_SMILE, (0,0)),
                      (Sprite.VERITY_SUNGLASSES, (0, 1)),
                      (Sprite.VERITY_SURPRISED, (1, 0)),
                      (Sprite.VERITY_DEAD, (1,1))]

    abs_pos = (133, 2)
    for name, pos in name_locations:
        save_sprites_from_sheet(name, abs_pos, pos, offset, size, sprite_sheet)

    # load 8x8 cursor arrow
    abs_pos = (79, 11)
    offset = (9, 9)
    size = (8, 8)
    save_sprites_from_sheet(Sprite.CURSOR, abs_pos, (0,0), offset, size, sprite_sheet)

    # load 8x8 red texts
    abs_pos = (97, 11)
    name_locations = [(Sprite.RED_ZERO, (0, 0)),
                      (Sprite.RED_ONE, (0, 1)),
                      (Sprite.RED_TWO, (0, 2)),
                      (Sprite.RED_THREE, (0, 3)),
                      (Sprite.RED_FOUR, (1, 0)),
                      (Sprite.RED_FIVE, (1, 1)),
                      (Sprite.RED_SIX, (1, 2)),
                      (Sprite.RED_SEVEN, (1, 3)),
                      (Sprite.RED_EIGHT, (2, 0)),
                      (Sprite.RED_NINE, (2, 1)),]

    for name, pos in name_locations:
        save_sprites_from_sheet(name, abs_pos, pos, offset, size, sprite_sheet)

    abs_pos = (97, 47)
    offset = (33, 9)
    size = (32, 8)
    # load 32x8 status texts
    name_locations = [(Sprite.TEXT_LOST, (0, 0)),
                      (Sprite.TEXT_WON, (1, 0)),
                      (Sprite.TEXT_PLAYING, (2, 0))]

    for name, pos in name_locations:
        save_sprites_from_sheet(name, abs_pos, pos, offset, size, sprite_sheet)

    # load game over panel
    game_over_sheet = pg.image.load(str(Path(__file__).parent / "assets/game_over_sheet.png")).convert_alpha()

    # save game over panel as a sprite
    save_sprites_from_sheet(Sprite.GAME_OVER, GAME_OVER_SOURCE_RECT.topleft, (0, 0), (0, 0), GAME_OVER_SOURCE_RECT.size, game_over_sheet, native_size=GAME_OVER_SIZE)

# draw that 20 to 0 for flags remaining
def draw_flags_left_numbers(board):
    flags = board.flags_remaining
    tens_digit = flags // 10
    ones_digit = flags % 10
    # the sprites are 20 to 29, for zero to nine respectively
    tens_sprite = sprites[tens_digit + 20]
    ones_sprite = sprites[ones_digit + 20]
    # tens_sprite = sprites[Sprite.RED_ZERO]
    # ones_sprite = sprites[Sprite.RED_ZERO]
    
    # screen starts at (1,77) on the sprite sheet so subtract that offset
    locations = [(tens_sprite, [SCREEN_WIDTH - 49, 32]),
                 (ones_sprite, [SCREEN_WIDTH - 41, 32])]
    for surf, tile_coord in locations:
        # scale
        tile_coord[0] *= SCALE
        tile_coord[1] *= SCALE

        screen.blit(surf, tile_coord)

# draw the playing status text
def draw_status(board):
    surf = None

    if board.is_game_won:
        surf = Sprite.TEXT_WON.value
    elif board.is_game_lost:
        surf = Sprite.TEXT_LOST.value
    else:
        surf = Sprite.TEXT_PLAYING.value
    
    surf = sprites[surf]

    # screen starts at (1,77) on the sprite sheet so subtract that offset
    tile_coord = [32 - 1, 109 - 77]

    tile_coord[0] *= SCALE
    tile_coord[1] *= SCALE

    screen.blit(surf, tile_coord)

def draw_start_menu():
    panel_surf = sprites[Sprite.START_PANEL.value]
    screen.blit(panel_surf, (PANEL_X * SCALE, PANEL_Y * SCALE))


def draw_settings_page():
    screen.fill((42, 42, 42))
    screen.blit(
         sprites["settings_panel"],
        (SETTINGS_PANEL_POS[0] * SCALE, SETTINGS_PANEL_POS[1] * SCALE)
    )
    draw_red_setting_value(str(selected_settings.mines), MINE_COUNT_DIGITS_POS)
    draw_red_setting_value(f"{selected_settings.board_size}x{selected_settings.board_size}", BOARD_SIZE_VALUE_POS)
    strength_sprite = sprites[f"strength_{selected_settings.strength}"]
    strength_pos = settings_rect(STRENGTH_VALUE_POS, (1, 1)).topleft
    strength_pos = (
        strength_pos[0],
        strength_pos[1] + STRENGTH_VALUE_PIXEL_OFFSETS[selected_settings.strength],
    )
    screen.blit(strength_sprite, strength_pos)
    mode_sprite = sprites[f"mode_{selected_settings.mode}"]
    mode_pos = settings_rect(MODE_VALUE_POS, (1, 1)).topleft
    mode_pos = (mode_pos[0], mode_pos[1] + 25)
    screen.blit(mode_sprite, mode_pos)


def draw_red_setting_value(value, position):
    x = position[0]
    y = position[1]
    for character in value:
        glyph_rect = settings_rect((x, y), (8, 8))
        if character.isdigit():
            sprite = sprites[int(character) + Sprite.RED_ZERO.value]
            screen.blit(sprite, glyph_rect.topleft)
        else:
            separator = pg.font.Font(None, 8 * SCALE).render(character, True, (255, 0, 0))
            screen.blit(separator, separator.get_rect(center=glyph_rect.center))
        x += 8

def configure_display(size=10):
    """Resize the board area and overlay hit boxes together for each new game."""
    global screen, SCREEN_WIDTH, SCREEN_HEIGHT, GAME_OVER_RECT, MENU_BUTTON_RECT
    SCREEN_WIDTH = size * 16 + 32
    SCREEN_HEIGHT = size * 16 + 72
    screen = pg.display.set_mode((SCREEN_WIDTH * SCALE, SCREEN_HEIGHT * SCALE))
    GAME_OVER_RECT.topleft = (
        (SCREEN_WIDTH - GAME_OVER_SIZE[0]) // 2 * SCALE,
        ((SCREEN_HEIGHT - GAME_OVER_SIZE[1]) // 2 + 20) * SCALE)
    MENU_BUTTON_RECT.topleft = (
        GAME_OVER_RECT.x + MENU_BUTTON_RELATIVE_POS[0] * SCALE,
        GAME_OVER_RECT.y + MENU_BUTTON_RELATIVE_POS[1] * SCALE)


def draw_background():
    # Draw a size-aware frame so the old fixed-grid artwork is never stretched.
    screen.fill((0, 0, 0))
    pg.draw.rect(screen, (180, 180, 180),
                 pg.Rect(8 * SCALE, 8 * SCALE,
                         (SCREEN_WIDTH - 16) * SCALE, (SCREEN_HEIGHT - 16) * SCALE))
    pg.draw.rect(screen, (0, 0, 0),
                 pg.Rect(16 * SCALE, 16 * SCALE, (SCREEN_WIDTH - 32) * SCALE, 32 * SCALE))
    font = pg.font.Font(None, 8 * SCALE)
    for label, x in (("STATUS", 31), ("FLAGS", SCREEN_WIDTH - 49)):
        screen.blit(font.render(label, True, (255, 255, 255)), (x * SCALE, 18 * SCALE))


# draw from given board
def draw_board(board):
    for r in range(board.rows):
        for c in range(board.cols):
            tile = board.tiles[r][c]

            sprite_to_draw = Sprite.VERITY_DEAD # if this gets drawn then check for error
            pass_value = False

            # if the tile is flagged, then draw the flag
            if (tile.is_flagged):
                sprite_to_draw = Sprite.FLAG
            # if the tile isn't revealed, then just draw the unrevealed tile
            elif (not tile.is_revealed):
                sprite_to_draw = Sprite.UNREVEALED
            # if it is revealed, then check the value to see if it is [0, 8]
            else:
                # if it is revealed and also a mine, draw the revealed mine tile
                if (tile.is_mine):
                    # clicked mine is displayed w/ clicked sprite
                    if(tile is board.clicked_mine):
                        sprite_to_draw = Sprite.CLICKED_MINE
                    # all unclicked mines are just revealed (w/ unclicked sprites)
                    else:
                        sprite_to_draw = Sprite.MINE
                elif (tile.value >= 0 and tile.value <= 8):
                    sprite_to_draw = tile.value
                    pass_value = True
                else:
                    sprite_to_draw = Sprite.REVEALED

            # get surface to draw
            surf = None

            # use this if passing in an integer instead of sprite enum
            if(pass_value):
                surf = sprites[sprite_to_draw]
            else:
                surf = sprites[sprite_to_draw.value]

            # use (c,r) for (x,y) matching
            draw_to_tile(surf, (c, r))

# Function written by John Rader
# helper to save sheets given the name and relative position of the sprites on the sheet
# name is sprite enum
# absolute_position is the coordinate of the top left pixel of the top left sprite in the set
# spacing is the coordinate representing the horizontal and vertical distance between sprites
# size is the coordinate representing the size of the sprite
# if pass_value is set, lookup with name, not name.value
def save_sprites_from_sheet(name, absolute_position, relative_position, spacing, size, sprite_sheet, native_size=None):
        surf = pg.Surface(size)

        # top left sprite starts at (2, 2), have 1 pixel spacing, and are 16x16
        # use this to find top left of each sprite, 16,16 is the size
        sprite_sheet_location = (absolute_position[0] + relative_position[1] * spacing[0],
                                 absolute_position[1] + relative_position[0] * spacing[1],
                                 size[0], size[1])

        surf.blit(sprite_sheet, (0,0), area=sprite_sheet_location)

        if(native_size is not None):
            surf = pg.transform.scale(surf, native_size)
        
        surf = scale_surface(surf)

        sprites[name.value] = surf

# draw cursor below an unrevealed tile
def draw_cursor(board):
    # only draw cursor if game is not done
    if (board.is_game_won or board.is_game_lost):
        return
    
    # test drawing cursor
    mouse_pos = pg.mouse.get_pos()
    tile_coords = get_clicked_tile(mouse_pos)

    if (tile_coords is None):
        return

    if (board.tiles[tile_coords[1]][tile_coords[0]].is_revealed):
        return

    one_below = (tile_coords[0], tile_coords[1] + 1)
    draw_to_tile(sprites[Sprite.CURSOR.value], one_below)


# helper function for drawing the face on the start panel based on the game state
# authored by: Sina Asheghalishahi, John Rader
# date created: 9/20/26
def draw_face(board):
    if(board.is_game_won):
        face = Sprite.VERITY_SUNGLASSES
    elif(board.is_game_lost):
        face = Sprite.VERITY_DEAD
    else:
        face = Sprite.VERITY_SMILE

    # draw face image to screen
    screen.blit(sprites[face.value], ((SCREEN_WIDTH // 2 - 8) * SCALE, FACE_POS[1] * SCALE))


# helper function for drawing game over panel when the game ends
# authored by: Sina Asheghalishahi
# date created: 9/20/26
def draw_game_over(board):
    if(board.is_game_won or board.is_game_lost):
        screen.blit(sprites[Sprite.GAME_OVER.value], GAME_OVER_RECT.topleft)

# Function outline sourced from pygame tutorial
# core drawing loop


# date created : 10/11/26
# draws the elapsed game time in seconds at the top of the game screen
def draw_game_timer(start_time , end_time=None):
    if start_time is None:
        return
    # f the game has ended ... use the saved ending time so the timer freezes
    if end_time is not None:
        elapsed_ms = end_time - start_time
    else:
        elapsed_ms = pg.time.get_ticks() - start_time
    elapsed_seconds = max(0 , elapsed_ms // 1000)
    minutes = elapsed_seconds // 60
    seconds = elapsed_seconds % 60
    timer_text = f"{minutes:02}:{seconds:02}"
    font = pg.font.Font(None, 8 * SCALE)
    label_surface = font.render("TIME" , True , (255,255,255))
    time_surface = font.render(timer_text , True , (255,255,255))

    center_x = SCREEN_WIDTH * SCALE // 2
    label_rect = label_surface.get_rect(center=(center_x , 17 * SCALE))
    time_rect = time_surface.get_rect(center=(center_x , 40 * SCALE))

    screen.blit(label_surface , label_rect)
    screen.blit(time_surface , time_rect)
def main():
    # pygame setup
    pg.init()

    # updates the non local vars instead of making new local ones
    global game_state, selected_settings

    clock = pg.time.Clock()
    running = True
    game_over_start_time = -1
    # game timerr values
    game_start_time = None
    game_end_time = None

    init_sprites()

    # board doesnt exist until the player presses start on the menu
    board = None
    # same with ai solver
    ai_solver = AISolver(AIStrength[selected_settings.strength.upper()])
    # whether or not to alternate turns with the real player
    ai_alternate, ai_turn = ai_turn_configuration(selected_settings.mode)

    while running:
        # poll for events
        # pygame.QUIT event means the user clicked X to close your window
        for event in pg.event.get():
            if event.type == pg.QUIT:
                running = False

            # on click, handle it differently depending on which screen is active
            elif event.type == pg.MOUSEBUTTONDOWN:
                if(game_state == "game_over"):
                    mouse_pos = event.pos

                    if(event.button == 1 and MENU_BUTTON_RECT.collidepoint(mouse_pos)):
                        game_state = "menu"
                        configure_display()

                # Menu controls are positioned relative to the panel and scaled by SCALE.
                elif game_state == "menu":
                    mouse_pos = pg.mouse.get_pos()

                    start_button_rect = scaled_rect(
                        (PANEL_X + START_BUTTON_POS[0], PANEL_Y + START_BUTTON_POS[1]),
                        START_BUTTON_SIZE
                    )
                    settings_button_rect = scaled_rect(
                        (PANEL_X + SETTINGS_BUTTON_POS[0], PANEL_Y + SETTINGS_BUTTON_POS[1]),
                        SETTINGS_BUTTON_SIZE
                    )
                    if event.button == 1 and start_button_rect.collidepoint(mouse_pos):
                        board = selected_settings.create_board()
                        ai_solver = AISolver(AIStrength[selected_settings.strength.upper()])
                        ai_alternate, ai_turn = ai_turn_configuration(selected_settings.mode)
                        configure_display(board.rows)
                        game_over_start_time = -1
                        # start fresh game clock
                        game_start_time = pg.time.get_ticks()
                        game_end_time = None
                        game_state = "playing"
                    elif event.button == 1 and settings_button_rect.collidepoint(mouse_pos):
                        game_state = "settings"
                elif game_state == "settings" and event.button == 1:
                    mouse_pos = pg.mouse.get_pos()
                    mine_up_rect = settings_rect(MINE_UP_POS, SETTING_ARROW_SIZE)
                    mine_down_rect = settings_rect(MINE_DOWN_POS, SETTING_ARROW_SIZE)
                    board_up_rect = settings_rect(BOARD_UP_POS, SETTING_ARROW_SIZE)
                    board_down_rect = settings_rect(BOARD_DOWN_POS, SETTING_ARROW_SIZE)
                    settings_start_rect = settings_rect(SETTINGS_START_POS, SETTINGS_START_SIZE)
                    strength_up_rect = settings_rect(STRENGTH_UP_POS, SETTING_ARROW_SIZE)
                    strength_down_rect = settings_rect(STRENGTH_DOWN_POS, SETTING_ARROW_SIZE)
                    mode_up_rect = settings_rect(MODE_UP_POS, SETTING_ARROW_SIZE)
                    mode_down_rect = settings_rect(MODE_DOWN_POS, SETTING_ARROW_SIZE)

                    if mine_up_rect.collidepoint(mouse_pos):
                        selected_settings = selected_settings.adjusted("mines", 1)
                    elif mine_down_rect.collidepoint(mouse_pos):
                        selected_settings = selected_settings.adjusted("mines", -1)
                    elif board_up_rect.collidepoint(mouse_pos):
                        selected_settings = selected_settings.adjusted("board_size", 1)
                    elif board_down_rect.collidepoint(mouse_pos):
                        selected_settings = selected_settings.adjusted("board_size", -1)
                    elif strength_up_rect.collidepoint(mouse_pos):
                        selected_settings = selected_settings.adjusted("strength", 1)
                    elif strength_down_rect.collidepoint(mouse_pos):
                        selected_settings = selected_settings.adjusted("strength", -1)
                    elif mode_up_rect.collidepoint(mouse_pos):
                        selected_settings = selected_settings.adjusted("mode", 1)
                    elif mode_down_rect.collidepoint(mouse_pos):
                        selected_settings = selected_settings.adjusted("mode", -1)
                    elif settings_start_rect.collidepoint(mouse_pos):
                        board = selected_settings.create_board()
                        ai_solver = AISolver(AIStrength[selected_settings.strength.upper()])
                        ai_alternate, ai_turn = ai_turn_configuration(selected_settings.mode)
                        configure_display(board.rows)
                        game_over_start_time = -1
                        # start fresh game clock 
                        game_start_time = pg.time.get_ticks()
                        game_end_time = None
                        game_state = "playing"
                # on click, get the cords of the tile that was clicked
                elif game_state == "playing":
                    assert board is not None
                    # disregard board input when the ai is in control
                    if ai_turn:
                        continue
                    LEFT_CLICK = 1
                    RIGHT_CLICK = 3
                    if (event.button == LEFT_CLICK or event.button == RIGHT_CLICK):
                        mouse_pos = event.pos
                        tile_coords = get_clicked_tile(mouse_pos)
                        # get coords of clicked tile
                        if (tile_coords is not None):
                            col, row = tile_coords
                            tile = get_tile_at_coords((row, col), board)
                            # for left-click, if first click, then do mine blocking logic, and otherwise reveal the clicked tile and surrounding tiles
                            if (event.button == LEFT_CLICK):
                                if(not board.first_click):
                                    first_click(tile, board)
                                else:
                                    left_click_tile(tile, board)

                            # for right-click, execute flagging logic
                            if (event.button == RIGHT_CLICK):
                                right_click_tile(tile, board)

                            # end turn
                            if ai_solver is not None and ai_alternate:
                                ai_turn = True

                    # detect game over state change
                    if(board.is_game_lost or board.is_game_won):
                        game_state = "game_over"
                        # record game over start time
                        game_over_start_time = pg.time.get_ticks()
                        if game_end_time is None:
                            game_end_time = pg.time.get_ticks() 
            elif event.type == pg.KEYDOWN and game_state == "settings" and event.key == pg.K_ESCAPE:
                game_state = "menu"

        # now take ai input and detect game overs regardless of real input
        if game_state == "playing":
            assert board is not None
            if ai_turn:
                assert ai_solver is not None
                finished = ai_solver.run(board)
                if finished and ai_alternate:
                    ai_turn = False
            # detect game over state change
            if(board.is_game_lost or board.is_game_won):
                game_state = "game_over"
                # record game over start time
                game_over_start_time = pg.time.get_ticks()
                if game_end_time is None:
                    game_end_time = pg.time.get_ticks() 


        # draw whichever screen is currently active
        if game_state == "menu":
            draw_start_menu()
        elif game_state == "settings":
            draw_settings_page()
        elif game_state == "playing":
            # draw background
            draw_background()

            draw_board(board)

            draw_cursor(board)

            draw_flags_left_numbers(board)

            draw_status(board)

            draw_face(board)

            draw_game_timer(game_start_time)
        # during gameover, display everything minus the cursor, and plus the blinking game over panel
        elif game_state == "game_over":
            # draw background
            draw_background()

            draw_board(board)

            draw_flags_left_numbers(board)

            draw_status(board)

            draw_face(board)

            draw_game_timer(game_start_time , game_end_time)

            # calculate elapsed time from game over start time
            elapsed_time = pg.time.get_ticks() - game_over_start_time

            # only draw the game over board during even intervals of 500 ms
            if((elapsed_time // GAME_OVER_BLINK_MS) % 2 == 0):
                draw_game_over(board)


        # flip() the display to put your work on screen
        pg.display.flip()

        clock.tick(60)  # limits FPS to 60

    pg.quit()


if __name__ == "__main__":
    main()