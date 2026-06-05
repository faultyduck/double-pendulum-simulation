import numpy as np
import cupy as cp
from scipy.integrate import solve_ivp

# https://physics.umd.edu/hep/drew/pendulum2.html
class DoublePendulum:
    def __init__(
        self, g=9.81,
        m1=1.0, m2=1.0,
        l1=1.0, l2=1.0,
        theta1=30.0, theta2=0.0,
        omega1=0.0, omega2=0.0,
    ):
        self.g = g
        self.m1 = m1
        self.m2 = m2
        self.l1 = l1
        self.l2 = l2
        self.theta1 = theta1
        self.theta2 = theta2
        self.omega1 = omega1
        self.omega2 = omega2

    def get_coordinates(self):
        x1 = self.l1 * np.sin(self.theta1)
        y1 = -self.l1 * np.cos(self.theta1)
        x2 = x1 + self.l2 * np.sin(self.theta2)
        y2 = y1 - self.l2 * np.cos(self.theta2)
        return (x1, y1), (x2, y2)

    def get_dcoordinates(self):
        dx1 = self.l1 * self.omega1 * np.cos(self.theta1)
        dy1 = self.l1 * self.omega1 * np.sin(self.theta1)
        dx2 = dx1 + self.l2 * self.omega2 * np.cos(self.theta2)
        dy2 = dy1 + self.l2 * self.omega2 * np.sin(self.theta2)
        return (dx1, dy1), (dx2, dy2)

    def sum_ke(self):
        dxy1, dxy2 = self.get_dcoordinates()
        dx1, dy1 = dxy1
        dx2, dy2 = dxy2
        return 0.5*self.m1*(dx1**2 + dy1**2) + 0.5*self.m2*(dx2**2 + dy2**2)

    def sum_pe(self):
        xy1, xy2 = self.get_coordinates()
        x1, y1 = xy1
        x2, y2 = xy2
        return self.m1*self.g*y1 + self.m2*self.g*y2

    def _derivs(self, theta1, theta2, omega1, omega2, xp=np):
        M = self.m1 + self.m2
        delta = theta1 - theta2
        alpha = M - self.m2 * xp.sin(delta)**2
        num1 = (
            -xp.sin(delta) * (self.m2*self.l1*omega1**2*xp.cos(delta)
                              + self.m2*self.l2*omega2**2)
            - self.g*(M*xp.sin(theta1) - self.m2*xp.sin(theta2)*xp.cos(delta))
        ) # -- Equation 6
        num2 = (
            xp.sin(delta) * (M*self.l1*omega1**2
                             + self.m2*self.l2*omega2**2*xp.cos(delta))
            + self.g*(M*xp.sin(theta1)*xp.cos(delta) - M*xp.sin(theta2))
        ) # -- Equation 7
        return omega1, omega2, num1/(self.l1*alpha), num2/(self.l2*alpha)

    def _rk4(self, dt):
        th1, th2, w1, w2 = self.theta1, self.theta2, self.omega1, self.omega2
        d1 = self._derivs(th1, th2, w1, w2, xp=cp)
        d2 = self._derivs(*(s + dt/2*k for s, k in zip((th1,th2,w1,w2), d1)), xp=cp)
        d3 = self._derivs(*(s + dt/2*k for s, k in zip((th1,th2,w1,w2), d2)), xp=cp)
        d4 = self._derivs(*(s + dt   *k for s, k in zip((th1,th2,w1,w2), d3)), xp=cp)
        self.theta1, self.theta2, self.omega1, self.omega2 = tuple(
            s + dt/6*(k1+2*k2+2*k3+k4)
            for s,k1,k2,k3,k4 in zip((th1,th2,w1,w2),d1,d2,d3,d4)
        )


    def _derivs_flat(self, t, state): # t unused, but scipy needs it
        return self._derivs(*state)

    def step(self, dt):
        sol = solve_ivp(
            self._derivs_flat,
            t_span=(0, dt),
            y0=[self.theta1, self.theta2, self.omega1, self.omega2],
            method='RK45',
            max_step=dt,
        )
        self.theta1, self.theta2, self.omega1, self.omega2 = sol.y[:, -1]