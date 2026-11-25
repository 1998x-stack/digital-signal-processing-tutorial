"""第 18 章：FFT 的时间盲区与 STFT 的时频定位（仅标准库）。"""
from math import sin, cos, pi

N, FS = 256, 256.0
F1, F2 = 32.0, 64.0           # 两个分量，分别只出现在前/后半段


def build():
    x = []
    for n in range(N):
        v = sin(2 * pi * F1 * n / FS) if n < N // 2 else sin(2 * pi * F2 * n / FS)
        x.append(v)
    return x


def dft_mag(x):
    n0 = len(x)
    return [abs(sum(x[n] * complex(cos(2 * pi * k * n / n0), -sin(2 * pi * k * n / n0))
                    for n in range(n0))) for k in range(n0)]


def hann(L):
    return [0.5 - 0.5 * cos(2 * pi * n / (L - 1)) for n in range(L)]


def stft(x, L, hop):
    """返回 (帧起点, 单边幅度谱)；频率分辨率为 FS/L。"""
    w = hann(L)
    frames = []
    for m in range(0, len(x) - L + 1, hop):
        seg = [x[m + n] * w[n] for n in range(L)]
        frames.append((m, dft_mag(seg)[:L // 2 + 1]))
    return frames


def band(spec, lo, hi, res):
    """谱中落在 [lo, hi) Hz 的能量。"""
    return sum(spec[k] ** 2 for k in range(len(spec)) if lo <= k * res < hi)


def main():
    x = build()
    X = dft_mag(x)
    g1, g2 = X[32], X[64]
    print("整段 DFT：32 Hz 分量幅度 =", round(g1, 1), " 64 Hz 分量幅度 =", round(g2, 1))
    assert g1 > 20 and g2 > 20, "整段 DFT 同时看到两个分量，但看不到它们出现的时间"

    L, hop = 32, 16
    res = FS / L
    frames = stft(x, L, hop)
    early_ok = late_ok = 0
    for m, spec in frames:
        e1 = band(spec, 24, 40, res)      # 32 Hz 附近
        e2 = band(spec, 56, 72, res)      # 64 Hz 附近
        if m + L // 2 < N // 2 and e1 > e2:
            early_ok += 1
        if m >= N // 2 and e2 > e1:
            late_ok += 1
    print(f"STFT(L={L}, hop={hop})：频率分辨率 {res} Hz；前段定位正确的帧数 =", early_ok,
          " 后段 =", late_ok)
    assert early_ok >= 5 and late_ok >= 5, "STFT 应把 32 Hz 定位在前段、64 Hz 定位在后段"

    Llong = 128
    resl = FS / Llong
    long_frames = stft(x, Llong, hop)
    both = sum(1 for m, s in long_frames
               if band(s, 24, 40, resl) > 0 and band(s, 56, 72, resl) > 0)
    print(f"L={Llong} 时长窗：频率分辨率 {resl} Hz，同时含两个分量的帧数 =", both)
    assert both >= 1, "长窗跨越分界时，时间定位被模糊，前后分量会同时出现"
    print("PASS: 整段 DFT 无时间信息，STFT 用短窗恢复时间定位，长窗模糊时间")


if __name__ == "__main__":
    main()
