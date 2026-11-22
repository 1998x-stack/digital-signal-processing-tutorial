from math import cos, pi

def sampled_cos(f, fs, n=9):
    return [cos(2*pi*f*k/fs) for k in range(n)]

def folded_frequency(f, fs):
    assert fs > 0
    return abs((f+fs/2)%fs-fs/2)

if __name__ == "__main__":
    a, b = sampled_cos(3,4), sampled_cos(1,4)
    assert all(abs(x-y)<1e-12 for x,y in zip(a,b))
    assert folded_frequency(3,4) == 1
    assert folded_frequency(3,8) == 3
    print("PASS: 3 Hz and 1 Hz alias under 4 Hz sampling")
