"""第 24 章：星座距离、OFDM 频域均衡与 QPSK 判决（仅标准库，确定性断言）。"""
import math


def levels(m):
    half = (m - 1) / 2.0
    return [(i - half) * 2.0 for i in range(m)]


def normalize(m):
    """把每轴电平归一化到单位平均功率，返回最小相邻距离。"""
    L = levels(m)
    p = sum(x * x for x in L) / m
    return [x / p ** 0.5 for x in L], (L[1] - L[0]) / p ** 0.5


def min_distance(m):
    _, spacing = normalize(m)
    return spacing                       # 最近邻只在一个坐标上差一个间距


# QPSK(m=2)、16QAM(m=4)、64QAM(m=8)：归一化后最小距离之比
d2, d4, d8 = min_distance(2), min_distance(4), min_distance(8)
assert abs(d4 / d2 - 0.447) < 2e-3, d4 / d2
assert abs(d8 / d2 - 0.218) < 2e-3, d8 / d2
assert int(math.log2(64)) == 6        # 每符号 6 bit

# QPSK 判决：四个星座点 (±1±j)/√2 对应两个比特
qpsk = {0: -1 - 1j, 1: 1 - 1j, 2: -1 + 1j, 3: 1 + 1j}
pts = {k: v / (2 ** 0.5) for k, v in qpsk.items()}
for bits, s in pts.items():
    dec = (s.real > 0) + 2 * (s.imag > 0)            # 硬判决重建索引
    assert dec == bits, (bits, dec, s)

# OFDM 每个子载波单抽头均衡：已知信道 H 时，X = Y / H 精确恢复
H = [0.6 + 0.4j * (-1) ** k for k in range(8)]
X = [1 + 0j, -1 + 0j, 0 + 1j, 0 - 1j, 1 + 1j, -1 - 1j, 1 - 1j, -1 + 1j]
Y = [H[k] * X[k] for k in range(8)]
Xh = [Y[k] / H[k] for k in range(8)]
err = max(abs(Xh[k] - X[k]) for k in range(8))
assert err < 1e-12, err

# NCO 相位累加：频率控制字 FTW 决定输出频率 f = FTW/2^B · fs
B, fs, FTW = 32, 100e6, 2 ** 28
f_out = FTW / 2 ** B * fs
assert abs(f_out - fs / 16) < 1e-6, f_out
print("PASS 24: d16/dQPSK=%.3f d64/dQPSK=%.3f，QPSK 判决全对，OFDM 均衡误差 %.1e，NCO 输出 %.3f MHz"
      % (d4 / d2, d8 / d2, err, f_out / 1e6))
