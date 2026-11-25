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

function twoTone(noise) {
  const nz = lcg(N, 1234);
  return Array.from({ length: N }, (_, n) => Math.sin(2 * Math.PI * 10 * n / 64)
    + Math.sin(2 * Math.PI * 10.6 * n / 64) + noise * nz[n]);
}
function periodogram(x) {
  const out = [];
  for (let k = 0; k <= x.length / 2; k++) {
    let re = 0, im = 0;
    for (let n = 0; n < x.length; n++) { re += x[n] * Math.cos(2 * Math.PI * k * n / x.length); im -= x[n] * Math.sin(2 * Math.PI * k * n / x.length); }
    out.push((re * re + im * im) / x.length);
  }
  return out;
}
function burg(x, p) {
  let f = x.slice(), b = x.slice();
  const a = Array.from({ length: p + 1 }, () => new Array(p + 1).fill(0));
  const kref = []; let err = x.reduce((s, v) => s + v * v, 0) / x.length;
  for (let m = 1; m <= p; m++) {
    let num = 0, den = 0;
    for (let n = m; n < x.length; n++) { num += -2 * f[n] * b[n - 1]; den += f[n] ** 2 + b[n - 1] ** 2; }
    const km = num / den; kref.push(km); a[m][m] = km;
    for (let i = 1; i < m; i++) a[m][i] = a[m - 1][i] + km * a[m - 1][m - i];
    err *= 1 - km * km;
    const nf = f.slice(), nb = b.slice();
    for (let n = x.length - 1; n >= m; n--) { nf[n] = f[n] + km * b[n - 1]; nb[n] = b[n - 1] + km * f[n]; }
    f = nf; b = nb;
  }
  return { a: a[p].slice(1, p + 1), kref, err };
}
function arSpec(a, err, M = 256) {
  const out = [];
  for (let i = 0; i <= M; i++) {
    const w = Math.PI * i / M;
    let re = 1, im = 0;
    for (let k = 0; k < a.length; k++) { re += a[k] * Math.cos(w * (k + 1)); im -= a[k] * Math.sin(w * (k + 1)); }
    out.push(err / (re * re + im * im));
  }
  return out;
}
function dftMag(x) {
  const n0 = x.length, out = [];
  for (let k = 0; k < n0; k++) {
    let re = 0, im = 0;
    for (let n = 0; n < n0; n++) { re += x[n] * Math.cos(2 * Math.PI * k * n / n0); im -= x[n] * Math.sin(2 * Math.PI * k * n / n0); }
    out.push(Math.hypot(re, im));
  }
  return out;
}
function stepTones() {
  const n0 = 192, x = [];
  for (let n = 0; n < n0; n++) x.push(Math.sin(2 * Math.PI * (n < n0 / 2 ? 24 : 60) * n / n0));
  return x;
}
function stftSpec(x, L, hop) {
  const w = Array.from({ length: L }, (_, n) => 0.5 - 0.5 * Math.cos(2 * Math.PI * n / (L - 1)));
  const frames = [];
  for (let m = 0; m + L <= x.length; m += hop) {
    frames.push({ m, s: dftMag(w.map((wn, n) => x[m + n] * wn)).slice(0, L / 2 + 1) });
  }
  return frames;
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
  },
  ar(pv, svg, out) {
    const p = pv, x = twoTone(0.1), per = periodogram(x), { a, kref, err } = burg(x, p), sp = arSpec(a, err);
    const g = frame(svg), fmax = 32, mp = Math.max(...per), ms = Math.max(...sp), M = sp.length - 1;
    const X = f => g.left + f / fmax * (g.right - g.left);
    const Y = (v, mx) => g.bottom - v / mx * (g.bottom - g.top) * 0.92;
    per.forEach((v, k) => line(svg, X(k * fmax / (per.length - 1)), g.bottom, X(k * fmax / (per.length - 1)), Y(v, mp), "#e3c9ab", 3));
    add(svg, "path", { d: sp.map((v, i) => (i ? "L" : "M") + X(i / M * fmax).toFixed(1) + " " + Y(v, ms).toFixed(1)).join(" "), fill: "none", stroke: "#147f80", "stroke-width": 2.4 });
    txt(svg, g.left + 6, g.top + 12, "周期图（赭柱）与 Burg AR 谱（青线），各自归一化", "#53676d");
    const hm = 0.30, pk = [];
    for (let i = 1; i < sp.length - 1; i++) if (sp[i] > sp[i - 1] && sp[i] >= sp[i + 1] && sp[i] > hm * ms) pk.push(i / M * fmax);
    out.textContent = "AR 阶数 p=" + p + "：Burg 谱出现 " + pk.length + " 个峰（" +
      pk.map(v => v.toFixed(1)).join("、") + " Hz），最大 |k|=" + Math.max(...kref.map(Math.abs)).toFixed(3) +
      "。" + (pk.length >= 2 ? "已分辨出间隔 0.6 Hz 的双峰（周期图仍是单峰）。" : p > 30 ? "阶数过高，谱线起伏，未必更清晰。" : "仍与周期图类似地合并为单峰。");
  },
  stft(sv, svg, out) {
    const L = sv * 2, hop = sv, x = stepTones(), frames = stftSpec(x, L, hop), g = frame(svg);
    const nb = frames[0].s.length, nf = frames.length;
    let mx = 0;
    frames.forEach(f => f.s.forEach(v => { if (v > mx) mx = v; }));
    const cw = (g.right - g.left) / Math.max(nf, 1), ch = (g.bottom - g.top) / Math.max(nb, 1);
    frames.forEach((f, fi) => f.s.forEach((v, bi) => {
      const t = v / mx;
      const col = "rgb(" + Math.round(233 - 213 * t) + "," + Math.round(245 - 118 * t) + "," + Math.round(240 - 112 * t) + ")";
      add(svg, "rect", { x: g.left + fi * cw, y: g.bottom - (bi + 1) * ch, width: cw + 0.5, height: ch + 0.5, fill: col });
    }));
    txt(svg, g.left + 6, g.top + 12, "语谱图：横轴时间、纵轴频率", "#53676d");
    const peakHz = idx => { const s = frames[idx].s; let bi = 0; for (let i = 1; i < s.length; i++) if (s[i] > s[bi]) bi = i; return bi * 192 / L; };
    out.textContent = "窗长 L=" + L + "、帧移 " + hop + "：频率分辨率 f_s/L = " + (192 / L).toFixed(1) +
      " Hz，时间分辨率≈ " + (hop / 192 * 1000).toFixed(0) + " ms。前段峰 " + peakHz(0).toFixed(0) +
      " Hz，后段峰 " + peakHz(nf - 1).toFixed(0) + " Hz。" + (L <= 16 ? "窗很短：台阶陡、时间准，但频率带很宽。" : L >= 48 ? "窗较长：频率细，但时间定位变模糊。" : "窗长适中。");
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
