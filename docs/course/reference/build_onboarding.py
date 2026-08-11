#!/usr/bin/env python3
"""Render parrot-onboarding.md -> reference/onboarding.html (Mermaid diagrams render in-browser).

Re-run this whenever the onboarding doc changes:
    python3 reference/build_onboarding.py
"""
import datetime
import pathlib

SRC = pathlib.Path("/home/odoo/Data/Dev/Odoo/parrot-onboarding.md")
OUT = pathlib.Path("/home/odoo/Data/Dev/Odoo/parrot-voip-teaching/reference/onboarding.html")

TEMPLATE = r"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Parrot VoIP — Onboarding Guide (rendered)</title>
<style>
  :root{--ink:#1c1a17;--muted:#6b655c;--faint:#9a948a;--rule:#e4ded3;--paper:#fbf9f4;--parrot:#1a7a4c;--parrot-deep:#0f5a37;--accent-bg:#eef3ec}
  *{box-sizing:border-box}
  html{font-size:16.5px}
  body{margin:0;background:var(--paper);color:var(--ink);font-family:ui-sans-serif,system-ui,sans-serif;line-height:1.6}
  .wrap{max-width:880px;margin:0 auto;padding:2.6rem 1.4rem 5rem}
  header.doc{border-bottom:2px solid var(--ink);padding-bottom:1rem;margin-bottom:1.4rem}
  .kicker{font-family:ui-sans-serif,system-ui,sans-serif;text-transform:uppercase;letter-spacing:.16em;font-size:.7rem;color:var(--parrot);font-weight:700}
  header.doc h1{font-size:2.1rem;margin:.3rem 0 .3rem}
  .sub{color:var(--muted);font-size:.92rem;margin:0;font-family:ui-sans-serif,system-ui,sans-serif}
  .md h1{font-size:1.9rem;margin:2.4rem 0 .4rem;padding-top:.8rem;border-top:2px solid var(--rule)}
  .md h2{font-size:1.45rem;margin:2rem 0 .3rem;padding-top:.6rem;border-top:1px solid var(--rule)}
  .md h3{font-size:1.15rem;margin:1.5rem 0 .2rem}
  .md h4{font-size:1rem;margin:1.2rem 0 .2rem;font-family:ui-sans-serif,system-ui,sans-serif}
  .md p,.md li{font-size:1.02rem}
  .md a{color:var(--parrot-deep)}
  .md code{font-family:ui-monospace,"SF Mono",Menlo,Consolas,monospace;font-size:.82em;background:#f0ece3;padding:.05rem .3rem;border-radius:4px}
  .md pre{background:#2a2722;color:#f3efe7;padding:1rem 1.1rem;border-radius:8px;overflow-x:auto;font-size:.84rem}
  .md pre code{background:none;color:inherit;padding:0}
  .md blockquote{border-left:3px solid var(--parrot);background:#fff;margin:1rem 0;padding:.6rem 1rem;color:var(--muted);border-radius:4px}
  .md table{border-collapse:collapse;width:100%;font-size:.92rem;margin:1rem 0;background:#fff;border-radius:6px;overflow:hidden}
  .md th,.md td{text-align:left;padding:.5rem .7rem;border-bottom:1px solid var(--rule);vertical-align:top}
  .md th{font-family:ui-sans-serif,system-ui,sans-serif;font-size:.74rem;text-transform:uppercase;letter-spacing:.05em;color:var(--muted);background:var(--accent-bg)}
  .md hr{border:0;border-top:1px solid var(--rule);margin:2rem 0}
  .mermaid{background:#fff;border:1px solid var(--rule);border-radius:8px;padding:1rem;margin:1.2rem 0;text-align:center;overflow-x:auto}
  .backlink{font-family:ui-sans-serif,system-ui,sans-serif;font-size:.85rem;margin-bottom:1rem}
  @media print{body{background:#fff}.md pre{background:#f4f1ea;color:#000;border:1px solid var(--rule)}}
</style>
</head>
<body>
<div class="wrap">
  <header class="doc">
    <div class="kicker">🦜 Parrot VoIP · Reference</div>
    <h1>Onboarding Guide</h1>
    <p class="sub">Rendered snapshot of <code>parrot-onboarding.md</code> (canonical: Obsidian vault + <code>Data/Dev/Odoo/</code>). Mermaid diagrams render below. Regenerate with <code>reference/build_onboarding.py</code> when the doc changes. · snapshot __DATE__</p>
    <p class="backlink"><a href="../index.html">🦜 ← Course home</a> · <a href="./glossary.html">📑 Glossary</a> · <a href="../lessons/0001-odoo-becomes-a-phone-company.html">▶ Start Lesson 1</a></p>
  </header>
  <article id="out" class="md">Rendering… (the Mermaid &amp; Markdown libraries load from the local <code>vendor/</code> folder — works offline).</article>
</div>
<script type="text/markdown" id="md">__MD__</script>
<script src="../vendor/marked.min.js"></script>
<script src="../vendor/mermaid.min.js"></script>
<script>
(function(){
  var md = document.getElementById("md").textContent;
  var out = document.getElementById("out");
  if(!window.marked){
    out.innerHTML="";
    var pre=document.createElement("pre");
    pre.style.whiteSpace="pre-wrap"; pre.style.background="none"; pre.style.color="inherit";
    pre.textContent=md; out.appendChild(pre); return;
  }
  var renderer=new marked.Renderer();
  var origCode=renderer.code.bind(renderer);
  renderer.code=function(code, lang){
    if((lang||"").trim()==="mermaid"){ return '<div class="mermaid">'+code+'</div>'; }
    return origCode(code, lang);
  };
  marked.setOptions({renderer:renderer, headerIds:true, mangle:false, gfm:true});
  out.innerHTML=marked.parse(md);
  if(window.mermaid){
    mermaid.initialize({startOnLoad:false, theme:"neutral", securityLevel:"loose"});
    try{ mermaid.run({querySelector:".mermaid"}); }catch(e){ console.warn("mermaid:", e); }
  }
})();
</script>
</body>
</html>
"""

def main():
    md = SRC.read_text(encoding="utf-8")
    md = md.replace("</script>", "<\\/script>")  # defensive: don't end the embed early
    out = TEMPLATE.replace("__MD__", md).replace("__DATE__", datetime.date.today().isoformat())
    OUT.write_text(out, encoding="utf-8")
    print("wrote", OUT, "(%d bytes)" % len(out))

if __name__ == "__main__":
    main()
