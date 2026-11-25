(() => {
"use strict";
const NS = "http://www.w3.org/2000/svg";
const E = (n, a = {}, t = "") => {
  const e = document.createElementNS(NS, n);
  for (const [k, v] of Object.entries(a)) e.setAttribute(k, String(v));
  if (t) e.textContent = t;
  return e;
};
const add = (s, n, a, t = "") => s.append(E(n, a, t));
const line = (s, x1, y1, x2, y2, c = "#c5d6ce", w = 1) =>
  add(s, "line", { x1, y1, x2, y2, stroke: c, "stroke-width": w });
const txt = (s, x, y, v, c = "#53676d", fs = 12) =>
  add(s, "text", { x, y, fill: c, "font-size": fs, "font-family": "system-ui,PingFang SC,sans-serif" }, v);

function lcg(n, seed) {
  const out = []; let s = seed;
  for (let i = 0; i < n; i++) { s = (s * 16807) % 2147483647; out.push(s / 2147483647 * 2 - 1); }
  return out;
}

const N = 120;
function scene() {
  const tru = []; let p = 0;
  for (let t = 0; t < N; t++) { p += t < 60 ? 0.6 : -0.9; tru.push(p); }
  const nz = lcg(N, 2024);
  return { tru, z: tru.map((v, i) => v + 2.5 * nz[i]) };
}

function kalman(z, q, r = 6.25) {
  let x = [z[0], 0], P = [[10, 0], [0, 10]];
  const out = [];
  for (const zz of z) {
    const xp = [x[0] + x[1], x[1]];
    const Pp = [
      [P[0][0] + P[0][1] + P[1][0] + P[1][1] + q / 4, P[0][1] + P[1][1] + q / 2],
      [P[1][0] + P[1][1] + q / 2, P[1][1] + q]
    ];
    const S = Pp[0][0] + r, K = [Pp[0][0] / S, Pp[1][0] / S], y = zz - xp[0];
    x = [xp[0] + K[0] * y, xp[1] + K[1] * y];
    P = [
      [(1 - K[0]) * Pp[0][0], (1 - K[0]) * Pp[0][1]],
      [Pp[1][0] - K[1] * Pp[0][0], Pp[1][1] - K[1] * Pp[0][1]]
    ];
    out.push(x[0]);
  }
  return out;
}

function frame(svg) {
  svg.replaceChildren();
  svg.setAttribute("viewBox", "0 0 560 215");
  const g = { left: 42, right: 540, top: 26, bottom: 176 };
  line(svg, g.left, g.bottom, g.right, g.bottom, "#718d88", 1.4);
  line(svg, g.left, g.top, g.left, g.bottom, "#718d88", 1.4);
  return g;
}
const registry = {
  kalman(v, svg, out) {
    const q = v / 10, { tru, z } = scene(), est = kalman(z, q);
    const g = frame(svg), ymin = -26, ymax = 44;
    const X = i => g.left + i * (g.right - g.left) / (N - 1);
    const Y = val => g.bottom - (val - ymin) / (ymax - ymin) * (g.bottom - g.top);
    line(svg, X(60), g.top, X(60), g.bottom, "#dbe7e3", 1.2);
    txt(svg, X(60) + 4, g.top + 12, "机动", "#916c22");
    z.forEach((z2, i) => add(svg, "circle", { cx: X(i), cy: Y(z2), r: 2, fill: "#d8b48a" }));
    add(svg, "path", { d: tru.map((p, i) => (i ? "L" : "M") + X(i).toFixed(1) + " " + Y(p).toFixed(1)).join(" "), fill: "none", stroke: "#7461ba", "stroke-width": 1.6 });
    add(svg, "path", { d: est.map((p, i) => (i ? "L" : "M") + X(i).toFixed(1) + " " + Y(p).toFixed(1)).join(" "), fill: "none", stroke: "#147f80", "stroke-width": 2.4 });
    txt(svg, g.left + 6, g.top + 12, "位置（匀速真值 / 带噪观测 / 估计）", "#53676d");
    let se = 0, lg = 0;
    for (let i = 0; i < N; i++) se += (est[i] - tru[i]) ** 2;
    for (let i = 60; i < 76; i++) lg += tru[i] - est[i];
    const rms = Math.sqrt(se / N), lag = lg / 16;
    out.textContent = "过程噪声 Q=" + q.toFixed(1) + "：位置 RMS 误差 " + rms.toFixed(2) +
      "，机动后 16 点平均滞后 " + lag.toFixed(2) + "。" +
      (q < 0.5 ? "Q 太小：曲线更平滑，但转弯时明显落后。" : q > 8 ? "Q 太大：跟得上机动，但更抖、RMS 更高。" : "Q 适中：在平滑与跟踪之间折中。");
  }
};
document.querySelectorAll("[data-spectrum-lab]").forEach(el => {
  const run = registry[el.dataset.spectrumLab];
  const slider = el.querySelector('input[type="range"]'), svg = el.querySelector("svg"), out = el.querySelector("output");
  if (!run || !slider || !svg || !out) return;
  const paint = () => run(Number(slider.value), svg, out);
  slider.addEventListener("input", paint);
  paint();
});
})();
