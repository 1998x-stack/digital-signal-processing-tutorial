# 第二批：DTFT → IIR 设计（06–10）

## 本批验收与技术审计重点

| 章节 | 主要问题 | 可验证结论 | 图解 | 数值程序 |
| --- | --- | --- | --- | --- |
| 06 | DTFT 连续频率与 2π 周期 | 3 点平均在 2π/3 为零；频谱平移 2π 不变 | 06-dtft-periodic、06-lti-response | 06_dtft.py |
| 07 | DFT 泄漏、补零、循环卷积 | 4 点循环与 7 点线性结果不同；补零 ≥7 后一致 | 07-leakage、07-circular-linear | 07_dft.py |
| 08 | FFT 奇偶分治、位反转、非 2 幂支持边界 | radix-2 与独立 O(N²) DFT 在数值容差内一致 | 08-dit-butterfly、08-bit-reversal | 08_fft.py |
| 09 | FIR 线性相位条件与截止规范 | 系数对称、DC=1、Nyquist 低增益；firwin cutoff 是半幅值 | 09-windowed-sinc、09-window-tradeoff | 09_fir.py |
| 10 | IIR 双线性预畸变、SOS | 一阶预畸变低通在 fc 处幅度 1/√2、极点模 <1 | 10-bilinear-map、10-prewarp、10-sos-chain | 10_iir.py |

## 证据与设计边界

- 第一手工程接口来自 SciPy 的 [FFT](https://docs.scipy.org/doc/scipy/reference/generated/scipy.fft.fft.html)、[firwin](https://docs.scipy.org/doc/scipy/reference/generated/scipy.signal.firwin.html)、[butter](https://docs.scipy.org/doc/scipy/reference/generated/scipy.signal.butter.html) 与 [bilinear](https://docs.scipy.org/doc/scipy/reference/generated/scipy.signal.bilinear.html) 官方文档。
- 教学数学核心参照 [MIT OCW DSP](https://ocw.mit.edu/courses/6-341-discrete-time-signal-processing-fall-2005/) 与原仓库前几章的规范。
- 相应证据记于 evidence/06.json 至 evidence/10.json；交互图是确定性 toy demo，不是设备测试。
- 图 09-window-tradeoff.svg 明确标为定性示意，不应从示意图读出精确的旁瓣 dB 或截止位置。
- 本批保留 11–28 章原内容，旧根目录链接全部保留；不修改历史章节知识点以外的资源。

## 质量门禁

```bash
python scripts/validate_site.py
python examples/check_examples.py
python scripts/browser_qa.py --out qa-results
```

最后一项需要 Playwright 与 Chromium；只在工作流实际执行成功时记录为浏览器已验证。浏览器截图可从 CI artifact 取得。
