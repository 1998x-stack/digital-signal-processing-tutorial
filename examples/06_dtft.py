"""DTFT and moving-average response, using standard-library complex arithmetic."""
from math import pi, cos, sin
def dtft(h, omega):
    return sum(value*complex(cos(-omega*n), sin(-omega*n))
               for n,value in enumerate(h))
if __name__ == "__main__":
    h=[1/3]*3
    assert abs(dtft(h,0)-1)<1e-12
    assert abs(dtft(h,2*pi/3))<1e-12
    assert abs(abs(dtft(h,pi))-1/3)<1e-12
    for omega in (0.2,0.9,2.7):
        assert abs(dtft(h,omega)-dtft(h,omega+2*pi))<1e-12
    print("PASS: 2pi periodic DTFT and 3-point moving average")
