#gui.py

import pygame as pg
from defs import *
from backend import *
from pathlib import Path
from settings import GameSettings
import settings_menu


SCALE = 4
SCREEN_WIDTH = 192 # ten 16px tiles + four 8px tiles = 192
SCREEN_HEIGHT = 232 # ten 16px tiles + nine 8px tiles = 232

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
    settings_menu.draw(screen, selected_settings)


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
def main():
    # pygame setup
    pg.init()

    # updates the non local vars instead of making new local ones
    global game_state, selected_settings

    clock = pg.time.Clock()
    running = True
    game_over_start_time = -1

    init_sprites()

    # board doesnt exist until the player presses start on the menu
    board = None

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

                elif game_state == "menu":
                    selected_settings, start_requested = settings_menu.handle_event(
                        event, selected_settings, screen)
                    if start_requested:
                        board = selected_settings.create_board()
                        configure_display(board.rows)
                        game_over_start_time = -1
                        game_state = "playing"
                # on click, get the cords of the tile that was clicked
                elif game_state == "playing":
                    assert board is not None
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

                    # detect game over state change
                    if(board.is_game_lost or board.is_game_won):
                        game_state = "game_over"
                        # record game over start time
                        game_over_start_time = pg.time.get_ticks()

        # draw whichever screen is currently active
        if game_state == "menu":
            draw_start_menu()
        elif game_state == "playing":
            # draw background
            draw_background()

            draw_board(board)

            draw_cursor(board)

            draw_flags_left_numbers(board)

            draw_status(board)

            draw_face(board)

        # during gameover, display everything minus the cursor, and plus the blinking game over panel
        elif game_state == "game_over":
            # draw background
            draw_background()

            draw_board(board)

            draw_flags_left_numbers(board)

            draw_status(board)

            draw_face(board)

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
