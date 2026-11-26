"""第 21 章：吞吐量下界、乒乓缓冲、环形缓冲 FIR 与 SIMD 计数（仅标准库）。"""
from math import ceil


def max_sample_rate(clock_hz, taps):
    """单 MAC/周期假设下，每样本需 taps 个周期。"""
    return clock_hz / taps


def ring_fir(x, h):
    """模寻址（环形缓冲）实现的 FIR，延迟线不搬移数据。"""
    M, buf, idx, y = len(h), [0.0] * len(h), 0, []
    for v in x:
        buf[idx] = v
        acc = 0.0
        for k in range(M):
            acc += h[k] * buf[(idx - k) % M]
        y.append(acc)
        idx = (idx + 1) % M
    return y


def conv(x, h):
    y = [0.0] * (len(x) + len(h) - 1)
    for i, a in enumerate(x):
        for j, b in enumerate(h):
            y[i + j] += a * b
    return y


def dot_ops(n, lanes):
    """点积：标量乘加次数、向量乘加次数、尾部剩余元素。"""
    full = n // lanes
    rem = n % lanes
    return n, full + (1 if rem else 0), rem


def pingpong(blocks):
    """模拟 DMA/CPU 乒乓：返回 (读缓冲, 写缓冲) 序列与冲突标记。"""
    seq, read, write, conflict = [], 1, 0, False
    for _ in range(blocks):
        if read == write:
            conflict = True
        seq.append((read, write))
        read, write = write, read
    return seq, conflict


def main():
    clock, taps, target = 100e6, 256, 48000.0
    fs = max_sample_rate(clock, taps)
    util = target * taps / clock
    print(f"256 抽头 @100MHz：最大采样率 = {fs:.0f} Hz，按 48 kHz 工作占用 = {util*100:.2f}%")
    assert fs > target and util < 0.5, "单 MAC/周期下 256 抽头仍能满足 48 kHz 实时"

    x = [1.0, -2.0, 0.5, 3.0, -1.0, 2.0, 0.25, -0.75, 1.5, -0.5]
    h = [0.2, -0.1, 0.4, 0.25, -0.05]
    yr = ring_fir(x, h)
    yc = conv(x, h)[:len(x)]
    print("环形缓冲 FIR 前 4 个输出 =", [round(v, 4) for v in yr[:4]])
    assert all(abs(a - b) < 1e-12 for a, b in zip(yr, yc)), "模寻址与直接卷积等价"

    seq, conflict = pingpong(6)
    print("乒乓序列（读缓冲, 写缓冲） =", seq)
    assert not conflict and all(r != w for r, w in seq), "读写永不同时落在同一缓冲区"

    n, vops, rem = dot_ops(1000, 4)
    print(f"n={n}，4 通道：向量乘加 {vops} 次，尾部剩余 {rem} 个元素")
    assert vops == 250 and rem == 0, "向量化把乘加次数降到 1/4（不计横向求和）"
    print("PASS: 21 章吞吐量、乒乓、环形缓冲与 SIMD 计数均通过")


if __name__ == "__main__":
    main()
