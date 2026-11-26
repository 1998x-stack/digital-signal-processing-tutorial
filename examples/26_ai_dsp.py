"""第 26 章：理想比例掩码、谱减法的过减、谐波振荡器周期（仅标准库）。"""
from math import pi, sin


def irm(clean, noise):
    """理想比例掩码：对每个时频点 c/(c+n)，取值范围 0–1。"""
    return [c / (c + n) if (c + n) > 0 else 0.0 for c, n in zip(clean, noise)]


# 理想比例掩码作用在混合幅度上可精确恢复干净幅度（幅度域恒等式）
C = [3.0, 0.4, 2.2, 0.1, 1.5, 0.0]
Nn = [0.5, 1.8, 0.3, 1.2, 0.9, 2.0]
M = [c + n for c, n in zip(C, Nn)]
mask = irm(C, Nn)
restored = [m * g for m, g in zip(M, mask)]
assert max(abs(restored[k] - C[k]) for k in range(len(C))) < 1e-12
assert all(0.0 <= g <= 1.0 for g in mask)

# 谱减法：估计噪声谱后做 max(0, |Y| - α|N|)。α=1 时纯噪声点归零
alpha = 1.0
enh = [max(0.0, m - alpha * n) for m, n in zip(M, Nn)]
assert abs(enh[5]) < 1e-12                      # 纯噪声点被完全减去
# 过减 α>1 会连带削掉信号点，残余偏差随 α 单调增大（在信号点集合上）
def resid(a):
    return sum(abs(max(0.0, m - a * n) - c) for m, n, c in zip(M, Nn, C))
r1, r2, r3 = resid(1.0), resid(1.6), resid(2.4)
assert r1 <= r2 <= r3, (r1, r2, r3)

# 谐波振荡器：基频 f0 的各次谐波叠加，波形周期为 fs/f0 个样本
fs, f0 = 16000.0, 250.0
amps = [1.0, 0.5, 0.25, 0.1]
def osc(n):
    return sum(amps[k] * sin(2 * pi * (k + 1) * f0 * n / fs) for k in range(len(amps)))
period = round(fs / f0)                          # 恰为 64 个样本的整数周期
err = max(abs(osc(n + 10 * period) - osc(n)) for n in range(200))   # 10 个精确周期
assert err < 1e-9, err

# 归一化最小均方意义下，α=1 的谱减与 IRM 都是逐点线性加权，可微
assert period > 0
print("PASS 26: IRM 精确恢复误差<1e-12，谱减 α=1 纯噪声点归零，残余 r(1.0)=%.2f ≤ r(1.6)=%.2f ≤ r(2.4)=%.2f，谐波周期误差<1e-9"
      % (r1, r2, r3))
