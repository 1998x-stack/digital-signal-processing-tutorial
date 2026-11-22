"""Odd-length, linear-phase lowpass using symmetric Hamming-windowed sinc."""
from math import pi, sin, cos
from cmath import exp
def lowpass(M, wc):
    assert M>=3 and M%2==1 and 0<wc<pi
    center=(M-1)/2
    taps=[]
    for n in range(M):
        m=n-center
        ideal=wc/pi if m==0 else sin(wc*m)/(pi*m)
        window=.54-.46*cos(2*pi*n/(M-1))
        taps.append(ideal*window)
    s=sum(taps)
    return [v/s for v in taps]
def response(h, w):
    return sum(v*exp(-1j*w*n) for n,v in enumerate(h))
if __name__=="__main__":
    h=lowpass(31,.35*pi)
    assert len(h)==31
    assert max(abs(a-b) for a,b in zip(h,reversed(h)))<1e-12
    assert abs(response(h,0)-1)<1e-12
    assert abs(response(h,pi))<.01
    for w in (.15*pi,.2*pi,.3*pi):
        demod=response(h,w)*exp(1j*w*15)
        assert abs(demod.imag)<1e-11
    print("PASS: symmetric Hamming FIR, DC gain, stopband and linear phase")
