import json, os, sys
sys.path.insert(0, os.path.dirname(__file__))
from common import *
from visuals import SEXTANT_TERM_SHORT, NANOSERVE_BARS, NANOSERVE_SIM, COMPANYHUB_MOCK
import pages
import notes
import cfchart

OUT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))


def write(path, html):
    full = os.path.join(OUT, path)
    os.makedirs(os.path.dirname(full), exist_ok=True)
    with open(full, "w", encoding="utf-8") as f:
        f.write(html)
    print("wrote", path, len(html))


def facts(items):
    return "<dl class=\"facts\">" + "".join(
        f"<div><dt>{label}</dt><dd>{value}</dd></div>" for value, label in items) + "</dl>"


def row(slug, when, kind, stack, title, sub, text, fact_items, links, visual, visual_cls="", visual_label=""):
    link_html = f'<a class="btn btn-sm" href="/work/{slug}/">Read the case study<span class="btn-icon">{ARROW}</span></a>'
    for label, href in links:
        link_html += f'<a class="text-link" href="{href}">{label}</a>'
    return f"""
    <article class="row" aria-labelledby="t-{slug}">
      <dl class="row-meta">
        <dt>When</dt><dd class="when">{when}</dd>
        <dt>Kind</dt><dd>{kind}</dd>
        <dt>Stack</dt><dd>{stack}</dd>
      </dl>
      <div class="row-body">
        <h3 class="row-title" id="t-{slug}"><a href="/work/{slug}/" style="view-transition-name: vt-{slug}">{title}</a><span class="row-sub">{sub}</span></h3>
        <p class="row-text">{text}</p>
        {facts(fact_items)}
        <div class="row-links">{link_html}</div>
      </div>
      <a class="row-visual {visual_cls}" href="/work/{slug}/" tabindex="-1" aria-label="{visual_label}">{visual}</a>
    </article>"""


person = {
    "@context": "https://schema.org",
    "@type": "Person",
    "name": "Aaditya Kumawat",
    "url": SITE + "/",
    "email": "mailto:" + EMAIL,
    "jobTitle": "B.Tech student, Production and Industrial Engineering",
    "affiliation": {"@type": "CollegeOrUniversity", "name": "Indian Institute of Technology Delhi"},
    "alumniOf": {"@type": "CollegeOrUniversity", "name": "Indian Institute of Technology Delhi"},
    "sameAs": [GITHUB, LINKEDIN, CODEFORCES, ORCID],
    "knowsAbout": ["Machine learning systems", "LLM inference", "Signal processing", "Storage engines", "C++", "Python"],
}

index = head(
    "Aaditya Kumawat",
    "Aaditya Kumawat is an engineering student at IIT Delhi who builds ML systems and signal processing tools from scratch: an LLM inference server, an LSM-backed lineage platform, and a direction-adaptive EMD method.",
    "/",
    extra='<script type="application/ld+json">' + json.dumps(person) + "</script>\n",
) + header(home=True) + f"""
<main id="main">
  <section class="hero wrap" aria-label="Introduction">
    <div class="hero-grid">
      <div class="cell cell-meta">
        <p>
          <span class="place">New Delhi, India</span>
          <span class="clock num" data-clock>IST</span>
          <span class="today" data-date></span>
        </p>
        <div class="cell-bottom">
          <p class="lastpush" data-lastpush="AadityaK21" hidden>Last pushed to <a href="https://github.com/AadityaK21">GitHub</a>, <span data-ago></span></p>
          <p class="status"><span class="pulse" aria-hidden="true"></span>Open to Summer 2027 internships</p>
        </div>
      </div>
      <div class="cell cell-portrait">
        <figure class="portrait">
          <span class="mark mark-tl" aria-hidden="true"></span><span class="mark mark-tr" aria-hidden="true"></span>
          <span class="mark mark-bl" aria-hidden="true"></span><span class="mark mark-br" aria-hidden="true"></span>
          <canvas data-ridges role="img" aria-label="A fingerprint-like ridge pattern, drawn live in the browser"></canvas>
          <figcaption data-angle data-default="A ridge field, drawn live. Hover or tap to read its direction.">A ridge field, drawn live. Hover or tap to read its direction.</figcaption>
        </figure>
      </div>
      <div class="cell cell-intro">
        <p class="intro">I&rsquo;m a third-year engineering student at IIT Delhi. I build ML systems and signal processing tools from scratch, then test them until the numbers hold up.</p>
        <div class="intro-actions">
          <a class="btn" href="#work">See my work<span class="btn-icon">{ARROW}</span></a>
          <a class="btn btn-ghost" href="mailto:{EMAIL}">Email me</a>
        </div>
      </div>
    </div>
    <h1 class="name" data-fit>aaditya kumawat</h1>
  </section>

  <section class="section wrap" id="work" aria-labelledby="work-title">
    <div class="section-head">
      <h2 class="section-title" id="work-title">Selected work<span class="count">5</span></h2>
      <p class="section-lede">Things I built on my own in 2026, and the numbers that came out of them.</p>
    </div>
    <div class="rows">
""" + row(
    "sextant", "Jun&ndash;Aug 2026", "Self-led project", "C++20, React, TypeScript, CMake",
    "Sextant", "Ontology and lineage platform",
    "A mini-Foundry for maritime data. It pulls port and vessel records from three public sources, merges duplicates into real entities, and can trace every stored value back to the source row and transforms that produced it. Underneath is an LSM storage engine I wrote from scratch.",
    [("100%", "of 4,201 values replay from source"), ("1.53M", "batched writes per second"), ("0.991", "F1 on entity resolution")],
    [("Code on GitHub", GITHUB + "/sextant")],
    SEXTANT_TERM_SHORT, "", "Sextant case study",
) + row(
    "nanoserve", "Jun&ndash;Jul 2026", "Self-led project", "PyTorch, Triton, CUDA",
    "nanoserve", "LLM inference server",
    "An LLM inference server built without vLLM or TGI: a paged KV cache, continuous batching with chunked prefill, a fused Triton attention kernel and INT4/INT8 weight quantization. vLLM only appears as an outside yardstick.",
    [("1.65&times;", "throughput over static batching"), ("12&times;", "lower p99 time to first token"), ("92", "tests")],
    [("Code on GitHub", GITHUB + "/nanoserve")],
    NANOSERVE_SIM, "", "nanoserve case study",
) + row(
    "st-bemd", "May&ndash;Jul 2026", "Self-led project", "Python, NumPy, SciPy",
    "ST-BEMD", "Direction-adaptive 2-D EMD",
    "A method for splitting 2-D signals like fingerprints into their component layers. It bends along the ridges instead of treating every direction alike. I tested it against four baselines that I also wrote from scratch.",
    [("3.3&deg;", "better than the baseline under heavy noise"), ("4", "baselines written from scratch"), ("78%", "of the clean-data gain traced by ablation")],
    [("Code on GitHub", GITHUB + "/stbemd-signal-processing")],
    '<img src="/assets/img/stbemd-paired.webp" width="830" height="666" alt="" loading="lazy" decoding="async">', "is-figure", "ST-BEMD case study",
) + row(
    "company-hub", "Jun 2026 to now", "Live product", "Next.js 15, TypeScript, PostgreSQL",
    "Company Hub", "Interview prep platform",
    "A live site that ranks LeetCode questions by how often each company asks them, with progress tracking, spaced revision and an in-browser code editor. I run it in production and fixed the problems that only show up under real traffic.",
    [("3,400", "questions indexed"), ("656", "companies"), ("9", "languages in the editor")],
    [("Visit companyhub.fun", "https://companyhub.fun"), ("Code", GITHUB + "/leetcode-company-hub")],
    COMPANYHUB_MOCK, "", "Company Hub case study",
) + f"""
    </div>

    <h3 class="subhead">Also</h3>
    <div class="list">
      <article class="item">
        <h4 class="item-title"><a href="{GITHUB}/qrt-stock-return-prediction">QRT return prediction</a></h4>
        <p class="item-text">Predicting whether a stock rises tomorrow from anonymised market data, built to resist leakage: purged cross-validation with a 20-day embargo and a 72-day holdout that tuning never sees. A simulator that knows the true signal shows the model captures 73.7% of the edge that is actually there.<span class="by">LightGBM, XGBoost, Optuna</span></p>
        <p class="item-side"><span>Mar 2026</span><span><a href="{GITHUB}/qrt-stock-return-prediction">Code</a></span></p>
      </article>
    </div>
  </section>

  <section class="section wrap" id="research" aria-labelledby="research-title">
    <div class="section-head">
      <h2 class="section-title" id="research-title">Research<span class="count">2</span></h2>
      <p class="section-lede">Work done in a lab and with a professor.</p>
    </div>
    <div class="rows">
""" + row(
    "legal-audio", "May&ndash;Jul 2026", "Research intern (remote)", "Applied AI Laboratory, HEC Lausanne",
    "Legal audio to notes", "Legal AI pipeline",
    "A fully local pipeline that turns court audio into speaker-attributed notes. Every note links back to the moment in the recording it came from, and nothing leaves the machine. In one mode the language model can only pick sentence ids, so it has no way to invent text.",
    [("6.9%", "word error rate"), ("7.9%", "diarization error rate"), ("100%", "verbatim in extractive mode")],
    [],
    '<img src="/assets/img/legal-audio-crop.webp" width="1400" height="963" alt="" loading="lazy" decoding="async">', "", "Legal audio case study",
) + f"""
    </div>
    <div class="list">
      <article class="item">
        <h3 class="item-title"><a href="{GITHUB}/llm-as-a-judge-survey/blob/main/llm_as_a_judge_survey.pdf">Towards Reliable LLM-as-a-Judge Systems</a></h3>
        <p class="item-text">A survey of five directions in using LLMs to grade other LLMs: pairwise versus pointwise protocols, checklist assessment, MCTS reasoning judges, multilingual judges and prompt-injection security, brought together into one framework.<span class="by">Co-authored with Suvit Vishwakarma and Avaneesh R, advised by Prof. Amartansh Dubey.</span></p>
        <p class="item-side"><span>2026</span><span><a href="{GITHUB}/llm-as-a-judge-survey/blob/main/llm_as_a_judge_survey.pdf">Paper (PDF)</a></span></p>
      </article>
    </div>
  </section>

  <section class="section wrap" id="notes" aria-labelledby="notes-title">
    <div class="section-head">
      <h2 class="section-title" id="notes-title">Notes<span class="count">""" + str(len(notes.NOTES)) + f"""</span></h2>
      <p class="section-lede">Short write-ups on what my projects measured, including the parts that didn&rsquo;t go to plan.</p>
    </div>
    """ + notes.notes_list_html() + f"""
  </section>

  <section class="section wrap" id="recognition" aria-labelledby="rec-title">
    <div class="section-head">
      <h2 class="section-title" id="rec-title">Recognition</h2>
    </div>
    """ + cfchart.chart() + f"""
    <div class="list honors">
      <div class="item"><p class="item-title"><strong>Candidate Master</strong> on Codeforces as <a class="text-link" href="{CODEFORCES}">codeleon</a>, reached in 8 rated contests from unrated; peak rating 1935</p><p class="item-side num">2026</p></div>
      <div class="item"><p class="item-title">Rank <strong>170</strong> in Codeforces Educational Round 193</p><p class="item-side num">2026</p></div>
      <div class="item"><p class="item-title">Letter of recommendation from the <strong>Applied AI Laboratory, HEC Lausanne</strong></p><p class="item-side num">2026</p></div>
      <div class="item"><p class="item-title">All India Rank in the <strong>top 3%</strong> of about 200,000 candidates who qualified JEE Advanced</p><p class="item-side num">2024</p></div>
      <div class="item"><p class="item-title"><strong>99.33 percentile</strong> in JEE Main, top 0.7% of about 1.5 million candidates</p><p class="item-side num">2024</p></div>
    </div>
  </section>

  <section class="section wrap" id="about" aria-labelledby="about-title">
    <div class="section-head">
      <h2 class="section-title" id="about-title">About</h2>
    </div>
    <div class="about">
      <div class="about-text">
        <p>I&rsquo;m in the third year of a B.Tech in Production and Industrial Engineering at IIT Delhi, graduating in 2028.</p>
        <p>Most of what I build sits where machine learning meets systems: inference servers, storage engines and signal processing methods. I like rebuilding things from first principles to understand them, and I try to break my own numbers before anyone else does.</p>
        <p>Outside of projects, I do competitive programming, mostly on Codeforces.</p>
      </div>
      <div class="about-side">
        <dl class="skills">
          <div><dt>Education</dt><dd>B.Tech, Production and Industrial Engineering, IIT Delhi, 2024&ndash;2028</dd></div>
          <div><dt>Languages</dt><dd>C++20, Python, TypeScript</dd></div>
          <div><dt>Machine learning</dt><dd>PyTorch, Hugging Face Transformers, scikit-learn, LightGBM, XGBoost, Optuna, NumPy, pandas</dd></div>
          <div><dt>GPU and inference</dt><dd>CUDA, Triton, INT4/INT8 quantization</dd></div>
          <div><dt>Web and backend</dt><dd>Next.js, React, PostgreSQL</dd></div>
          <div><dt>Tools</dt><dd>Git, Docker, CMake, ASan, UBSan, TSan</dd></div>
        </dl>
      </div>
    </div>
  </section>

  <section class="contact wrap" id="contact" aria-labelledby="contact-title">
    <div class="section-head">
      <h2 class="section-title" id="contact-title">Contact</h2>
    </div>
    <p class="contact-lede">Have an internship, a research problem or a question about my work? Write to me.</p>
    <a class="email" href="mailto:{EMAIL}">{EMAIL}</a>
    <div class="contact-actions">
      <button class="btn" type="button" data-copy="{EMAIL}"><span class="copy-state" aria-live="polite">Copy email</span><span class="btn-icon">{COPY}</span></button>
      <a class="btn btn-ghost" href="{GITHUB}">GitHub</a>
      <a class="btn btn-ghost" href="{LINKEDIN}">LinkedIn</a>
      <a class="btn btn-ghost" href="{CODEFORCES}">Codeforces</a>
      <a class="btn btn-ghost" href="{ORCID}">ORCID</a>
      <a class="btn btn-ghost" href="{CV}" download>CV (PDF)</a>
    </div>
  </section>
</main>
""" + footer()

write("index.html", index)

for path, html in pages.build():
    write(path, html)
for path, html in notes.build_notes():
    write(path, html)

urls = ["/", "/work/sextant/", "/work/nanoserve/", "/work/legal-audio/", "/work/st-bemd/", "/work/company-hub/", "/notes/"] + [f"/notes/{n['slug']}/" for n in notes.NOTES]
sm = '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n' + "".join(f"  <url><loc>{SITE}{u}</loc><lastmod>2026-10-05</lastmod></url>\n" for u in urls) + "</urlset>\n"
open(os.path.join(OUT, "sitemap.xml"), "w").write(sm)
print("sitemap", len(urls))
