"""第 12 章：抽取、内插与多相分解的确定性校验（仅用标准库）。"""
import math


def downsample(x, M):
    return x[::M]


def upsample(x, L):
    out = [0.0] * (len(x) * L)
    for i, v in enumerate(x):
        out[i * L] = v
    return out


def direct_decimate(x, h, M):
    at = lambda i: x[i] if 0 <= i < len(x) else 0.0
    n_out = (len(x) + len(h)) // M
    return [sum(h[j] * at(M * n - j) for j in range(len(h))) for n in range(n_out)]


def polyphase_decimate(x, h, M):
    at = lambda i: x[i] if 0 <= i < len(x) else 0.0
    n_out = (len(x) + len(h)) // M
    y = []
    for n in range(n_out):
        acc = 0.0
        for k in range(M):
            i = 0
            while k + i * M < len(h):
                acc += h[k + i * M] * at((n - i) * M - k)
                i += 1
        y.append(acc)
    return y


def main():
    x0 = [1.0, 0.0, -1.0, 0.0, 1.0, 0.0, -1.0, 0.0]
    assert downsample(x0, 2) == [1.0, -1.0, 1.0, -1.0]
    up = upsample([1.0, 2.0, 3.0], 3)
    assert up == [1.0, 0.0, 0.0, 2.0, 0.0, 0.0, 3.0, 0.0, 0.0], "上采样除 L 的倍数外必须为零"

    # 混叠恒等式：0.30 循环/样本的余弦在 M=3 下采样后等于 0.10（新采样率）
    f0, M = 0.30, 3
    y = [math.cos(2 * math.pi * f0 * M * n) for n in range(16)]
    alias = [math.cos(2 * math.pi * 0.10 * n) for n in range(16)]
    assert max(abs(a - b) for a, b in zip(y, alias)) < 1e-12, "混叠频率应为 0.10（新采样率）"
    print("0.30 @ M=3 折叠到新频率 0.10（原始归一化轴 0.0333）")

    # 多相恒等式：多相抽取必须与直接抽取逐点相同
    h = [0.25, 0.5, 0.25, 0.1, -0.05, 0.02, 0.01, -0.005, 0.003]
    x = [math.sin(0.7 * n) + 0.3 * math.cos(0.13 * n) for n in range(40)]
    yd, yp = direct_decimate(x, h, M), polyphase_decimate(x, h, M)
    assert max(abs(a - b) for a, b in zip(yd, yp)) < 1e-12, "多相分解必须与直接抽取等价"
    print("直接抽取前 4 个输出：", [round(v, 5) for v in yd[:4]])

    N = len(h)
    print(f"直接：{N} 次乘加/输入样本；多相：约 {N/M:.3f} 次/输入样本（速率降为 1/{M}）")
    print("PASS: 抽取、内插与多相分解")


if __name__ == "__main__":
    main()
