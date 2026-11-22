"""第 11 章：滤波器结构的等价性与系数量化极点敏感度（仅用标准库，确定性）。"""
import cmath
from math import cos, pi, sqrt

B = [0.2, 0.3, -0.1, 0.05]          # 任意 FIR 系数
X = [1.0, 2.0, -1.0, 0.5, 0.0, 0.0, 0.0, 0.0]


def direct(x, b):
    return [sum(b[k] * x[n - k] for k in range(len(b)) if n - k >= 0) for n in range(len(x))]


def transposed(x, b):
    y, z = [], [0.0] * (len(b) + 1)
    for n in range(len(x)):
        for k in range(len(b)):
            z[k] = b[k] * x[n] + z[k + 1]
        y.append(z[0])
    return y


def poles(a1, a2):
    disc = a1 * a1 - 4 * a2
    if disc >= 0:
        return (complex((-a1 + sqrt(disc)) / 2), complex((-a1 - sqrt(disc)) / 2))
    re, im = -a1 / 2, sqrt(-disc) / 2
    return (complex(re, im), complex(re, -im))


def quantize(value, bits):
    scale = 2 ** bits
    return round(value * scale) / scale


def main():
    yd, yt = direct(X, B), transposed(X, B)
    assert all(abs(a - b) < 1e-12 for a, b in zip(yd, yt)), "直接型与转置型必须等价"
    print("直接型 = 转置型：", [round(v, 4) for v in yd])

    r, w0 = 0.98, 0.2 * pi
    a1, a2 = -2 * r * cos(w0), r * r
    exact = max(abs(p) for p in poles(a1, a2))
    for bits in (8, 10, 12):
        qa1, qa2 = quantize(a1, bits), quantize(a2, bits)
        rq = max(abs(p) for p in poles(qa1, qa2))
        # 共轲复极点时半径恰为 sqrt(a2)
        assert abs(rq - sqrt(qa2)) < 1e-12, "复极点半径应等于 sqrt(a2)"
        estimate = (qa2 - a2) / (2 * r)          # 式(6) 一阶估计
        rel = abs((rq - exact) - estimate) / max(abs(rq - exact), 1e-12)
        assert rel < 0.05, f"{bits} bit 一阶估计偏差过大"
        print(f"{bits:>2} bit: a2={qa2:.6f}  半径={rq:.6f}  实际偏移={rq-exact:+.6f}  一阶估计={estimate:+.6f}")

    # 高 Q 时同样的 a2 误差带来更大半径偏移：不同 r 对比
    for rr in (0.90, 0.98):
        aa2 = rr * rr
        err = abs(quantize(aa2, 6) - aa2)
        print(f"r={rr}: 6 bit 下 |Δa2|={err:.6f} → 一阶 |Δr|≈{err/(2*rr):.6f}")
    print("PASS: 结构等价与量化敏感度")


if __name__ == "__main__":
    main()
