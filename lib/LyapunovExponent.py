import numpy as np
from .DoublePendulum import DoublePendulum

def get_lyapunov(pendulum, epsilon, T, dt):
    scores = []
    pendulum_2 = DoublePendulum(
            g=pendulum.g,
            m1=pendulum.m1, m2=pendulum.m2,
            l1=pendulum.l1, l2=pendulum.l2,
            theta1=pendulum.theta1 + epsilon, theta2=pendulum.theta2,
            omega1=pendulum.omega1, omega2=pendulum.omega2
        )
    for _ in np.arange(0, T, dt):
        # advance both simulations
        pendulum.step(dt)
        pendulum_2.step(dt) 

        # measure gap
        gap = np.sqrt(
            (pendulum_2.theta1-pendulum.theta1)**2 + 
            (pendulum_2.theta2-pendulum.theta2)**2 + 
            (pendulum_2.omega1-pendulum.omega1)**2 + 
            (pendulum_2.omega2-pendulum.omega2)**2
        )

        # accumulate ln(gap/epsiln)
        scores.append(np.log(gap / epsilon))
        
        # renormalize, reset gap to epsilon while keeping direction
        scale = epsilon / gap

        d1 = pendulum_2.theta1 - pendulum.theta1
        d2 = pendulum_2.theta2 - pendulum.theta2
        d3 = pendulum_2.omega1 - pendulum.omega1
        d4 = pendulum_2.omega2 - pendulum.omega2
        
        pendulum_2.theta1 = pendulum.theta1 + d1 * scale
        pendulum_2.theta2 = pendulum.theta2 + d2 * scale
        pendulum_2.omega1 = pendulum.omega1 + d3 * scale
        pendulum_2.omega2 = pendulum.omega2 + d4 * scale

    return np.sum(scores)/T
