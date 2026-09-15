#!/usr/bin/env python3
"""Offline structure/link/JavaScript checks. Diagram rendering needs a browser."""
from html.parser import HTMLParser
from pathlib import Path
import subprocess
from urllib.parse import unquote, urlsplit

ROOT = Path(__file__).resolve().parent.parent


class Page(HTMLParser):
    def __init__(self, source):
        super().__init__()
        self.ids, self.links, self.scripts = set(), [], []
        self.duplicates, self.diagram_count, self.sources = [], 0, []
        self.script = None
        self.feed(source)

    def handle_starttag(self, tag, attributes):
        attrs = dict(attributes)
        for name in ("id", "name"):
            if attrs.get(name):
                if attrs[name] in self.ids:
                    self.duplicates.append(attrs[name])
                self.ids.add(attrs[name])
        for name in ("href", "src"):
            if attrs.get(name):
                self.links.append(attrs[name])
        if "mermaid" in attrs.get("class", "").split() and tag in {"pre", "div"}:
            self.diagram_count += 1
        if tag == "script":
            if attrs.get("src"):
                self.sources.append(attrs["src"])
            if not attrs.get("src") and attrs.get("type", "") in {"", "text/javascript", "module"}:
                self.script = []

    def handle_data(self, value):
        if self.script is not None:
            self.script.append(value)

    def handle_endtag(self, tag):
        if tag == "script" and self.script is not None:
            self.scripts.append("".join(self.script))
            self.script = None


def main():
    pages = {path.resolve(): Page(path.read_text()) for path in ROOT.rglob("*.html")}
    issues, scripts = [], 0
    for path, page in pages.items():
        issues.extend(f"{path.relative_to(ROOT)}: duplicate id {value}" for value in page.duplicates)
        for href in page.links:
            link = urlsplit(href)
            if link.scheme or link.netloc:
                continue
            target = (path.parent / unquote(link.path)).resolve() if link.path else path
            if not target.exists():
                issues.append(f"{path.relative_to(ROOT)}: missing target {href}")
            elif link.fragment and target in pages and unquote(link.fragment) not in pages[target].ids:
                issues.append(f"{path.relative_to(ROOT)}: missing anchor {href}")
        for source in page.scripts:
            scripts += 1
            result = subprocess.run(["node", "--check"], input=source, text=True, capture_output=True)
            if result.returncode:
                issues.append(f"{path.relative_to(ROOT)}: JavaScript syntax error: {result.stderr}")
        if page.diagram_count and not any("mermaid" in source for source in page.sources):
            issues.append(f"{path.relative_to(ROOT)}: diagram library not loaded")
        if page.diagram_count and not any("initializeCourseDiagrams" in script or "mermaid.initialize" in script for script in page.scripts):
            issues.append(f"{path.relative_to(ROOT)}: diagrams not initialized")
    subprocess.run(["node", "--check", str(ROOT / "assets/interactions.js")], check=True)
    # The onboarding Markdown renders dynamically; check its decoded links/ids
    # with the exact vendored renderer instead of guessing a heading slug.
    renderer = r"""
const fs=require('fs'), vm=require('vm');
const root=process.argv[1], context={};vm.createContext(context);
vm.runInContext(fs.readFileSync(root+'/vendor/marked.min.js','utf8'),context);
const html=fs.readFileSync(root+'/reference/onboarding.html','utf8');
const md=html.match(/<script type="text\/markdown" id="md">([\s\S]*?)<\/script>/)[1];
context.marked.setOptions({headerIds:true,mangle:false,gfm:true});
const output=context.marked.parse(md),ids=new Set([...output.matchAll(/\bid="([^"]*)"/g)].map(m=>m[1]));
for(const match of output.matchAll(/\bhref="#([^"]*)"/g))if(!ids.has(decodeURIComponent(match[1])))throw new Error('Broken rendered-guide anchor: '+match[1]);
"""
    result = subprocess.run(["node", "-e", renderer, str(ROOT)], text=True, capture_output=True)
    if result.returncode:
        issues.append(result.stderr)
    if issues:
        raise SystemExit("\n".join(issues))
    print(f"PASS: {len(pages)} pages, local targets/anchors, unique ids, {scripts} inline scripts, shared JS and diagram bootstrap.")


if __name__ == "__main__":
    main()
