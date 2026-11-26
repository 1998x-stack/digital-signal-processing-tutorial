#!/usr/bin/env python3
"""Screenshot and browser quality gate for the static course.
Requires Playwright + Chromium. Artifacts are saved outside the source tree.
"""
from pathlib import Path
import argparse
import json
import sys
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parent.parent
PAGES = ["index.html"] + [f"chapters/{i:02d}.html" for i in range(1, 29)]
WIDTHS = (1440, 768, 390, 360)

def check(path, width, out, browser):
    errors = []
    page = browser.new_page(viewport={"width": width, "height": 900}, device_scale_factor=1)
    page.on("pageerror", lambda exc: errors.append("JS " + str(exc)))
    page.on("console", lambda msg: errors.append("console " + msg.text) if msg.type == "error" else None)
    page.goto((ROOT / path).as_uri(), wait_until="load")
    page.locator("img").evaluate_all("els => els.forEach(img => { img.loading = 'eager'; })")
    page.evaluate("""async () => {
      await Promise.all([...document.images].map(img => img.decode().catch(() => null)));
    }""")
    state = page.evaluate("""() => ({
      docWidth: document.documentElement.scrollWidth,
      viewport: innerWidth,
      h1: document.querySelectorAll('h1').length,
      images: [...document.querySelectorAll('img')].map(i => ({
        src: i.getAttribute('src'), natural: i.naturalWidth,
        width: i.getBoundingClientRect().width, alt: i.getAttribute('alt')
      })),
      figures: document.querySelectorAll('article figure').length,
      captions: document.querySelectorAll('article figcaption').length,
      maths: [...document.querySelectorAll('math')].map(m => ({
        namespace: m.namespaceURI,
        width: m.getBoundingClientRect().width,
        height: m.getBoundingClientRect().height
      })),
      invalidFractions: [...document.querySelectorAll('mfrac')].filter(n => n.children.length !== 2).length
    })""")
    if state["docWidth"] > state["viewport"] + 1:
        errors.append(f"horizontal overflow: {state['docWidth']} > {state['viewport']}")
    if state["h1"] != 1: errors.append("H1 count is not 1")
    for img in state["images"]:
        if img["natural"] == 0 or img["width"] == 0 or not img["alt"]:
            errors.append(f"broken/unnamed image: {img['src']}")
    if path != "index.html":
        if state["figures"] < 2 or state["captions"] != state["figures"]:
            errors.append("Expected at least two captioned figures")
        if state["invalidFractions"]:
            errors.append("Invalid MathML mfrac arity")
        if not state["maths"]:
            errors.append("MathML missing")
        for equation in state["maths"]:
            if equation["namespace"] != "http://www.w3.org/1998/Math/MathML" or min(equation["width"],equation["height"]) <= 0:
                errors.append("MathML namespace/size invalid")
        if page.locator("svg math").count():
            errors.append("MathML nested inside SVG")
        slider = page.locator("input[type=range]")
        output = page.locator("output")
        before = output.inner_text()
        slider.evaluate("""el => {
          el.value = el.value === el.min ? el.max : el.min;
          el.dispatchEvent(new Event('input', {bubbles: true}));
        }""")
        after = output.inner_text()
        if not after or before == after:
            errors.append("Interactive lab did not update accessible output")
        if page.locator(".lab svg circle").count() == 0:
            errors.append("Interactive stem plot missing")
    elif width == 390:
        search = page.locator("#course-search")
        search.fill("卷积")
        visible = page.locator(".chapter-card:visible").count()
        if visible < 1 or visible >= 28:
            errors.append(f"Course filter did not work: {visible}")
        search.fill("")
    safe = path.replace("/", "-").replace(".html", "")
    screenshot = out / f"{safe}-{width}.png"
    page.screenshot(path=str(screenshot), full_page=True)
    if width == 1440 and path != "index.html":
        page.emulate_media(media="print")
        print_imgs = page.locator("figure img").evaluate_all("els=>els.every(e=>e.getBoundingClientRect().width>0)")
        if not print_imgs: errors.append("Print figures have zero width")
    page.close()
    return {"page":path,"viewport":width,"errors":errors,"screenshot":str(screenshot.name)}

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--out",default="qa-results")
    args=parser.parse_args()
    out=Path(args.out).resolve()
    out.mkdir(parents=True,exist_ok=True)
    results=[]
    with sync_playwright() as pw:
        browser=pw.chromium.launch(headless=True)
        for path in PAGES:
            for width in WIDTHS:
                result=check(path,width,out,browser)
                results.append(result)
                print(("FAIL" if result["errors"] else "PASS"),path,width,result["errors"])
        browser.close()
    (out/"report.json").write_text(json.dumps(results,ensure_ascii=False,indent=2),encoding="utf-8")
    errors=sum(len(result["errors"]) for result in results)
    print(f"Browser QA: {len(results)} viewport cases, {errors} errors")
    return 1 if errors else 0

if __name__ == "__main__":
    sys.exit(main())
