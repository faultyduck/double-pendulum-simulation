import pygame as py
from lib import DoublePendulum
import sys
import math
from collections import deque

py.init()
WIDTH, HEIGHT = 800, 600
screen = py.display.set_mode((WIDTH, HEIGHT))
clock = py.time.Clock()
FPS = 60 
DT = 1/FPS
SCALE = 100
ORIGIN = (WIDTH // 2, HEIGHT // 3)

WHITE = (255, 255, 255)
BLACK = (30, 30, 30)
BLUE = (0, 120, 215)
RED = (220, 50, 50)
TRAIL_COLOR = (200, 200, 200)

def main():
    py.init()
    screen = py.display.set_mode((WIDTH, HEIGHT))
    py.display.set_caption("Double Pendulum Simulation")
    clock = py.time.Clock()

    pendulum = DoublePendulum(theta1=math.pi/2, theta2=math.pi/2) #call from lib/DoublePendulum.py
    trail = deque(maxlen=250)

    running = True
    while running:
        for event in py.event.get():
            if event.type == py.QUIT:
                running = False
            elif event.type == py.KEYDOWN:
                if event.key == py.K_ESCAPE:
                    running = False
        
        pendulum.step(DT)
        (x1, y1), (x2, y2) = pendulum.get_coordinates() #preset coordinates from lib/DoublePendulum.py

        screen.fill(WHITE)
        
        # Pygame y-axis is inverted (increases downwards); subtracting y keeps it looking correct
        pos1 = (int(ORIGIN[0] + x1 * SCALE), int(ORIGIN[1] - y1 * SCALE))
        pos2 = (int(ORIGIN[0] + x2 * SCALE), int(ORIGIN[1] - y2 * SCALE))
        
        trail.append(pos2)

        if len(trail) > 1:
            py.draw.lines(screen, TRAIL_COLOR, False, trail, 2)

        py.draw.line(screen, BLACK, ORIGIN, pos1, 4)
        py.draw.line(screen, BLACK, pos1, pos2, 4)
        py.draw.circle(screen, BLACK, ORIGIN, 6) # Pivot
        py.draw.circle(screen, BLUE, pos1, 12)   # Bob 1
        py.draw.circle(screen, RED, pos2, 12)    # Bob 2

        py.display.flip()
        clock.tick(FPS)

    py.quit()
    sys.exit()

if __name__ == "__main__":
    main()
