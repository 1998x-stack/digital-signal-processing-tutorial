"""First-order prewarped bilinear Butterworth lowpass."""
from math import pi,tan,cos,sin,sqrt
def design(fs,fc):
    assert fs>0 and 0<fc<fs/2
    omega_c=2*fs*tan(pi*fc/fs)
    feedback=(2*fs-omega_c)/(2*fs+omega_c)
    b0=omega_c/(2*fs+omega_c)
    return omega_c,feedback,b0
def magnitude(fs,f,feedback,b0):
    w=2*pi*f/fs
    numerator=b0*(1+complex(cos(-w),sin(-w)))
    denominator=1-feedback*complex(cos(-w),sin(-w))
    return abs(numerator/denominator)
if __name__=="__main__":
    fs=8000
    for fc in (400,1000,2400,3400):
        omega,a,b=design(fs,fc)
        assert abs(a)<1
        assert abs(magnitude(fs,0,a,b)-1)<1e-12
        assert abs(magnitude(fs,fc,a,b)-1/sqrt(2))<1e-12
    assert design(8000,1000)[0]>2*pi*1000
    print("PASS: prewarp cutoff, stable pole and half-power response")
