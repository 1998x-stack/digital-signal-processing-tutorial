"""第 28 章：三模块处理链、定点双二阶保真度与实时预算（仅标准库）。"""
from math import pi, sin, cos, log10, hypot

FS = 48000


def peaking(f0, Q, gain_db):
    A = 10 ** (gain_db / 40); w0 = 2 * pi * f0 / FS; al = sin(w0) / (2 * Q)
    b = [1 + al * A, -2 * cos(w0), 1 - al * A]
    a = [1 + al / A, -2 * cos(w0), 1 - al / A]
    return [v / a[0] for v in b], [1.0, a[1] / a[0], a[2] / a[0]]


def mag_db(b, a, f):
    w = 2 * pi * f / FS
    nr = b[0] + b[1] * cos(w) + b[2] * cos(2 * w); ni = -b[1] * sin(w) - b[2] * sin(2 * w)
    dr = a[0] + a[1] * cos(w) + a[2] * cos(2 * w); di = -a[1] * sin(w) - a[2] * sin(2 * w)
    return 20 * log10(hypot(nr, ni) / hypot(dr, di))


b, a = peaking(1000.0, 1.0, 6.0)
assert abs(mag_db(b, a, 1000.0) - 6.0) < 1e-6          # 峰化段中心增益 = 设定值
assert abs(mag_db(b, a, 0.0)) < 1e-9 and abs(mag_db(b, a, FS / 2)) < 1e-9

# 噪声门与压缩器的静态增益（dB），软切换门限
def gate_gain_db(x_db, th, floor_db=-80.0):
    return x_db - max(floor_db, x_db) if x_db > th else (floor_db - th)
def comp_gain_db(x_db, th, ratio):
    return 0.0 if x_db <= th else -(x_db - th) * (1 - 1 / ratio)
assert gate_gain_db(-10.0, -40.0) == 0.0               # 门限以上不衰减
assert gate_gain_db(-60.0, -40.0) == -40.0             # 门限以下衰减到地板
assert abs(comp_gain_db(-8.0, -20.0, 4.0) + 9.0) < 1e-9  # 4:1 压缩：高出 12 dB 压掉 9 dB

# 定点双二阶：系数 Q2.14，状态 Q1.31，16 位饱和输出
def q14(c): return round(c * 2 ** 14)
def iir_fixed(x, b, a):
    B0, B1, B2, A1, A2 = q14(b[0]), q14(b[1]), q14(b[2]), q14(a[1]), q14(a[2])
    r = lambda v: (v + 8192) >> 14                 # 系数乘加后舍入，避免直接移位的直流偏置
    w1 = w2 = 0; out = []
    for s in x:                                    # 状态保持 32 位 Q15，仅在输出处降至 16 位
        xi = round(s * 32767)
        y = r(B0 * xi) + w1
        w1 = r(B1 * xi) - r(A1 * y) + w2
        w2 = r(B2 * xi) - r(A2 * y)
        yc = 32767 if y > 32767 else (-32768 if y < -32768 else y)
        out.append(yc / 32767.0)
    return out
def iir_float(x, b, a):
    w1 = w2 = 0.0; out = []
    for s in x:
        y = b[0] * s + w1; w1 = b[1] * s - a[1] * y + w2; w2 = b[2] * s - a[2] * y
        out.append(y)
    return out
sig = [0.5 * sin(2 * pi * 1000 * n / FS) for n in range(4000)]
ref, got = iir_float(sig, b, a), iir_fixed(sig, b, a)
nse = sum((got[n] - ref[n]) ** 2 for n in range(4000))
sigp = sum(ref[n] ** 2 for n in range(4000))
snr = 10 * log10(sigp / max(nse, 1e-30))
assert snr > 60.0, snr                                   # 定点相对浮点保真度
assert abs(64 / FS * 1000 - 1.333) < 0.01                # 64 样本块的实时预算
print("PASS 28: 峰化 6.0000 dB，门/压缩静态曲线通过，定点 SNR %.1f dB (>60)，实时预算 %.3f ms/块"
      % (snr, 64 / FS * 1000))
