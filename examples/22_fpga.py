"""第 22 章：CORDIC、分布式算法 FIR 与转置型 FIR（仅标准库）。"""
from math import sin, cos, atan, sqrt

# CORDIC 增益 K = ∏ sqrt(1 + 2^(−2i))，补偿用 1/K
_K = 1.0
for _i in range(24):
    _K *= sqrt(1 + 2.0 ** (-2 * _i))
INV_K = 1.0 / _K


def cordic(theta, iters):
    """只用移位、加法与查表逼近 cos/sin。"""
    atan_t = [atan(2.0 ** -i) for i in range(iters)]
    x, y, z = INV_K, 0.0, theta
    for i in range(iters):
        s = 1.0 if z >= 0 else -1.0
        x, y = x - s * y * 2.0 ** -i, y + s * x * 2.0 ** -i
        z -= s * atan_t[i]
    return x, y


def fir_direct(x, h):
    y = [0.0] * (len(x) + len(h) - 1)
    for i, v in enumerate(x):
        for j, c in enumerate(h):
            y[i + j] += v * c
    return y


def da_fir(x, c, bits=16):
    """分布式算法：用 LUT 预存系数组合的部分和，逐位累加。"""
    N = len(c)
    lut = [sum(c[k] for k in range(N) if (idx >> k) & 1) for idx in range(1 << N)]
    out = []
    for n in range(len(x)):
        w = [x[n - k] if n - k >= 0 else 0 for k in range(N)]
        acc = 0
        for b in range(bits - 1):
            acc += lut[sum(((w[k] >> b) & 1) << k for k in range(N))] << b
        acc -= lut[sum(((w[k] >> (bits - 1)) & 1) << k for k in range(N))] << (bits - 1)
        out.append(acc)
    return out


def fir_transposed(x, h):
    """转置型：寄存器分隔加法器，关键路径与阶数无关。"""
    M = len(h)
    z = [0.0] * max(0, M - 1)
    y = []
    for v in x:
        out = h[0] * v + (z[0] if M > 1 else 0.0)
        for i in range(M - 2):
            z[i] = h[i + 1] * v + z[i + 1]
        if M > 1:
            z[M - 2] = h[M - 1] * v
        y.append(out)
    return y


def main():
    for iters in (8, 12):
        err = max(abs(cordic(t, iters)[1] - sin(t)) for t in
                  [-1.4, -0.7, 0.0, 0.5, 1.0, 1.4])
        print(f"CORDIC {iters} 次迭代：最大 |sin 误差| = {err:.2e}")
    assert max(abs(cordic(t, 12)[1] - sin(t)) for t in [-1.4, 0.0, 1.4]) < 1e-3
    assert abs(cordic(0.0, 16)[0] - 1.0) < 1e-3, "CORDIC 增益补偿后 cos(0)≈1"

    c = [3, -2, 5, 1]                     # 整数系数，便于精确比对
    x = [7, -3, 11, 4, -6, 9, 2, -8]      # 整数输入
    yd = fir_direct(x, c)[:len(x)]
    ya = da_fir(x, c)
    print("直接型 =", yd)
    print("DA 型  =", ya)
    assert ya == yd, "分布式算法与直接型 FIR 逐点相等"

    h = [0.2, -0.1, 0.4, 0.25, -0.05]
    xf = [1.0, -2.0, 0.5, 3.0, -1.0, 2.0, 0.25, -0.75]
    yt = fir_transposed(xf, h)
    yc = fir_direct(xf, h)[:len(xf)]
    assert all(abs(a - b) < 1e-12 for a, b in zip(yt, yc)), "转置型与直接型 FIR 等价"
    print("PASS: 22 章 CORDIC、DA FIR 与转置型 FIR 均通过")


if __name__ == "__main__":
    main()
