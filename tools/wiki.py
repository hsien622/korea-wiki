#!/usr/bin/env python3
"""LLM Wiki 工具。  python3 tools/wiki.py build  產生 index.html
                   python3 tools/wiki.py check  檢查來源、Wiki、簡報"""
import re, sys, json, html, pathlib
R = pathlib.Path(__file__).resolve().parent.parent
OFFICIAL = ("boca.gov.tw", "visitkorea.or.kr")
CLAIM = re.compile(r"^- \{([a-z]+-\d+)\} 【(官方|民間)】(.+?) ((?:\[S\d\d\])+)$")
e = html.escape

def sources():
    out = {}
    for p in sorted((R / "raw").glob("*.txt")):
        t = p.read_text(encoding="utf-8-sig")
        urls = re.search(r"^來源網址：(.*)$", t, re.M).group(1)
        out["S" + p.name[:2]] = {"file": p.name, "official": any(d in urls for d in OFFICIAL)}
    return out

def claims():
    out, bad = {}, []
    for p in sorted((R / "wiki").glob("*.md")):
        if p.name in ("index.md", "log.md"): continue
        for n, line in enumerate(p.read_text(encoding="utf-8").splitlines(), 1):
            if not line.startswith("- "): continue
            m = CLAIM.match(line.strip())
            if not m: bad.append(f"{p.name}:{n} 格式錯誤，需為 - {{id}} 【官方|民間】內容 [Sxx]"); continue
            cid, label, text, refs = m.groups()
            if cid in out: bad.append(f"{p.name}:{n} 重複的主張 id：{cid}")
            out[cid] = {"label": label, "text": text, "refs": re.findall(r"S\d\d", refs)}
    return out, bad

def check():
    src, (cl, err) = sources(), claims()
    for cid, c in cl.items():
        for s in c["refs"]:
            if s not in src: err.append(f"{cid} 引用了不存在的來源 {s}")
        if c["label"] == "官方" and not any(src.get(s, {}).get("official") for s in c["refs"]):
            err.append(f"{cid} 標【官方】，但引用的來源都沒有官方網址（boca.gov.tw、visitkorea.or.kr）")
    used = {s for c in cl.values() for s in c["refs"]}
    err += [f"{s} 已放進 raw/ 但沒有任何 Wiki 主張引用（ingest 不完整）" for s in src if s not in used]
    h = R / "index.html"
    secs = re.findall(r'<section class="slide.*?</section>', h.read_text(encoding="utf-8"), re.S) if h.exists() else []
    if not secs: err.append("找不到簡報 index.html，請先執行 build")
    for i, sec in enumerate(secs, 1):
        m = re.search(r'data-wiki="([a-z]+)"', sec)
        if not m or not (R / "wiki" / f"{m.group(1)}.md").exists(): err.append(f"第 {i} 頁缺少有效的 data-wiki")
        for note in re.findall(r'<p class="note">(.*?)</p>', sec, re.S):
            if re.search(r"\d", note): err.append(f"第 {i} 頁教學說明含數字，只有 Wiki 主張可以出現數字")
        for cid, text in re.findall(r'data-claim="([^"]+)">.*?<p>(.*?)</p>', sec, re.S):
            if cid not in cl: err.append(f"第 {i} 頁引用了 Wiki 沒有的主張 {cid}")
            elif html.unescape(text) != cl[cid]["text"]: err.append(f"第 {i} 頁的 {cid} 內容和 Wiki 不一致")
    print(f"來源 {len(src)} 份，主張 {len(cl)} 條，簡報 {len(secs)} 頁，錯誤 {len(err)} 項")
    print("\n".join("  ✗ " + x for x in err) if err else "通過：每個主張有來源、官方標示成立、簡報內容都能在 Wiki 找到")
    sys.exit(1 if err else 0)

TEMPLATE = """<!DOCTYPE html><html lang="zh-Hant"><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>韓國自由行新手指南</title>
<style>:root{--bg:#e3eefa;--card:#f8fbff;--navy:#1f3a5f;--red:#c8553d;--mute:#4b5b70}*{box-sizing:border-box}
body{margin:0;background:var(--bg);color:#1f2a37;font-family:"PingFang TC","Microsoft JhengHei","Noto Sans TC",sans-serif;padding:16px}
.deck{max-width:880px;margin:0 auto;background:var(--card);border:2px solid var(--navy);border-radius:12px;overflow:hidden}
.bar{height:6px;background:#b9d0e8}.bar i{display:block;height:100%;background:var(--red);width:0}
.top{display:flex;justify-content:space-between;padding:10px 20px;font-size:.85rem;color:var(--mute);border-bottom:1px solid #b9d0e8}
.slide{display:none;padding:28px 32px;min-height:440px}.slide.on{display:block}
.cover{text-align:center;padding-top:90px}.cover h1{color:var(--navy);font-size:2.2rem}
.kicker{color:var(--red);font-weight:700;font-size:.85rem}h2{color:var(--navy);margin:4px 0 6px}
.note{color:var(--mute);margin:0 0 16px}.card{border:1px solid var(--navy);border-radius:10px;padding:10px 14px;margin-bottom:10px;background:#fff}
.card p{margin:4px 0}.card small{color:var(--mute)}.tag{font-size:.75rem;border:1px solid;border-radius:999px;padding:0 8px;margin-right:6px}
.o{color:#2f7d5b}.c{color:#b7791f}.nav{display:flex;justify-content:space-between;padding:12px 20px;border-top:1px solid #b9d0e8}
button{font:inherit;background:var(--navy);color:#fff;border:0;border-radius:8px;padding:8px 18px;cursor:pointer}button:disabled{opacity:.35}
details{margin-bottom:10px}summary{cursor:pointer;font-weight:600;margin-bottom:6px}@media print{.slide{display:block;break-after:page}.nav,.bar{display:none}}</style></head><body>
<div class="deck"><div class="bar"><i id="pg"></i></div><div class="top"><span id="ct"></span><span>知識來源：LLM Wiki（raw/ 原始資料）</span></div>
__BODY__
<div class="nav"><button id="pv">← 上一頁</button><button id="nx">下一頁 →</button></div></div>
<script>const S=[...document.querySelectorAll('.slide')];let i=0;
function go(n){i=Math.max(0,Math.min(S.length-1,n));S.forEach((s,k)=>s.classList.toggle('on',k===i));
pv.disabled=i===0;nx.disabled=i===S.length-1;ct.textContent='第 '+(i+1)+' / '+S.length+' 頁';pg.style.width=(i+1)/S.length*100+'%'}
pv.onclick=()=>go(i-1);nx.onclick=()=>go(i+1);document.onkeydown=e=>{if(e.key==='ArrowRight')go(i+1);if(e.key==='ArrowLeft')go(i-1)};go(0)</script></body></html>"""

def build():
    src, (cl, _) = sources(), claims()
    spec = json.loads((R / "tools" / "slides.json").read_text(encoding="utf-8"))
    def card(cid):
        c = cl[cid]
        links = " ".join(f'<a href="raw/{src[r]["file"]}" target="_blank">{r}</a>' for r in c["refs"])
        cls, lab = ("o", "官方") if c["label"] == "官方" else ("c", "民間")
        return f'<div class="card" data-claim="{cid}"><span class="tag {cls}">{lab}</span><p>{e(c["text"])}</p><small>來源：{links}</small></div>'
    body = []
    for s in spec:
        if s.get("cover"):
            body.append(f'<section class="slide cover" data-wiki="index"><h1>{e(s["title"])}</h1><p class="note">{e(s["note"])}</p></section>')
            continue
        if s.get("quiz"):
            inner = "".join(f'<details><summary>{e(q["q"])}</summary>{card(q["claim"])}</details>' for q in s["items"])
        else:
            inner = "".join(card(c) for c in s["claims"])
        body.append(f'<section class="slide" data-wiki="{s["wiki"]}"><div class="kicker">Wiki：wiki/{s["wiki"]}.md</div><h2>{e(s["title"])}</h2><p class="note">{e(s["note"])}</p>{inner}</section>')
    (R / "index.html").write_text(TEMPLATE.replace("__BODY__", "\n".join(body)), encoding="utf-8")
    print(f"已產生 index.html（{len(spec)} 頁）")

if __name__ == "__main__" and len(sys.argv) > 1 and sys.argv[1] in ("build", "check"):
    {"build": build, "check": check}[sys.argv[1]]()
else:
    print(__doc__)
