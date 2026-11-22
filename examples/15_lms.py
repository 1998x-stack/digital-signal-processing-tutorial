"""第 15 章：LMS/NLMS 收敛、失调与输入电平鲁棒性的确定性校验（仅用标准库）。"""
H = [0.6, 0.3, -0.2, 0.1]          # 未知系统（长度 4）
M = len(H)


def lcg(n, seed):
    out, s = [], seed
    for _ in range(n):
        s = (s * 16807) % 2147483647
        out.append(s / 2147483647 * 2 - 1)
    return out


def run(x, d, mu=None, nlms=False):
    w = [0.0] * M
    errs = []
    for n in range(M - 1, len(x)):
        xv = [x[n - k] for k in range(M)]
        y = sum(w[k] * xv[k] for k in range(M))
        e = d[n] - y
        if nlms:
            g = mu / (sum(v * v for v in xv) + 1e-6)
        else:
            g = mu
        for k in range(M):
            w[k] += g * e * xv[k]
        errs.append(e * e)
    return w, errs


def main():
    n = 20000
    x = lcg(n, 2024)
    d = [sum(H[k] * (x[i - k] if i - k >= 0 else 0) for k in range(M)) for i in range(n)]

    # LMS 在均值意义下收敛到未知系统
    w, _ = run(x, d, mu=0.02)
    err = max(abs(a - b) for a, b in zip(w, H))
    assert err < 0.02, f"LMS 应收敛到未知系统，最大系数误差={err:.4f}"
    print("LMS 估计权重：", [round(v, 4) for v in w], "真值", H)

    # 失调随步长增大：加入确定性噪声后比较稳态 MSE
    v = lcg(n, 99)
    dn = [d[i] + 0.1 * v[i] for i in range(n)]
    floor = 0.01 * (sum(vi * vi for vi in v) / n)
    ms = {}
    for mu in (0.005, 0.05):
        _, e = run(x, dn, mu=mu)
        ms[mu] = sum(e[-2000:]) / 2000
    assert ms[0.05] > ms[0.005], "大步长的稳态 MSE 应更大"
    print(f"小步长稳态 MSE={ms[0.005]:.5f} < 大步长 MSE={ms[0.05]:.5f}（噪声底≈{floor:.5f}）")

    # NLMS 对输入电平突变稳健：后半段把输入放大 10 倍
    x2 = x[:]
    for i in range(n // 2, n):
        x2[i] *= 10
    d2 = [sum(H[k] * (x2[i - k] if i - k >= 0 else 0) for k in range(M)) for i in range(n)]
    wn, _ = run(x2, d2, mu=0.5, nlms=True)
    assert all(abs(v2) < 2.0 for v2 in wn), "NLMS 权重应保持有界"
    assert max(abs(a - b) for a, b in zip(wn, H)) < 0.05, "NLMS 应跟随放大后的输入"
    print("NLMS 在输入放大 10 倍后权重：", [round(v2, 4) for v2 in wn])
    print("PASS: LMS 收敛、失调单调性与 NLMS 鲁棒性")


if __name__ == "__main__":
    main()
