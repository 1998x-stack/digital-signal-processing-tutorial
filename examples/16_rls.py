"""第 16 章：有色输入下 RLS 相对 LMS 的收敛优势，以及遗忘因子的跟踪作用（仅标准库）。"""
M = 4
H = [0.6, 0.3, -0.2, 0.1]          # 未知系统


def lcg(n, seed):
    out, s = [], seed
    for _ in range(n):
        s = (s * 16807) % 2147483647
        out.append(s / 2147483647 * 2 - 1)
    return out


def ar1(w, rho=0.9):
    """一阶自回归有色输入 x[n] = rho x[n-1] + w[n]：一个极点靠近单位圆。"""
    x, prev = [], 0.0
    for v in w:
        prev = rho * prev + v
        x.append(prev)
    return x


def maxerr(a, b):
    return max(abs(u - v) for u, v in zip(a, b))


def lms(x, d, mu=0.02):
    """返回每步的系数误差轨迹。"""
    w = [0.0] * M
    traj = []
    for n in range(M, len(x)):
        xv = [x[n - k] for k in range(M)]
        e = d[n] - sum(w[k] * xv[k] for k in range(M))
        for k in range(M):
            w[k] += mu * e * xv[k]
        traj.append(maxerr(w, H))
    return w, traj


def rls(x, d, lam=1.0, delta=1.0):
    """标准 RLS 递推：P(n) = (P - k xᵀ P)/λ，返回权重、系数误差轨迹和最终 P。"""
    w = [0.0] * M
    P = [[delta if i == j else 0.0 for j in range(M)] for i in range(M)]
    traj = []
    for n in range(M, len(x)):
        xv = [x[n - k] for k in range(M)]
        Px = [sum(P[i][j] * xv[j] for j in range(M)) for i in range(M)]
        denom = lam + sum(xv[i] * Px[i] for i in range(M))
        k = [v / denom for v in Px]
        e = d[n] - sum(w[i] * xv[i] for i in range(M))
        w = [w[i] + k[i] * e for i in range(M)]
        P = [[(P[i][j] - k[i] * Px[j]) / lam for j in range(M)] for i in range(M)]
        traj.append(maxerr(w, H))
    return w, traj, P


def build(n, seed_x, seed_v, rho=0.9, noise=0.1, switch=None):
    x = ar1(lcg(n, seed_x), rho)
    v = lcg(n, seed_v)
    d = []
    for i in range(n):
        h = switch[1] if (switch and i >= switch[0]) else H
        d.append(sum(h[k] * (x[i - k] if i - k >= 0 else 0.0) for k in range(M)) + noise * v[i])
    return x, d


def main():
    n = 700
    x, d = build(n, 2024, 99)
    _, tl = lms(x, d, mu=0.02)
    wr, tr, P = rls(x, d, lam=1.0, delta=1.0)
    idx = 150
    print("有色输入 rho=0.9；同一样本数下系数误差（||w−h||∞）：")
    print("  第", idx, "步：LMS =", round(tl[idx], 4), " RLS =", round(tr[idx], 4))
    print("  末步：LMS =", round(tl[-1], 4), " RLS =", round(tr[-1], 4))
    assert tr[idx] < 0.08 < tl[idx], "RLS 应比 LMS 更早获得小系数误差"
    assert maxerr(wr, H) < 0.05, "增长窗 RLS 应收敛到未知系统"
    for i in range(M):
        for j in range(M):
            assert abs(P[i][j] - P[j][i]) < 1e-9, "P 应保持对称"

    # 遗忘因子的作用：中点突变后，λ=1 的增长窗“冻结”，λ<1 继续跟踪
    n2 = 3000
    H2 = [0.2, -0.5, 0.4, 0.15]
    xs, ds = build(n2, 777, 55, switch=(n2 // 2, H2))
    wflat, _, _ = rls(xs, ds, lam=1.0, delta=1.0)
    wforget, _, _ = rls(xs, ds, lam=0.99, delta=0.01)
    print("突变后对新系统的系数误差：λ=1.0 =", round(maxerr(wflat, H2), 3),
          " λ=0.99 =", round(maxerr(wforget, H2), 3))
    assert maxerr(wforget, H2) < 0.05, "λ<1 的 RLS 应重新跟踪新系统"
    assert maxerr(wflat, H2) > 0.2, "λ=1 的增长窗对新系统跟踪很慢"
    print("PASS: RLS 收敛更快、P 对称、遗忘因子跟踪时变系统")


if __name__ == "__main__":
    main()
