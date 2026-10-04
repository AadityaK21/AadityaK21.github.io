import asyncio, os, html
from playwright.async_api import async_playwright
import notes
R = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
items = [
  ("sextant", "Project", "Sextant", "A mini-Foundry: ontology, entity resolution and cell-level lineage over an LSM engine written from scratch."),
  ("nanoserve", "Project", "nanoserve", "An LLM inference server written from scratch. 1.65× throughput and 12× lower p99 time to first token."),
  ("legal-audio", "Research", "Legal audio to notes", "A fully local pipeline that turns court audio into notes where every line links back to the record."),
  ("st-bemd", "Research", "ST-BEMD", "Direction-adaptive 2-D EMD for fingerprints, and an honest look at what its metric measures."),
  ("company-hub", "Project", "Company Hub", "A live interview-prep site ranking 3,400 LeetCode questions by how often 656 companies ask them."),
] + [(n["slug"], "Note", n["title"], n["dek"]) for n in notes.NOTES]

TPL = """<!doctype html><html><head><meta charset="utf-8"><link rel="stylesheet" href="/assets/css/site.css">
<style>
html,body{{margin:0;width:1200px;height:630px;overflow:hidden;background:var(--paper)}}
.o{{position:relative;width:1200px;height:630px;padding:44px 56px;box-sizing:border-box;display:grid;grid-template-columns:1fr 300px;grid-template-rows:auto 1fr auto;column-gap:48px}}
.t{{grid-column:1/-1;display:flex;justify-content:space-between;align-items:center;padding-bottom:22px;border-bottom:1px solid var(--rule)}}
.t .logo{{font-size:30px}} .u{{font-size:22px;color:var(--mute)}}
.m{{align-self:center;padding-top:20px}}
.k{{display:inline-block;padding:7px 16px;border-radius:999px;background:var(--ink);color:var(--paper);font-size:20px;font-weight:550;margin-bottom:22px}}
h1{{font-size:{size}px;font-weight:740;font-stretch:96%;letter-spacing:-0.055em;line-height:0.92;color:var(--ink);margin:0 0 22px;text-wrap:balance}}
.d{{font-size:26px;line-height:1.3;color:var(--ink-2);max-width:30ch;margin:0}}
.f{{grid-row:2/4;grid-column:2;align-self:center;margin-top:20px}}
.f .portrait{{height:440px;min-height:0;border-radius:6px}} .f .portrait canvas{{height:100%}}
.b{{font-size:20px;color:var(--mute);align-self:end}}
.js .name .ch{{animation:none!important}}
</style></head><body>
<div class="o">
 <div class="t"><span class="logo">ak<span class="logo-dot"></span></span><span class="u">aadityakumawat.me</span></div>
 <div class="m"><span class="k">{kind}</span><h1>{title}</h1><p class="d">{dek}</p></div>
 <div class="f"><figure class="portrait"><canvas data-ridges data-spacing="6"></canvas></figure></div>
 <div class="b">Aaditya Kumawat, IIT Delhi</div>
</div>
<script>window.matchMedia=function(q){{return{{matches:q.indexOf('reduced-motion')>-1,addEventListener(){{}},addListener(){{}}}}}};</script>
<script src="/assets/js/site.js"></script>
</body></html>"""

async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch()
        pg = await b.new_page(viewport={"width": 1200, "height": 630})
        for slug, kind, title, dek in items:
            size = 132 if len(title) <= 12 else (96 if len(title) <= 22 else 84)
            fn = f"_og_{slug}.html"
            open(os.path.join(R, fn), "w").write(TPL.format(kind=kind, title=html.escape(title), dek=html.escape(dek), size=size))
            await pg.goto(f"http://localhost:8765/{fn}", wait_until="networkidle")
            await pg.wait_for_timeout(500)
            await pg.screenshot(path=os.path.join(R, "assets/og", f"{slug}.png"))
            os.remove(os.path.join(R, fn))
            print("og", slug)
        await b.close()
asyncio.run(main())
