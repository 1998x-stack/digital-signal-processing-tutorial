"""Iterative radix-2 DIT FFT; no numpy/scipy dependency."""
from math import pi, cos, sin
from cmath import exp
def radix2_dit(x):
    n=len(x)
    if n<1 or n & (n-1):raise ValueError("radix-2 requires power-of-two length")
    a=list(map(complex,x));bits=n.bit_length()-1
    for i in range(n):
        j=int(f"{i:0{bits}b}"[::-1],2)
        if j>i:a[i],a[j]=a[j],a[i]
    size=2
    while size<=n:
        half=size//2
        for base in range(0,n,size):
            for j in range(half):
                twiddle=exp(-2j*pi*j/size)
                even=a[base+j];odd=twiddle*a[base+j+half]
                a[base+j]=even+odd
                a[base+j+half]=even-odd
        size*=2
    return a
def direct_dft(x):
    n=len(x)
    return [sum(v*exp(-2j*pi*k*i/n) for i,v in enumerate(x)) for k in range(n)]
if __name__=="__main__":
    for n in (1,2,4,8,16):
        x=[complex(sin(.3*i),cos(.7*i)) for i in range(n)]
        assert max(abs(a-b) for a,b in zip(radix2_dit(x),direct_dft(x)))<1e-10
    try:radix2_dit([1]*6)
    except ValueError:pass
    else:raise AssertionError("radix-2 accepted non-power-of-two input")
    print("PASS: radix-2 FFT matches independent O(N^2) DFT")
