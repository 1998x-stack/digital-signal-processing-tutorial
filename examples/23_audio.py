"""第 23 章：RBJ 峰值双二阶与动态处理静态曲线（仅标准库，确定性断言）。"""
from math import pi, sin, cos, hypot, log10


def peaking(fs, f0, Q, gain_db):
    """RBJ Audio-EQ-Cookbook 峰值滤波器系数（归一化到 a0=1）。"""
    A = 10 ** (gain_db / 40.0)
    w0 = 2 * pi * f0 / fs
    alpha = sin(w0) / (2 * Q)
    b0, b1, b2 = 1 + alpha * A, -2 * cos(w0), 1 - alpha * A
    a0, a1, a2 = 1 + alpha / A, -2 * cos(w0), 1 - alpha / A
    return (b0 / a0, b1 / a0, b2 / a0, a1 / a0, a2 / a0)


def mag_db(coef, fs, f):
    b0, b1, b2, a1, a2 = coef
    w = 2 * pi * f / fs
    nr = b0 + b1 * cos(w) + b2 * cos(2 * w)
    ni = -b1 * sin(w) - b2 * sin(2 * w)
    dr = 1 + a1 * cos(w) + a2 * cos(2 * w)
    di = -a1 * sin(w) - a2 * sin(2 * w)
    return 20 * log10(hypot(nr, ni) / hypot(dr, di))


def compress_db(x_db, threshold, ratio):
    """静态输入-输出曲线：阈值以下 1:1，以上按 ratio 压缩。"""
    return x_db if x_db <= threshold else threshold + (x_db - threshold) / ratio


fs = 48000
coef = peaking(fs, 1000.0, 2.0, 12.0)
peak = mag_db(coef, fs, 1000.0)
assert abs(peak - 12.0) < 1e-6, peak                      # 峰值恰为设定增益
assert abs(mag_db(coef, fs, 0.0)) < 1e-9                   # 直流增益为 1（0 dB）
assert abs(mag_db(coef, fs, fs / 2.0)) < 1e-9              # Nyquist 增益为 1（0 dB）
# 峰值型 EQ 在中心频率处的线性增益应严格等于 10^(gain/20)
assert abs(10 ** (peak / 20.0) - 10 ** (12.0 / 20.0)) < 1e-6
# 压缩器：输入 -20 处输出仍为 -20；再抬 12 dB 只出来 3 dB（4:1）
assert abs(compress_db(-20.0, -20.0, 4.0) - (-20.0)) < 1e-9
assert abs(compress_db(-8.0, -20.0, 4.0) - (-17.0)) < 1e-9
# 限幅器：比率很大时输出趋近阈值，不超过天花板
ceil = compress_db(0.0, -0.1, 1e9)
assert ceil <= -0.1 + 1e-6, ceil
print("PASS 23: 峰值 %.4f dB，DC %.4f dB，Nyquist %.4f dB，限幅天花板 %.4f dBFS"
      % (peak, mag_db(coef, fs, 0.0), mag_db(coef, fs, fs / 2.0), ceil))
