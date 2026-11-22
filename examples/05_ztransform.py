def causal_impulse(a, count=100):
    """h[n] = a**n u[n], evaluated for n >= 0."""
    return [a**n for n in range(count)]

def is_bibo_stable(a):
    """One-sided first-order system, including negative real poles."""
    return abs(a) < 1

if __name__ == "__main__":
    assert is_bibo_stable(0.7)
    assert is_bibo_stable(-0.8)
    assert not is_bibo_stable(1)
    assert not is_bibo_stable(1.05)
    assert abs(sum(causal_impulse(0.7))-1/(1-0.7))<1e-10
    print("PASS: first-order causal ROC/BIBO condition")
