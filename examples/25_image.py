"""第 25 章：二维可分离卷积、DCT-II 能量压缩与 Sobel 梯度（仅标准库）。"""
from math import pi, cos, sqrt

N = 8
a = lambda k: 1 / sqrt(2) if k == 0 else 1.0


def dct2(block):
    out = [[0.0] * N for _ in range(N)]
    for k in range(N):
        for l in range(N):
            s = 0.0
            for m in range(N):
                for n in range(N):
                    s += block[m][n] * cos(pi * k * (2 * m + 1) / (2 * N)) \
                         * cos(pi * l * (2 * n + 1) / (2 * N))
            out[k][l] = (2.0 / N) * a(k) * a(l) * s
    return out


def conv2(img, ker):
    K = len(ker); H = len(img); W = len(img[0]); r = K // 2
    return [[sum(img[i + di][j + dj] * ker[di + r][dj + r]
                 for di in range(-r, r + 1) for dj in range(-r, r + 1)
                 if 0 <= i + di < H and 0 <= j + dj < W)
             for j in range(W)] for i in range(H)]


def conv_sep(img, g, h):
    H = len(img); W = len(img[0]); r = len(g) // 2
    tmp = [[sum(img[i][j + dj] * g[dj + r] for dj in range(-r, r + 1)
                if 0 <= j + dj < W) for j in range(W)] for i in range(H)]
    s = len(h) // 2
    return [[sum(tmp[i + di][j] * h[di + s] for di in range(-s, s + 1)
                 if 0 <= i + di < H) for j in range(W)] for i in range(H)]


g = [2, 4, 5, 4, 2]                                   # 一维高斯，秩-1 核的外积
ker = [[g[i] * g[j] for j in range(5)] for i in range(5)]
img = [[(17 * i + 5 * j) % 9 * 12 + 10 for j in range(7)] for i in range(7)]
d, s = conv2(img, ker), conv_sep(img, g, g)
assert max(abs(d[i][j] - s[i][j]) for i in range(7) for j in range(7)) < 1e-9

block = [[80 + 30 * m + 15 * n for n in range(N)] for m in range(N)]   # 平坦渐变块
coef = dct2(block)
e_img = sum(v * v for row in block for v in row)
e_coef = sum(v * v for row in coef for v in row)
assert abs(e_img - e_coef) / e_img < 1e-9               # 正交变换能量守恒
flat = sorted((abs(coef[k][l]) for k in range(N) for l in range(N)), reverse=True)
top10 = sum(v * v for v in flat[:10]) / e_coef
assert top10 > 0.95, top10                              # 平滑块能量高度集中

# 之字形扫描：恰好覆盖 64 个系数且从 DC 开始
zig = []
for su in range(2 * N - 1):
    diag = [(r, su - r) for r in range(N) if 0 <= su - r < N]
    zig += diag[::-1] if su % 2 else diag
assert len(zig) == 64 and len(set(zig)) == 64 and zig[0] == (0, 0) and zig[-1] == (N - 1, N - 1)

# Sobel：竖直边缘只激发水平梯度核
edge = [[0 if j < 3 else 100 for j in range(6)] for i in range(6)]
gx = conv2(edge, [[-1, 0, 1], [-2, 0, 2], [-1, 0, 1]])
gy = conv2(edge, [[-1, -2, -1], [0, 0, 0], [1, 2, 1]])
assert all(gy[i][j] == 0 for i in (2, 3) for j in range(6))   # 竖直边缘内部 Gy=0
assert gx[3][3] == 400 and gx[3][1] == 0
print("PASS 25: 可分离卷积误差<1e-9，DCT 能量守恒，前 10 系数保留 %.1f%% 能量，Sobel 竖直边缘 |Gx|=400 |Gy|=0"
      % (100 * top10))
