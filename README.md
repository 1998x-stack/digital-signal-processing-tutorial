# 数字信号处理：从波形到算法

面向独立读者的 28 章中文数字信号处理教程，部署为纯静态 GitHub Pages 站点。

**入口：** [课程首页](https://1998x-stack.github.io/digital-signal-processing-tutorial/) · [GitHub](https://github.com/1998x-stack/digital-signal-processing-tutorial)

## 学习路线

| 范围 | 主题 | 当前状态 |
| --- | --- | --- |
| 01–05 | 数字信号处理导论、离散时间信号、LTI 系统、采样、Z 变换 | 第一批重构，含独立 SVG、原生公式与交互实验 |
| 06–10 | DTFT、DFT、FFT、FIR 与 IIR 设计 | 第二批重构，含独立 SVG、公式与数值实验 |
| 11 | 滤波器结构 | 已重构 |
| 12–18 | 多速率、统计分析、自适应滤波、谱估计、时频分析 | 已重构 |
| 19–22 | 仿真、定点、嵌入式和 FPGA | 已重构 |
| 23–28 | 音频、通信、图像、AI、SDR 与综合项目 | 已重构，含独立 SVG、交互图解、数值实验与来源台账 |

## 工程目录

```text
digital-signal-processing-tutorial/
├── index.html                    # GitHub Pages 入口，保持仓库根目录部署
├── 01.html ... 28.html           # 旧地址兼容跳转
├── chapters/                     # 正式章节地址，01–28 重新编写
│   ├── 01.html ... 28.html
│   ├── index.html                # 旧章节返回目录的兼容入口
│   └── theme.css                 # 后续 18 章使用的旧样式
├── assets/
│   ├── css/site.css              # 门户设计
│   ├── css/article.css           # 重构文章设计系统
│   ├── js/site.js                # 章节本地过滤
│   ├── js/spectrum-labs.js       # 交互图解，无外部依赖
│   └── svg/                      # 章节概念图的独立 SVG
├── examples/                     # 可运行的 Python 标准库小实验
├── evidence/                     # 事实来源与公式假设台账
├── scripts/validate_site.py      # 静态完整性检查
├── .github/workflows/quality.yml # PR / push 质量门禁
├── courses.json                  # 28 章可机读目录
└── AGENTS.md                     # 下一批重构规范
```

## 本地阅读与测试

直接打开 `index.html`，或者启动本地服务器：

```bash
python -m http.server 8000
# 浏览器访问 http://localhost:8000
python scripts/validate_site.py
python examples/check_examples.py
# 可选：pip install playwright && python -m playwright install chromium
python scripts/browser_qa.py --out qa-results
```

没有 npm、云字体、在线公式库等构建依赖。GitHub Pages 使用仓库根目录的静态文件；如当前仓库 Pages 来源不是 `main / (root)`，需要在 GitHub 设置中选择正确来源。**合并代码不等于已验证 Pages 发布。**

## 内容原则

- 每个章节独立自足，不能只写“本讲介绍了什么”。
- 保留明确的假设、求和区间、单位、频率归一化惯例与零极点条件。
- 数学展示采用原生 MathML；SVG 有标题、描述、可读图注，图表是解释的一部分而非装饰。
- 不伪造实验数字或工程经历；对具体事实标示来源及其作用域。
- 新篇至少包含问题、图解、机制推导、可执行例子、边界条件与参考来源。
- 06–10 核心约定：DTFT 的 2π 周期，正 DFT 不归一化、逆 DFT 除以 N，补零不增加观测长度；radix-2 不是 FFT 的唯一算法，firwin 截止是 -6 dB 而 Butterworth 是 -3 dB，bilinear() 不自动 prewarp。

## 参考资料

- [MIT OCW · Digital Signal Processing study materials](https://ocw.mit.edu/courses/res-6-008-digital-signal-processing-spring-2011/pages/study-materials/)
- [MIT OCW · Discrete-Time Signal Processing](https://www.ocw.mit.edu/courses/6-341-discrete-time-signal-processing-fall-2005/)
- [Oppenheim & Schafer · Discrete-Time Signal Processing（MIT 开放教材）](https://www.ocw.mit.edu/courses/res-6-dtsp-discrete-time-signal-processing/resources/mitres_6-dtsp_s26_firstedition_pdf/)
- [Analog Devices · The Scientist and Engineer's Guide to DSP](https://www.analog.com/en/resources/technical-books/scientist_engineers_guide.html)

视觉叙述借鉴 [Olah-style-posts](https://github.com/1998x-stack/Olah-style-posts) 的因果式图解工作流，所有图与文章内容均独立绘制和撰写。
