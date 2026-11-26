"""第 27 章：晶振 ppm 频偏、正交混频下变频与 CIC 抽取增益（仅标准库）。"""
from math import pi, cos, sin, hypot


def ppm_offset(f0_hz, ppm):
    """晶振相对频率偏差导致的实际接收频偏（Hz）。"""
    return f0_hz * ppm * 1e-6


# 1090 MHz、±50 ppm -> 约 ±54.5 kHz 频偏
off50 = ppm_offset(1090e6, 50)
assert abs(off50 - 54500.0) < 1e-6, off50
assert abs(ppm_offset(2400e6, 10) - 24000.0) < 1e-6

# 正交混频下变频：实信号 cos(2π f0 n/fs) 乘以 exp(-j2π f0 n/fs)，平均后得复幅度 1/2
fs, f0, N = 2.4e6, 100e3, 2400          # f0/fs = 1/24，N 为整周期数
acc_re = acc_im = 0.0
for n in range(N):
    s = cos(2 * pi * f0 * n / fs)
    acc_re += s * cos(2 * pi * f0 * n / fs)
    acc_im += s * -sin(2 * pi * f0 * n / fs)
dc = hypot(acc_re, acc_im) / N
assert abs(dc - 0.5) < 1e-3, dc                 # 二倍频分量被整周期平均抵消

# CIC 抽取：阶数 N、比率 M 的直流增益为 M^N
def cic_dc(order, M, length=400):
    x = [1.0] * length
    for _ in range(order):
        for n in range(1, length):
            x[n] += x[n - 1]                       # 积分器
    y = [x[n] - (x[n - M] if n >= M else 0.0) for n in range(length)]
    for _ in range(order - 1):
        y = [y[n] - (y[n - M] if n >= M else 0.0) for n in range(length)]
    return y[-1]
for order, M in ((1, 4), (2, 4), (3, 8)):
    assert abs(cic_dc(order, M) - M ** order) < 1e-6, (order, M)

# 频偏换算到 DFT bin 间距：Δbin = 频偏 / (fs/N_fft)
bin_spacing = fs / 256
assert abs(off50 / bin_spacing - 5.813) < 0.01
print("PASS 27: 50 ppm@1090MHz=%.1f kHz，正交下变频直流幅度 %.4f，CIC 增益 M^N 校验通过，频偏≈%.2f bin"
      % (off50 / 1e3, dc, off50 / bin_spacing))
