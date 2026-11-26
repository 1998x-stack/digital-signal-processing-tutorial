#!/usr/bin/env python3
"""Offline structural gate for the DSP static site; Python stdlib only."""
from html.parser import HTMLParser
from pathlib import Path
import json
import re
import sys
import xml.etree.ElementTree as ET
from urllib.parse import urlparse, unquote
ROOT=Path(__file__).resolve().parent.parent
issues=[]
class Page(HTMLParser):
 def __init__(self):
  super().__init__(convert_charrefs=True); self.refs=[]; self.ids=set(); self.h1=0; self.figures=0; self.captions=0; self.math=0; self.labs=0
 def handle_starttag(self,t,attrs):
  a=dict(attrs)
  if a.get("id"): self.ids.add(a["id"])
  if t=="h1": self.h1+=1
  if t=="figure": self.figures+=1
  if t=="figcaption": self.captions+=1
  if t=="math": self.math+=1
  if a.get("data-lab") or a.get("data-spectrum-lab"): self.labs+=1
  for key in ("src","href"):
   if a.get(key): self.refs.append(a[key])
def error(s): issues.append(s)
def page(path,upgrade=False):
 if not path.is_file(): error(f"Missing {path.relative_to(ROOT)}");return
 src=path.read_text(encoding="utf-8"); p=Page();p.feed(src)
 if upgrade:
  if p.h1!=1:error(f"{path.name}: expected one H1 got {p.h1}")
  if p.figures<2 or p.captions!=p.figures:error(f"{path.name}: figure/caption mismatch")
  if p.math<1:error(f"{path.name}: MathML missing")
  if p.labs!=1:error(f"{path.name}: expected one interactive lab")
  if "讲义介绍了" in src:error(f"{path.name}: contextless lecture preamble")
 for url in p.refs:
  u=urlparse(url)
  if u.scheme or url.startswith("//") or url.startswith("mailto:"):continue
  if u.path:
   target=(path.parent/unquote(u.path)).resolve()
   if not target.is_relative_to(ROOT) or not target.exists(): error(f"{path.relative_to(ROOT)}: broken reference {url}")
  elif u.fragment and u.fragment not in p.ids: error(f"{path.relative_to(ROOT)}: missing fragment {url}")
def run():
 try:
  c=json.loads((ROOT/"courses.json").read_text(encoding="utf-8"))
  assert len(c["chapters"])==28 and c["chapterCount"]==28
  assert [x["num"] for x in c["chapters"]]==[f"{i:02d}" for i in range(1,29)]
 except (OSError,ValueError,AssertionError,KeyError) as exc: error(f"Invalid catalog: {exc}");return 1
 page(ROOT/"index.html")
 for i in range(1,29):
  n=f"{i:02d}"; page(ROOT/f"{n}.html");page(ROOT/"chapters"/f"{n}.html",i<=22)
  if not (ROOT/c["chapters"][i-1]["file"]).exists():error(f"Catalog broken: {n}")
 for path in sorted((ROOT/"assets/svg").glob("*.svg")):
  try:
   root=ET.parse(path).getroot()
   if not root.tag.endswith("svg") or not root.get("viewBox"):error(f"{path.name}: no viewBox")
   children=list(root)
   if not any(e.tag.endswith("title") for e in children) or not any(e.tag.endswith("desc") for e in children):error(f"{path.name}: missing title/desc")
  except ET.ParseError as exc:error(f"{path.name}: XML parse {exc}")
 for i in range(1,23):
  if not (ROOT/"evidence"/f"{i:02d}.json").exists():error(f"evidence missing {i:02d}")
 if issues:
  print("\n".join("FAIL "+i for i in issues));return 1
 print("PASS: 28 catalog entries, article links, 22 upgraded chapters and SVG XML")
 return 0
if __name__=="__main__": sys.exit(run())
