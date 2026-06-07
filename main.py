import pygame as py
from lib import DoublePendulum
import sys
import math
from collections import deque

WIDTH, HEIGHT = 1050, 650
FPS    = 60
DT     = 1 / FPS
SCALE  = 120
ORIGIN = (460, 250)   # pendulum pivot in sim area

PANEL_X = 760         # left edge of right panel
PANEL_W = WIDTH - PANEL_X
PANEL_H = HEIGHT

BG         = (250, 250, 250) # near-white sim background
PANEL_BG   = (255, 255, 255) # white panel
BORDER     = (210, 210, 210) # light grey divider
BLACK      = ( 30,  30,  30)
DIM        = (160, 160, 160)
BLUE       = ( 40, 110, 220)
RED        = (210,  50,  50)
TRAIL_COL  = (130,  60, 200)
GREEN_BTN  = ( 34, 150,  80)
GREEN_HOV  = ( 20, 110,  55)
STOP_BTN   = (190, 190, 190) #stop button collor
STOP_HOV   = (155, 155, 155) #stop button hover color
RESET_BTN  = (200,  85,  65) #reset button collor
RESET_HOV  = (165,  55,  40) #reset button hover color
WHITE      = (255, 255, 255)

py.init()
py.font.init()
screen = py.display.set_mode((WIDTH, HEIGHT))
py.display.set_caption("Double Pendulum Simulation")
clock  = py.time.Clock()
#fonts
FONT_TITLE = py.font.SysFont("Segoe UI", 14, bold=True)
FONT_LABEL = py.font.SysFont("Segoe UI", 13)
FONT_SMALL = py.font.SysFont("Segoe UI", 11)
FONT_BIG   = py.font.SysFont("Segoe UI", 26, bold=True)
FONT_MED   = py.font.SysFont("Segoe UI", 14)

class Slider:
    def __init__(self, x, y, w, val_min, val_max, initial, color=BLUE):
        self.rect     = py.Rect(x, y, w, 4)
        self.min      = val_min
        self.max      = val_max
        self.value    = initial
        self.color    = color
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

    def handle_event(self, event): #handles mouse clicks
        if event.type == py.MOUSEBUTTONDOWN:
            if self.handle_rect.collidepoint(event.pos) or \
               self.rect.inflate(0, 20).collidepoint(event.pos): #easier click
                self.dragging = True
        elif event.type == py.MOUSEBUTTONUP:
            self.dragging = False #turns off dragging when not clicked
        elif event.type == py.MOUSEMOTION and self.dragging:
            rel_x = max(self.rect.x, min(event.pos[0], self.rect.right))
            t = (rel_x - self.rect.x) / self.rect.w
            self.value = self.min + t * (self.max - self.min)
        return self.dragging

    def draw(self, surf): #draw slider
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

class TextInput: #text input for slider
    def __init__(self, x, y, w, h, initial, val_min, val_max, color=BLUE):
        self.rect   = py.Rect(x, y, w, h)
        self.min    = val_min
        self.max    = val_max
        self.value  = initial
        self.text   = str(int(initial))
        self.active = False
        self.color  = color

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
        self.text = str(int(self.value))

    def set_value(self, v):
        self.value = v
        if not self.active:
            self.text = str(int(round(v)))

    def draw(self, surf):
        border_col = self.color if self.active else BORDER
        py.draw.rect(surf, WHITE, self.rect, border_radius=4)
        py.draw.rect(surf, border_col, self.rect, 1, border_radius=4)
        display = self.text + ("|" if self.active else "")
        t = FONT_LABEL.render(display, True, BLACK)
        surf.blit(t, (self.rect.x + 5, self.rect.centery - t.get_height() // 2))

class Button:
    def __init__(self, x, y, w, h, text, color, hover_color, text_color=WHITE):
        self.rect        = py.Rect(x, y, w, h)
        self.text        = text
        self.color       = color
        self.hover_color = hover_color
        self.text_color  = text_color
        self.hovered     = False

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

def main():
    init_theta1 = 120.0 #initial angles
    init_theta2 = 150.0

    pendulum = DoublePendulum(
        theta1=math.radians(init_theta1), #calling double pendulum math file
        theta2=math.radians(init_theta2)
    )
    trail       = deque(maxlen=800) #trail
    running     = True
    simulating  = False
    elapsed_sim = 0.0

    #side panel height width etc
    px = PANEL_X + 14
    pw = PANEL_W - 28
    input_w, input_h = 54, 22

    # Layout:
    ROW1_Y   = 70    #angle 1 label placement
    SLIDE1_Y = ROW1_Y + input_h + 8   #slider 1 placement

    ROW2_Y   = SLIDE1_Y + 14 + 20 #angle 2 label placement
    SLIDE2_Y = ROW2_Y + input_h + 8 #slider 2 placement

    #calling slider function
    s_theta1 = Slider(px, SLIDE1_Y, pw, -180, 180, init_theta1, color=BLUE)
    s_theta2 = Slider(px, SLIDE2_Y, pw, -180, 180, init_theta2, color=RED)

    #calling text input function
    input_x = PANEL_X + PANEL_W - 14 - input_w
    ti_theta1 = TextInput(input_x, ROW1_Y,  input_w, input_h, init_theta1, -180, 180, color=BLUE)
    ti_theta2 = TextInput(input_x, ROW2_Y,  input_w, input_h, init_theta2, -180, 180, color=RED)

    #calling button functions
    pcx = PANEL_X + PANEL_W // 2
    HINT_Y  = SLIDE2_Y + 28
    BTN_Y   = HINT_Y + 22
    RESET_Y = BTN_Y + 42

    btn_play  = Button(pcx - 82, BTN_Y,  76, 32, "▶  Play",  GREEN_BTN, GREEN_HOV)
    btn_stop  = Button(pcx +  6, BTN_Y,  76, 32, "■  Stop",  STOP_BTN,  STOP_HOV,  text_color=BLACK)
    btn_reset = Button(pcx - 37, RESET_Y, 74, 28, "↺  Reset", RESET_BTN, RESET_HOV)

    #loop
    while running:
        for event in py.event.get():
            if event.type == py.QUIT:
                running = False
            elif event.type == py.KEYDOWN:
                if event.key == py.K_ESCAPE:
                    running = False
                elif event.key == py.K_SPACE:
                    simulating = not simulating

            s1_drag = s_theta1.handle_event(event) #handling slider 1
            s2_drag = s_theta2.handle_event(event) #handling slider 2
            ti_theta1.handle_event(event) #handling text input 1
            ti_theta2.handle_event(event) #handling text input 2

            #Sync slider with input
            if s1_drag:
                ti_theta1.set_value(s_theta1.value)
            if s2_drag:
                ti_theta2.set_value(s_theta2.value)
            #Sync input with slider (after commit / click-away)
            if not ti_theta1.active:
                s_theta1.value = ti_theta1.value
            if not ti_theta2.active:
                s_theta2.value = ti_theta2.value

            if btn_play.handle_event(event): #handling button play
                if not simulating:
                    pendulum = DoublePendulum(
                        theta1=math.radians(s_theta1.value), #taking s_theta1 value from slider as initial values to be simulated
                        theta2=math.radians(s_theta2.value)
                    )
                    trail.clear() #clear previous trail
                    elapsed_sim = 0.0 #reset elapsed time
                simulating = True #start simulation

            if btn_stop.handle_event(event): #handling button stop
                simulating = False #stop simulation

            if btn_reset.handle_event(event): #handling button reset
                simulating = False #stop simulation
                elapsed_sim = 0.0 #reset elapsed time
                trail.clear() #clear previous trail
                pendulum = DoublePendulum(
                    theta1=math.radians(s_theta1.value), #taking s_theta1 value from slider as initial values to be reset
                    theta2=math.radians(s_theta2.value) #taking s_theta2 value from slider as initial values to be reset
                )

        if simulating:
            pendulum.step(DT)
            elapsed_sim += DT #time countdown increase
            (x1, y1), (x2, y2) = pendulum.get_coordinates()
            pos1 = (int(ORIGIN[0] + x1 * SCALE), int(ORIGIN[1] - y1 * SCALE))
            pos2 = (int(ORIGIN[0] + x2 * SCALE), int(ORIGIN[1] - y2 * SCALE))
            trail.append(pos2)
        else:
            th1  = math.radians(s_theta1.value)
            th2  = math.radians(s_theta2.value)
            x1   = math.sin(th1);  y1 = -math.cos(th1)
            x2   = x1 + math.sin(th2); y2 = y1 - math.cos(th2)
            pos1 = (int(ORIGIN[0] + x1 * SCALE), int(ORIGIN[1] - y1 * SCALE))
            pos2 = (int(ORIGIN[0] + x2 * SCALE), int(ORIGIN[1] - y2 * SCALE))

        screen.fill(BG)

        if len(trail) > 1: #drawing the trail 
            py.draw.lines(screen, TRAIL_COL, False, list(trail), 1)

        py.draw.line(screen, BLACK, ORIGIN, pos1, 2) #drawing the arms
        py.draw.line(screen, BLACK, pos1,   pos2, 2)

        py.draw.circle(screen, BLACK, ORIGIN, 5) #origin point

        py.draw.circle(screen, BLUE,  pos1, 12)
        py.draw.circle(screen, WHITE, pos1,  4)

        py.draw.circle(screen, RED,   pos2, 12)
        py.draw.circle(screen, WHITE, pos2,  4)

        #time
        mins     = int(elapsed_sim) // 60
        secs     = int(elapsed_sim) % 60
        frac     = int((elapsed_sim % 1) * 10)
        time_str = f"{mins:02d}:{secs:02d}.{frac}"

        t_time = FONT_BIG.render(time_str, True, BLACK if simulating else DIM)
        screen.blit(t_time, (14, 14))

        stat_text = "RUNNING" if simulating else "PAUSED"
        stat_col  = GREEN_BTN if simulating else DIM
        t_stat = FONT_SMALL.render(stat_text, True, stat_col)
        screen.blit(t_stat, (14, 46))

        #draw right panel
        py.draw.rect(screen, PANEL_BG, py.Rect(PANEL_X, 0, PANEL_W, HEIGHT))
        py.draw.line(screen, BORDER, (PANEL_X, 0), (PANEL_X, HEIGHT), 1)

        t_title = FONT_TITLE.render("DOUBLE PENDULUM", True, BLACK)
        screen.blit(t_title, (PANEL_X + PANEL_W // 2 - t_title.get_width() // 2, 18))
        py.draw.line(screen, BORDER, (PANEL_X + 10, 42), (PANEL_X + PANEL_W - 10, 42), 1)

        t_lbl1 = FONT_LABEL.render("θ₁  Angle 1", True, BLUE) #draw label 1
        screen.blit(t_lbl1, (px, ROW1_Y + (input_h - t_lbl1.get_height()) // 2))
        ti_theta1.draw(screen)
        s_theta1.draw(screen)

        t_lbl2 = FONT_LABEL.render("θ₂  Angle 2", True, RED) #draw label 2
        screen.blit(t_lbl2, (px, ROW2_Y + (input_h - t_lbl2.get_height()) // 2))
        ti_theta2.draw(screen)
        s_theta2.draw(screen)

        hint = FONT_SMALL.render("Type value & press Enter  (−180° to 180°)", True, DIM)
        screen.blit(hint, (PANEL_X + PANEL_W // 2 - hint.get_width() // 2, HINT_Y))

        py.draw.line(screen, BORDER,
                     (PANEL_X + 10, BTN_Y - 10),
                     (PANEL_X + PANEL_W - 10, BTN_Y - 10), 1)

        #drawing buttons
        btn_play.draw(screen)
        btn_stop.draw(screen)
        btn_reset.draw(screen)

        sp = FONT_SMALL.render("Space = Play / Pause", True, DIM)
        screen.blit(sp, (PANEL_X + PANEL_W // 2 - sp.get_width() // 2, RESET_Y + 36))

        py.display.flip()
        clock.tick(FPS)

    py.quit()
    sys.exit()


if __name__ == "__main__":
    main()
