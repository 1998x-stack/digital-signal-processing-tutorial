from math import pi, sin

def sample_sine(f_hz=2, fs_hz=16, count=9):
    """Uniform sampling without quantizing amplitudes."""
    assert fs_hz > 0 and count >= 0
    return [sin(2*pi*f_hz*n/fs_hz) for n in range(count)]

def quantize(x, delta=0.25):
    """Nearest-step quantization, without clipping."""
    assert delta > 0
    return round(x/delta)*delta

if __name__ == "__main__":
    x = sample_sine()
    assert len(x) == 9 and abs(x[0]) < 1e-12
    assert all(abs(quantize(v)-v) <= 0.125+1e-12 for v in x)
    print("PASS: sample and quantization error bound")
