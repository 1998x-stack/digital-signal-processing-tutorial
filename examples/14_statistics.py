"""第 14 章：自相关、Wiener-Khinchin 与分段平均降方差的确定性校验（仅用标准库）。"""
import cmath
import math


def acf(x, tau, circular=True):
    n = len(x)
    if circular:
        return sum(x[i] * x[(i + tau) % n] for i in range(n)) / n
    return sum(x[i] * x[i + tau] for i in range(n - tau)) / n


def dft(x):
    n = len(x)
    return [sum(v * cmath.exp(-2j * math.pi * k * i / n) for i, v in enumerate(x)) for k in range(n)]


def lcg(n, seed=12345):
    out = []
    for _ in range(n):
        seed = (seed * 16807) % 2147483647
        out.append(seed / 2147483647 * 2 - 1)
    return out


def main():
    # 周期信号 x[n]=cos(2 pi n/8) 的循环 ACF 精确为 0.5 cos(2 pi tau/8)
    n = 512
    x = [math.cos(2 * math.pi * i / 8) for i in range(n)]
    assert abs(acf(x, 0) - 0.5) < 1e-12, "r[0] 应等于平均功率"
    for tau in range(1, 9):
        assert abs(acf(x, tau) - 0.5 * math.cos(2 * math.pi * tau / 8)) < 1e-9
        assert abs(acf(x, -tau) - acf(x, tau)) < 1e-9, "实信号 ACF 应为偶函数"
    print("周期信号 ACF 与 0.5cos(2pi tau/8) 一致；r[0]=%.3f" % acf(x, 0))

    # Wiener-Khinchin（离散循环形式）：DFT(ACF) == |X[k]|^2 / N
    r = [acf(x, tau) for tau in range(n)]
    R, X = dft(r), dft(x)
    err = max(abs(R[k] - abs(X[k]) ** 2 / n) for k in range(n))
    assert err < 1e-6, "DFT(自相关) 应等于周期图"
    print("Wiener-Khinchin 离散校验最大误差：%.2e" % err)

    # 白噪声：非零延迟的自相关接近 0
    w = lcg(2048)
    assert abs(acf(w, 0)) > 0.2, "白噪声 r[0] 应近似方差"
    assert max(abs(acf(w, tau)) for tau in range(1, 6)) < 0.1
    print("白噪声 r[0]=%.3f，|r[tau>0]| 均 < 0.1" % acf(w, 0))

    # 分段平均降低 PSD 估计的变异系数
    def cv(vals):
        mean = sum(vals) / len(vals)
        return (sum((v - mean) ** 2 for v in vals) / len(vals)) ** 0.5 / mean

    K, L = 8, 128
    segs = [lcg(L, seed=1000 + k) for k in range(K)]
    ps = [[abs(v) ** 2 for v in dft(s)] for s in segs]
    single = cv(ps[0])
    avg = cv([sum(ps[k][i] for k in range(K)) / K for i in range(L)])
    assert avg < single, "分段平均应降低变异系数"
    print(f"单段 cv={single:.3f}；{K} 段平均 cv={avg:.3f}（约 1/sqrt(K)={K ** -0.5:.3f}）")
    print("PASS: 自相关、Wiener-Khinchin 与 Welch 方差")


if __name__ == "__main__":
    main()
