import pygame as py
from lib import DoublePendulum
from components import Slider, TextInput, Button #import UI
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


def main():
    init_theta1 = 120.0 #initial angles
    init_theta2 = 150.0
    init_m1     = 1.0   #initial masses
    init_m2     = 1.0
    init_l1     = 1.0   #initial lengths
    init_l2     = 1.0

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
    ROW_GAP = input_h + 8 + 14 + 20  # label row + slider + spacing

    # Layout — angles
    ROW1_Y   = 70
    SLIDE1_Y = ROW1_Y + input_h + 8
    ROW2_Y   = SLIDE1_Y + 14 + 20
    SLIDE2_Y = ROW2_Y + input_h + 8

    # Layout — masses (below angles)
    SEC_MASS_Y = SLIDE2_Y + 18 + 20   # section divider label
    ROW3_Y     = SEC_MASS_Y + 18
    SLIDE3_Y   = ROW3_Y + input_h + 8
    ROW4_Y     = SLIDE3_Y + 14 + 20
    SLIDE4_Y   = ROW4_Y + input_h + 8

    # Layout — lengths (below masses)
    SEC_LEN_Y = SLIDE4_Y + 18 + 20
    ROW5_Y    = SEC_LEN_Y + 18
    SLIDE5_Y  = ROW5_Y + input_h + 8
    ROW6_Y    = SLIDE5_Y + 14 + 20
    SLIDE6_Y  = ROW6_Y + input_h + 8

    #calling slider function — angles
    s_theta1 = Slider(px, SLIDE1_Y, pw, -180, 180, init_theta1, color=BLUE)
    s_theta2 = Slider(px, SLIDE2_Y, pw, -180, 180, init_theta2, color=RED)

    #calling slider function — masses
    s_m1 = Slider(px, SLIDE3_Y, pw, 0.1, 10.0, init_m1, color=BLUE)
    s_m2 = Slider(px, SLIDE4_Y, pw, 0.1, 10.0, init_m2, color=RED)

    #calling slider function — lengths
    s_l1 = Slider(px, SLIDE5_Y, pw, 1.0, 2.0, init_l1, color=BLUE)
    s_l2 = Slider(px, SLIDE6_Y, pw, 1.0, 2.0, init_l2, color=RED)

    #calling text input function — angles
    input_x = PANEL_X + PANEL_W - 14 - input_w
    ti_theta1 = TextInput(input_x, ROW1_Y, input_w, input_h, init_theta1, -180, 180, color=BLUE)
    ti_theta2 = TextInput(input_x, ROW2_Y, input_w, input_h, init_theta2, -180, 180, color=RED)

    #calling text input function — masses
    ti_m1 = TextInput(input_x, ROW3_Y, input_w, input_h, init_m1, 0.1, 10.0, color=BLUE, decimals=1)
    ti_m2 = TextInput(input_x, ROW4_Y, input_w, input_h, init_m2, 0.1, 10.0, color=RED,  decimals=1)

    #calling text input function — lengths
    ti_l1 = TextInput(input_x, ROW5_Y, input_w, input_h, init_l1, 0.1, 5.0, color=BLUE, decimals=1)
    ti_l2 = TextInput(input_x, ROW6_Y, input_w, input_h, init_l2, 0.1, 5.0, color=RED,  decimals=1)

    #calling button functions
    pcx     = PANEL_X + PANEL_W // 2
    HINT_Y  = SLIDE6_Y + 28
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

            s1_drag  = s_theta1.handle_event(event) #handling angle sliders
            s2_drag  = s_theta2.handle_event(event)
            sm1_drag = s_m1.handle_event(event)      #handling mass sliders
            sm2_drag = s_m2.handle_event(event)
            sl1_drag = s_l1.handle_event(event)      #handling length sliders
            sl2_drag = s_l2.handle_event(event)
            ti_theta1.handle_event(event)            #handling text inputs
            ti_theta2.handle_event(event)
            ti_m1.handle_event(event)
            ti_m2.handle_event(event)
            ti_l1.handle_event(event)
            ti_l2.handle_event(event)

            #Sync sliders → inputs
            if s1_drag:  ti_theta1.set_value(s_theta1.value) #taking s_theta1 value from slider as initial values to be simulated
            if s2_drag:  ti_theta2.set_value(s_theta2.value)
            if sm1_drag: ti_m1.set_value(s_m1.value)
            if sm2_drag: ti_m2.set_value(s_m2.value)
            if sl1_drag: ti_l1.set_value(s_l1.value)
            if sl2_drag: ti_l2.set_value(s_l2.value)
            #Sync inputs → sliders (after commit / click-away)
            if not ti_theta1.active: s_theta1.value = ti_theta1.value
            if not ti_theta2.active: s_theta2.value = ti_theta2.value
            if not ti_m1.active:     s_m1.value     = ti_m1.value
            if not ti_m2.active:     s_m2.value     = ti_m2.value
            if not ti_l1.active:     s_l1.value     = ti_l1.value
            if not ti_l2.active:     s_l2.value     = ti_l2.value

            if btn_play.handle_event(event): #handling button play
                if not simulating:
                    pendulum = DoublePendulum(
                        theta1=math.radians(s_theta1.value),
                        theta2=math.radians(s_theta2.value),
                        m1=s_m1.value, m2=s_m2.value,
                        l1=s_l1.value, l2=s_l2.value,
                    )
                    trail.clear()
                    elapsed_sim = 0.0 #reset elapsed time
                simulating = True

            if btn_stop.handle_event(event): #handling button stop
                simulating = False

            if btn_reset.handle_event(event): #handling button reset
                simulating = False
                elapsed_sim = 0.0
                trail.clear()
                pendulum = DoublePendulum(
                    theta1=math.radians(s_theta1.value),
                    theta2=math.radians(s_theta2.value),
                    m1=s_m1.value, m2=s_m2.value,
                    l1=s_l1.value, l2=s_l2.value,
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

        # --- Angle rows ---
        t_lbl1 = FONT_LABEL.render("θ₁  Angle 1", True, BLUE)
        screen.blit(t_lbl1, (px, ROW1_Y + (input_h - t_lbl1.get_height()) // 2))
        ti_theta1.draw(screen)
        s_theta1.draw(screen)

        t_lbl2 = FONT_LABEL.render("θ₂  Angle 2", True, RED)
        screen.blit(t_lbl2, (px, ROW2_Y + (input_h - t_lbl2.get_height()) // 2))
        ti_theta2.draw(screen)
        s_theta2.draw(screen)

        #Mass
        py.draw.line(screen, BORDER, (PANEL_X + 10, SEC_MASS_Y - 8), (PANEL_X + PANEL_W - 10, SEC_MASS_Y - 8), 1)
        t_sec_mass = FONT_SMALL.render("MASS  (kg)", True, DIM)
        screen.blit(t_sec_mass, (PANEL_X + PANEL_W // 2 - t_sec_mass.get_width() // 2, SEC_MASS_Y))

        t_lbl3 = FONT_LABEL.render("m₁  Mass 1", True, BLUE)
        screen.blit(t_lbl3, (px, ROW3_Y + (input_h - t_lbl3.get_height()) // 2))
        ti_m1.draw(screen)
        s_m1.draw(screen)

        t_lbl4 = FONT_LABEL.render("m₂  Mass 2", True, RED)
        screen.blit(t_lbl4, (px, ROW4_Y + (input_h - t_lbl4.get_height()) // 2))
        ti_m2.draw(screen)
        s_m2.draw(screen)

        #Length
        py.draw.line(screen, BORDER, (PANEL_X + 10, SEC_LEN_Y - 8), (PANEL_X + PANEL_W - 10, SEC_LEN_Y - 8), 1)
        t_sec_len = FONT_SMALL.render("LENGTH  (m)", True, DIM)
        screen.blit(t_sec_len, (PANEL_X + PANEL_W // 2 - t_sec_len.get_width() // 2, SEC_LEN_Y))

        t_lbl5 = FONT_LABEL.render("l₁  Rod 1", True, BLUE)
        screen.blit(t_lbl5, (px, ROW5_Y + (input_h - t_lbl5.get_height()) // 2))
        ti_l1.draw(screen)
        s_l1.draw(screen)

        t_lbl6 = FONT_LABEL.render("l₂  Rod 2", True, RED)
        screen.blit(t_lbl6, (px, ROW6_Y + (input_h - t_lbl6.get_height()) // 2))
        ti_l2.draw(screen)
        s_l2.draw(screen)

        hint = FONT_SMALL.render("Type value & press Enter", True, DIM)
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