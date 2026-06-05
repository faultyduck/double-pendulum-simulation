import cupy as cp
import numpy as np
from .DoublePendulum import DoublePendulum


def get_lyapunov(th1_vals, th2_vals, epsilon, T, dt, checkpoints=None):
    dp = DoublePendulum()
    dp2 = DoublePendulum()

    th1 = cp.array(np.deg2rad(th1_vals), dtype=cp.float64)
    th2 = cp.array(np.deg2rad(th2_vals), dtype=cp.float64)
    w1 = cp.zeros_like(th1)
    w2 = cp.zeros_like(th1)

    # dp state
    dp.theta1, dp.theta2 = th1, th2
    dp.omega1, dp.omega2 = w1, w2

    # dp2 state
    dp2.theta1, dp2.theta2 = th1 + epsilon, th2.copy()
    dp2.omega1, dp2.omega2 = w1.copy(), w2.copy()

    checkpoints_set = {round(c, 5) for c in checkpoints} if checkpoints else set()
    score_sum = cp.zeros(th1.shape, dtype=cp.float64)
    results   = {}
    n_steps   = int(round(T / dt))

    for step in range(n_steps):
        # advance both
        dp._rk4(dt)
        dp2._rk4(dt)

        # measure gap
        d1 = dp2.theta1 - dp.theta1
        d2 = dp2.theta2 - dp.theta2
        d3 = dp2.omega1 - dp.omega1
        d4 = dp2.omega2 - dp.omega2
        gap = cp.sqrt(d1**2 + d2**2 + d3**2 + d4**2)
        gap = cp.maximum(gap, cp.float64(1e-30))

        # accumulate
        score_sum += cp.log(gap / epsilon)

        # renormalize, reset gap to epsilon keeping direction
        scale = epsilon / gap
        dp2.theta1 = dp.theta1 + d1 * scale
        dp2.theta2 = dp.theta2 + d2 * scale
        dp2.omega1 = dp.omega1 + d3 * scale
        dp2.omega2 = dp.omega2 + d4 * scale

        t_now = round((step + 1) * dt, 5)
        if t_now in checkpoints_set or t_now == round(T, 5):
            results[t_now] = (score_sum / t_now).get()

    return results