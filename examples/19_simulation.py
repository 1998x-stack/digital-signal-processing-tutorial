"""第 19 章：仿真参考模型、频率约定与三级验证（仅标准库）。

验证三件事：
1. 窗函数法 FIR 的“截止频率”对应 -6 dB 半幅点，巴特沃斯对应 -3 dB 半功率点；
2. 因果滤波有 (M-1)/2 个样本群延迟，零相位正反滤波把延迟抵消但阶数翻倍；
3. 定点系数量化误差不超过半个量化步长，可直接用于三级验证的定点模型。
"""
from math import sin, cos, pi, sqrt, log10

FS = 800.0


def mag_at(h, w):
    """FIR 在数字角频率 w 处的幅度（|H(e^{jw})|）。"""
    re = sum(c * cos(w * n) for n, c in enumerate(h))
    im = -sum(c * sin(w * n) for n, c in enumerate(h))
    return sqrt(re * re + im * im)


def lowpass_fir(wc, taps=65):
    """理想 sinc × Hamming 窗，并归一化到单位直流增益（firwin 的做法）。"""
    M = taps
    h = []
    for n in range(M):
        m = n - (M - 1) / 2
        ideal = wc / pi if abs(m) < 1e-12 else sin(wc * m) / (pi * m)
        win = 0.54 - 0.46 * cos(2 * pi * n / (M - 1))
        h.append(ideal * win)
    dc = sum(h)
    return [c / dc for c in h]


def butter1_mag(wc, w):
    """一阶数字巴特沃斯低通（T=2 双线性，预畸变 Omega_c=tan(wc/2)）在 w 处幅度。"""
    O = __import__("math").tan(wc / 2)
    b0 = b1 = O / (O + 1)
    a1 = (O - 1) / (O + 1)
    re = b0 + b1 * cos(w)
    im = -b1 * sin(w)
    dr = 1 + a1 * cos(w)
    di = -a1 * sin(w)
    return sqrt(re * re + im * im) / sqrt(dr * dr + di * di)


def conv(a, b):
    y = [0.0] * (len(a) + len(b) - 1)
    for i, ai in enumerate(a):
        for j, bj in enumerate(b):
            y[i + j] += ai * bj
    return y


def quantize(c, bits=16):
    """Q(bits-1) 格式：把系数舍入到 2^-(bits-1) 的网格。"""
    step = 2.0 ** (bits - 1)
    return round(c * step) / step


def lcg(n, seed=7):
    out, s = [], seed
    for _ in range(n):
        s = (s * 16807) % 2147483647
        out.append(s / 2147483647 * 2 - 1)
    return out


def main():
    wc = 0.4 * pi
    h = lowpass_fir(wc)
    g0, gc = mag_at(h, 0.0), mag_at(h, wc)
    print("FIR 直流增益 =", round(g0, 4), " 截止点幅度 =", round(gc, 4))
    assert abs(g0 - 1) < 1e-6, "直流增益应归一化为 1"
    assert abs(gc - 0.5) < 0.05, "firwin 截止点约对应 -6 dB 半幅点（0.5）"

    gb = butter1_mag(wc, wc)
    print("巴特沃斯截止点幅度 =", round(gb, 4), "（目标 0.7071）")
    assert abs(gb - 1 / sqrt(2)) < 1e-3, "巴特沃斯临界点对应 -3 dB 半功率点"

    taps = 33
    h33 = lowpass_fir(0.3 * pi, taps)
    nd = (taps - 1) // 2
    x = [0.0] * 80
    x[40] = 1.0
    y = conv(h33, x)
    pk = max(range(len(y)), key=lambda i: abs(y[i]))
    print("因果滤波峰值位置 =", pk, "（输入在 40，群延迟 =", nd, "）")
    assert pk == 40 + nd, "因果 FIR 群延迟为 (M-1)/2 个样本"
    yz = conv(h33, conv(h33, x))
    yz = yz[2 * nd:2 * nd + len(x)]
    pkz = max(range(len(yz)), key=lambda i: abs(yz[i]))
    support = [i for i, v in enumerate(yz) if abs(v) > 1e-9]
    print("零相位滤波峰值位置 =", pkz, " 非零支撑长度 =", len(support))
    assert pkz == 40, "正反两次滤波抵消了相位延迟"
    assert len(support) == 2 * (taps - 1) + 1, "零相位滤波等效阶数翻倍"

    hq = [quantize(c, 16) for c in h]
    max_err = max(abs(a - b) for a, b in zip(h, hq))
    print("Q15 量化最大系数误差 =", max_err, " 上界 2^-16 =", 2 ** -16)
    assert max_err <= 2 ** -16 + 1e-15, "未过载时量化误差不超过半个量化步长"
    assert abs(mag_at(hq, wc) - mag_at(h, wc)) < 0.01, "Q15 系数对幅度响应影响很小"

    n = 4096
    sig = [sin(2 * pi * 50 * i / FS) for i in range(n)]
    noise = lcg(n, 2024)
    target_db = 10.0
    var_s = sum(v * v for v in sig) / n
    var_n = sum(v * v for v in noise) / n
    scale = sqrt(var_s / (10 ** (target_db / 10)) / var_n)
    meas = [sig[i] + scale * noise[i] for i in range(n)]
    var_e = sum((scale * noise[i]) ** 2 for i in range(n)) / n
    snr = 10 * log10(var_s / var_e)
    print("目标 SNR = 10 dB，实测 =", round(snr, 3), "dB")
    assert abs(snr - target_db) < 0.05, "SNR 标定公式与实测一致"
    print("PASS: 19 章频率约定、群延迟与量化上界均通过")


if __name__ == "__main__":
    main()
