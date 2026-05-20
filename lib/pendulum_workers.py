import numpy as np
from .DoublePendulum import DoublePendulum  
from .calc_lyapunov import get_lyapunov        

def compute_points(i, j, t1_deg, t2_deg, checkpoints, dt, epsilon):
    pend = DoublePendulum(
        theta1=np.deg2rad(t1_deg),
        theta2=np.deg2rad(t2_deg)
    )
    lyap_dict = get_lyapunov(
        pend, epsilon=epsilon,
        T=max(checkpoints), dt=dt,
        checkpoints=checkpoints
    )
    return i, j, lyap_dict