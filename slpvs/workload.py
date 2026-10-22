"""Backend workload model: M/M/c queue (Erlang C) added to the per-event latency."""
import math
import numpy as np


def erlang_c(lam, mu, c):
    """Probability that an arriving request waits (Erlang C)."""
    a = lam / mu
    rho = a / c
    if rho >= 1:
        return 1.0
    s = sum(a ** k / math.factorial(k) for k in range(c))
    top = a ** c / math.factorial(c) / (1 - rho)
    return top / (s + top)


def mean_wait(lam, mu, c):
    pc = erlang_c(lam, mu, c)
    return pc / (c * mu - lam) if c * mu > lam else float("inf")


def sample_wait(rng, lam, mu, c, size):
    """W_q = 0 w.p. 1-C, else Exp(c*mu - lam)."""
    pc = erlang_c(lam, mu, c)
    wait = rng.exponential(1.0 / (c * mu - lam), size)
    return np.where(rng.random(size) < pc, wait, 0.0)
