"""Minimal Pygame view and input adapter for the settings model.

Inputs: Pygame events, a surface, and GameSettings. Outputs: updated settings
and a start request. Created 2026-10-10 for Anthony Tran's settings task.
The team's menu artwork can replace this view without changing validation.
"""
import pygame as pg

FIELDS = (("board_size", "Board size"), ("mines", "Mines"),
          ("max_hints", "Max hints"), ("time_limit_seconds", "Time limit"))


def controls(surface):
    """Use the same rectangles for rendering and hit testing."""
    width, height = surface.get_size()
    rows = []
    for index, (field, label) in enumerate(FIELDS):
        y = int(height * (0.24 + index * 0.13))
        rows.append((field, label, pg.Rect(int(width * .60), y, 44, 44),
                     pg.Rect(int(width * .85), y, 44, 44)))
    return rows, pg.Rect(width // 4, int(height * .82), width // 2, 56)


def handle_event(event, settings, surface):
    """Only left clicks activate controls; Start returns the current snapshot."""
    if event.type != pg.MOUSEBUTTONDOWN or event.button != 1:
        return settings, False
    rows, start = controls(surface)
    for field, _, minus, plus in rows:
        if minus.collidepoint(event.pos):
            return settings.adjusted(field, -1), False
        if plus.collidepoint(event.pos):
            return settings.adjusted(field, 1), False
    return settings, start.collidepoint(event.pos)


def draw(surface, settings):
    """Render live values and visibly disable controls at their bounds."""
    surface.fill((30, 35, 44))
    font = pg.font.Font(None, 30)
    title_font = pg.font.Font(None, 44)
    width, height = surface.get_size()

    def text(label, center, color=(240, 242, 246), selected_font=font):
        rendered = selected_font.render(label, True, color)
        surface.blit(rendered, rendered.get_rect(center=center))

    text("Minesweeper settings", (width // 2, int(height * .10)),
         selected_font=title_font)
    rows, start = controls(surface)
    for field, label, minus, plus in rows:
        value = getattr(settings, field)
        if field == "board_size":
            value = f"{value} x {value}"
        elif field == "time_limit_seconds":
            value = "Off" if value == 0 else f"{value // 60} min"
        text(label, (int(width * .25), minus.centery))
        text(str(value), ((minus.right + plus.left) // 2, minus.centery))
        for rect, direction, symbol in ((minus, -1, "-"), (plus, 1, "+")):
            enabled = settings.adjusted(field, direction) != settings
            pg.draw.rect(surface, (66, 94, 125) if enabled else (48, 51, 58),
                         rect, border_radius=6)
            text(symbol, rect.center, (255, 255, 255) if enabled else (115, 119, 126))
    text(f"Mines: 1-{settings.mine_limit} | Hints: 0-10 | Time: Off-30 min",
         (width // 2, int(height * .76)))
    pg.draw.rect(surface, (42, 120, 88), start, border_radius=8)
    text("Start game", start.center)
