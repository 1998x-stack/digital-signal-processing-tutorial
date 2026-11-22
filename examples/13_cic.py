"""第 13 章：CIC、半带滤波器与多级抽取的确定性校验（仅用标准库）。"""
import math


def cic_impulse(M, N):
    """N 级 CIC 抽取器的冲激响应：等价于 (长度 M 全 1 序列) 的 N 次卷积。"""
    h = [1.0] * M
    for _ in range(N - 1):
        out = [0.0] * (len(h) + M - 1)
        for i, a in enumerate(h):
            for j in range(M):
                out[i + j] += a
        h = out
    return h


def halfband(N):
    """以中点为中心、截止 π/2 的对称半带低通（Hamming 窗）。要求 N ≡ 1 (mod 4)。"""
    assert (N - 1) % 4 == 0, "选择 N ≡ 1 (mod 4) 使中心下标为偶数"
    alpha = (N - 1) // 2
    wc = math.pi / 2
    h = []
    for n in range(N):
        m = n - alpha
        ideal = wc / math.pi if m == 0 else math.sin(wc * m) / (math.pi * m)
        window = 0.54 - 0.46 * math.cos(2 * math.pi * n / (N - 1))
        h.append(ideal * window)
    return h, alpha


def main():
    M, N = 8, 4
    h = cic_impulse(M, N)
    # 直流增益 = 冲激响应之和 = M^N
    assert abs(sum(h) - M ** N) < 1e-6, "CIC 直流增益应为 M^N"
    assert len(h) == M * N - (N - 1), "N 级卷积后的长度"
    print(f"CIC M={M}, N={N}: 冲激响应长度 {len(h)}，直流增益 {sum(h):.0f} = M^N")

    # 单级 CIC 就是长度 M 的滑动平均
    assert cic_impulse(M, 1) == [1.0] * M, "单级 CIC 必须等于长度 M 的移动平均"

    hb, alpha = halfband(13)
    assert abs(hb[alpha] - 0.5) < 1e-12, "半带中心系数应为 1/2"
    zero_taps = [abs(hb[alpha + 2 * k]) for k in (-3, -2, -1, 1, 2, 3)]
    assert max(zero_taps) < 1e-12, "半带每隔一个抽头（除中心）应为零"
    # H(z)+H(-z) 的系数：n=alpha 处为 1，其余约为 0
    s = [hb[n] * (1 + (-1) ** n) for n in range(len(hb))]
    assert abs(s[alpha] - 1.0) < 1e-9, "H(z)+H(-z) 应为 z^-alpha"
    assert max(abs(v) for i, v in enumerate(s) if i != alpha) < 1e-9
    print(f"半带 N=13: 中心 h[{alpha}]={hb[alpha]:.4f}，H(z)+H(-z) 仅剩 z^-{alpha}")

    # 多级抽取因子相乘
    stages = [64, 2, 2, 2, 2]
    prod = 1
    for s_ in stages:
        prod *= s_
    assert prod * 2.5 == 2560, "级联因子必须为 2560"
    assert 122_880_000 / 2560 == 48_000
    print(f"级联因子 {prod}×2.5 = {prod * 2.5:.0f}；122.88 MHz / 2560 = 48000 Hz")
    print("PASS: CIC、半带与多级抽取")


if __name__ == "__main__":
    main()
