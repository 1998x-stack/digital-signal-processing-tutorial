"""DFT convention, inverse, leakage, circular/linear convolution."""
from math import pi, cos, sin
def dft(x):
    N=len(x)
    return [sum(v*complex(cos(-2*pi*k*n/N),sin(-2*pi*k*n/N))
                for n,v in enumerate(x)) for k in range(N)]
def idft(X):
    N=len(X)
    return [sum(v*complex(cos(2*pi*k*n/N),sin(2*pi*k*n/N))
                for k,v in enumerate(X))/N for n in range(N)]
def convolution(x,h):
    out=[0]*(len(x)+len(h)-1)
    for i,a in enumerate(x):
        for j,b in enumerate(h):out[i+j]+=a*b
    return out
def circular(x,h):
    N=len(x)
    assert len(h)==N
    return [sum(x[m]*h[(n-m)%N] for m in range(N)) for n in range(N)]
if __name__=="__main__":
    x=[1,2,1,0];h=[1,1,1,1]
    assert convolution(x,h)==[1,3,4,4,3,1,0]
    assert circular(x,h)==[4,4,4,4]
    padded_x=x+[0]*3;padded_h=h+[0]*3
    result=idft([a*b for a,b in zip(dft(padded_x),dft(padded_h))])
    assert max(abs(result[i]-v) for i,v in enumerate(convolution(x,h)))<1e-10
    assert max(abs(v-w) for v,w in zip(idft(dft(x)),x))<1e-10
    assert abs(sum(abs(v)**2 for v in x)-sum(abs(v)**2 for v in dft(x))/len(x))<1e-10
    integer=[cos(2*pi*3*n/16) for n in range(16)]
    shifted=[cos(2*pi*3.5*n/16) for n in range(16)]
    assert abs(dft(integer)[4])<1e-10
    assert abs(dft(shifted)[4])>0.1
    print("PASS: DFT/IDFT, Parseval, leakage and convolution padding")
