"""第 17 章：周期图与 Burg AR 谱在近邻频率上的可分辨性对照（仅标准库）。"""
from math import sin, cos, pi

N, FS = 64, 64.0
F1, F2 = 10.0, 10.6          # Δf = 0.6 Hz < FS/N = 1.0 Hz


def lcg(n, seed):
    out, s = [], seed
    for _ in range(n):
        s = (s * 16807) % 2147483647
        out.append(s / 2147483647 * 2 - 1)
    return out


def build(noise=0.1, seed=1234):
    nz = lcg(N, seed)
    return [sin(2 * pi * F1 * n / FS) + sin(2 * pi * F2 * n / FS) + noise * nz[n]
            for n in range(N)]


def periodogram(x):
    """矩形窗周期图：|DFT|²/N，只在 k=0..N/2 上取值。"""
    out = []
    for k in range(N // 2 + 1):
        re = sum(v * cos(2 * pi * k * n / len(x)) for n, v in enumerate(x))
        im = -sum(v * sin(2 * pi * k * n / len(x)) for n, v in enumerate(x))
        out.append((re * re + im * im) / len(x))
    return out


def peaks(seq, scale, thresh):
    mx = max(abs(v) for v in seq)
    return [i * scale for i in range(1, len(seq) - 1)
            if seq[i] > seq[i - 1] and seq[i] >= seq[i + 1] and seq[i] > thresh * mx]


def burg(x, p):
    """Burg 递推：返回 AR 系数 a[1..p]、反射系数与预测误差功率。"""
    f, b = x[:], x[:]
    a = [[0.0] * (p + 1) for _ in range(p + 1)]
    kref = []
    err = sum(v * v for v in x) / len(x)
    for m in range(1, p + 1):
        num = -2 * sum(f[n] * b[n - 1] for n in range(m, len(x)))
        den = sum(f[n] ** 2 + b[n - 1] ** 2 for n in range(m, len(x)))
        km = num / den
        kref.append(km)
        a[m][m] = km
        for i in range(1, m):
            a[m][i] = a[m - 1][i] + km * a[m - 1][m - i]
        err *= 1 - km * km
        nf, nb = f[:], b[:]
        for n in range(len(x) - 1, m - 1, -1):
            nf[n] = f[n] + km * b[n - 1]
            nb[n] = b[n - 1] + km * f[n]
        f, b = nf, nb
    return a[p][1:p + 1], kref, err


def ar_spectrum(a, err, points=1024):
    """AR 谱：σ²/|1 + Σ a[k] e^{-jw(k+1)}|²，返回 (频率, 谱值)。"""
    out = []
    for i in range(points + 1):
        w = pi * i / points
        re = 1 + sum(a[k] * cos(w * (k + 1)) for k in range(len(a)))
        im = -sum(a[k] * sin(w * (k + 1)) for k in range(len(a)))
        out.append((0.5 * i / points * FS, err / (re * re + im * im)))
    return out


def main():
    x = build(noise=0.1)
    per = periodogram(x)
    per_pk = peaks(per, FS / N, 0.25)

    a, kref, err = burg(x, 16)
    ar = ar_spectrum(a, err)
    freqs = [f for f, _ in ar]
    vals = [v for _, v in ar]
    ar_pk = peaks(vals, freqs[1] - freqs[0], 0.30)

    print(f"两个正弦：{F1} Hz 与 {F2} Hz，间距 {F2 - F1} Hz < FS/N = {FS / N} Hz")
    print("周期图峰值（Hz）：", [round(f, 2) for f in per_pk])
    print("Burg(p=16) AR 谱峰值（Hz）：", [round(f, 2) for f in ar_pk])
    print("反射系数绝对值最大值：", round(max(abs(v) for v in kref), 3))

    assert len(per_pk) == 1, "周期图无法分辨间隔小于 FS/N 的两个分量"
    assert len(ar_pk) >= 2, "Burg AR 谱应能分辨这两个分量"
    assert max(ar_pk) - min(ar_pk) > 0.4, "两个峰应明显分开"
    assert all(abs(v) < 1 for v in kref), "Burg 反射系数应满足 |k|<1，保证 AR 稳定"
    print("PASS: 周期图合并为单峰，Burg AR 谱分辨出双峰且反射系数均 |k|<1")


if __name__ == "__main__":
    main()
