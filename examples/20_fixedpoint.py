"""第 20 章：Q 格式、量化、MAC 与极限环（仅标准库）。

验证四件事：
1. 舍入量化误差不超过半个 LSB，截断误差有 −½ LSB 的直流偏置；
2. 满幅正弦的 SQNR 近似满足 6.02·N + 1.76 dB（均匀量化白噪声模型）；
3. Q15 × Q15 = Q30，右移 15 位后回到 Q15，增益正确；
4. 带舍入的一阶 IIR 冲激响应会停在非零极限环，而浮点衰减到零。
"""
from math import sin, pi, sqrt, log10, floor

def q_round(x, nbits=16):
    step = 2.0 ** (nbits - 1)
    return round(x * step) / step

def q_trunc(x, nbits=16):
    step = 2.0 ** (nbits - 1)
    return floor(x * step) / step

def lcg(n, seed=11):
    out, s = [], seed
    for _ in range(n):
        s = (s * 16807) % 2147483647
        out.append(s / 2147483647 * 2 - 1)
    return out


def main():
    LSB = 2.0 ** -15
    vals = [0.37 * v for v in lcg(4000, 2025)]
    er = [q_round(v) - v for v in vals]
    et = [q_trunc(v) - v for v in vals]
    print("舍入：max|e| =", max(abs(e) for e in er), " 上界 Δ/2 =", LSB / 2)
    assert max(abs(e) for e in er) <= LSB / 2 + 1e-12
    mean_t = sum(et) / len(et)
    print("截断：均值 =", round(mean_t, 8), " 预期 ≈ −Δ/2 =", -LSB / 2)
    assert -LSB < min(et) and max(et) <= 1e-12
    assert abs(mean_t + LSB / 2) < LSB / 20, "截断引入约 −½ LSB 的直流偏置"

    for N in (12, 16):
        step = 2.0 ** (N - 1)
        n = 4096
        x = [sin(2 * pi * i / n) for i in range(n)]
        e = [v - round(v * step) / step for v in x]
        px = sum(v * v for v in x) / n
        pe = sum(v * v for v in e) / n
        sqnr = 10 * log10(px / pe)
        print(f"N={N}：SQNR 实测 {sqnr:.2f} dB，公式 {6.02 * N + 1.76:.2f} dB")
        assert abs(sqnr - (6.02 * N + 1.76)) < 2.0, "均匀量化白噪声模型近似成立"

    a_int, b_int = 16384, 8192        # 0.5 与 0.25 的 Q15
    prod = a_int * b_int             # Q30
    assert prod >> 15 == 4096, "Q30 右移 15 位回到 Q15"
    print("0.5 × 0.25：Q30 =", prod, " → Q15 =", prod >> 15, "（值 =", (prod >> 15) / 32768, "）")

    a_q = round(0.9 * 32768)
    y_float, y_fixed = 0.5, 16384
    for _ in range(200):
        y_float *= 0.9
        y_fixed = round(a_q * y_fixed / 32768)
    print("浮点 200 步后 =", y_float, " 定点 =", y_fixed, "（约", y_fixed / 32768, "）")
    assert y_fixed != 0, "带舍入的一阶 IIR 停在非零极限环（死区）"
    assert abs(y_float) < 1 / 32768, "浮点则衰减到量化步长以下"

    hi = 7 * 4096                    # Q4.12 中的 +7
    raw = hi + 4096
    sat = min(raw, 32767)
    wrap = raw - 65536
    print("+7 + 1：饱和 →", sat / 4096, " 环绕 →", wrap / 4096)
    assert sat == 32767 and wrap == -32768, "饱和钳位，环绕翻转到相反满量程"
    print("PASS: 20 章量化、SQNR、MAC 与极限环均通过")


if __name__ == "__main__":
    main()
