import pygame as py

BORDER = (210, 210, 210)
WHITE = (255, 255, 255)
BLACK = (30, 30, 30)
BLUE = (40, 110, 220)

py.font.init()
FONT_LABEL = py.font.SysFont("Segoe UI", 13)
FONT_MED = py.font.SysFont("Segoe UI", 14)

class Slider:
    def __init__(self, x, y, w, val_min, val_max, initial, color=BLUE):
        self.rect = py.Rect(x, y, w, 4)
        self.min = val_min
        self.max = val_max
        self.value = initial
        self.color = color
        self.dragging = False
        self.handle_r = 7

    @property
    def handle_x(self):
        t = (self.value - self.min) / (self.max - self.min)
        return int(self.rect.x + t * self.rect.w)

    @property
    def handle_rect(self):
        hx = self.handle_x
        r  = self.handle_r
        return py.Rect(hx - r, self.rect.centery - r, r * 2, r * 2)

    def handle_event(self, event): 
        if event.type == py.MOUSEBUTTONDOWN:
            if self.handle_rect.collidepoint(event.pos) or \
               self.rect.inflate(0, 20).collidepoint(event.pos): 
                self.dragging = True
        elif event.type == py.MOUSEBUTTONUP:
            self.dragging = False 
        elif event.type == py.MOUSEMOTION and self.dragging:
            rel_x = max(self.rect.x, min(event.pos[0], self.rect.right))
            t = (rel_x - self.rect.x) / self.rect.w
            self.value = self.min + t * (self.max - self.min)
        return self.dragging

    def draw(self, surf): 
        py.draw.rect(surf, BORDER, self.rect, border_radius=2)
        fill_w = max(0, self.handle_x - self.rect.x)
        py.draw.rect(surf, self.color,
                     py.Rect(self.rect.x, self.rect.y, fill_w, self.rect.h),
                     border_radius=2)
        hx = self.handle_x
        cy = self.rect.centery
        py.draw.circle(surf, self.color, (hx, cy), self.handle_r)
        py.draw.circle(surf, WHITE,      (hx, cy), self.handle_r - 3)
        py.draw.circle(surf, self.color, (hx, cy), 3)

class TextInput: 
    def __init__(self, x, y, w, h, initial, val_min, val_max, color=BLUE, decimals=0):
        self.rect = py.Rect(x, y, w, h)
        self.min = val_min
        self.max = val_max
        self.value = initial
        self.active = False
        self.color = color
        self.decimals = decimals
        self.text = self._fmt(initial)

    def _fmt(self, v):
        if self.decimals == 0:
            return str(int(round(v)))
        return f"{v:.{self.decimals}f}"

    def handle_event(self, event):
        if event.type == py.MOUSEBUTTONDOWN:
            self.active = self.rect.collidepoint(event.pos)
            if self.active:
                self.text = str(int(self.value))
        elif event.type == py.KEYDOWN and self.active:
            if event.key in (py.K_RETURN, py.K_KP_ENTER):
                self._commit()
                self.active = False
            elif event.key == py.K_BACKSPACE:
                self.text = self.text[:-1]
            elif event.unicode in "0123456789.-":
                if len(self.text) < 6:
                    self.text += event.unicode

    def _commit(self):
        try:
            v = float(self.text)
            self.value = max(self.min, min(self.max, v))
        except ValueError:
            pass
        self.text = self._fmt(self.value)

    def set_value(self, v):
        self.value = v
        if not self.active:
            self.text = self._fmt(v)

    def draw(self, surf):
        border_col = self.color if self.active else BORDER
        py.draw.rect(surf, WHITE, self.rect, border_radius=4)
        py.draw.rect(surf, border_col, self.rect, 1, border_radius=4)
        display = self.text + ("|" if self.active else "")
        t = FONT_LABEL.render(display, True, BLACK)
        surf.blit(t, (self.rect.x + 5, self.rect.centery - t.get_height() // 2))

class Button:
    def __init__(self, x, y, w, h, text, color, hover_color, text_color=WHITE):
        self.rect = py.Rect(x, y, w, h)
        self.text = text
        self.color = color
        self.hover_color = hover_color
        self.text_color = text_color
        self.hovered = False

    def handle_event(self, event): #handles pressing etc
        if event.type == py.MOUSEMOTION:
            self.hovered = self.rect.collidepoint(event.pos)
        elif event.type == py.MOUSEBUTTONDOWN:
            if self.rect.collidepoint(event.pos):
                return True
        return False

    def draw(self, surf): #draw and hover
        col = self.hover_color if self.hovered else self.color
        py.draw.rect(surf, col, self.rect, border_radius=5)
        t = FONT_MED.render(self.text, True, self.text_color)
        surf.blit(t, (self.rect.centerx - t.get_width() // 2,
                      self.rect.centery - t.get_height() // 2))