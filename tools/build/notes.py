"""Notes: short write-ups drawn from the project reports."""
import re
from common import *

NOTES = [
    {
        "slug": "gpu-waiting-not-working",
        "title": "My GPU was waiting, not working",
        "dek": "Why LLM decode on my RTX 4060 is limited by kernel launches, not memory bandwidth, and what I changed once I knew.",
        "date": "5 October 2026",
        "iso": "2026-10-05",
        "project": ("nanoserve", "/work/nanoserve/"),
    },
    {
        "slug": "gaussian-blur-beat-my-method",
        "title": "A Gaussian blur beat my method",
        "dek": "What happened when I tested the metric instead of the method, on my direction-adaptive EMD for fingerprints.",
        "date": "5 October 2026",
        "iso": "2026-10-05",
        "project": ("ST-BEMD", "/work/st-bemd/"),
    },
]


def table(head, rows, num_from=1):
    h = "".join(f"<th{' class=\"r\"' if i >= num_from else ''}>{c}</th>" for i, c in enumerate(head))
    b = ""
    for r in rows:
        b += "<tr>" + "".join(f"<td{' class=\"r\"' if i >= num_from else ''}>{c}</td>" for i, c in enumerate(r)) + "</tr>"
    return f'<div class="tbl"><table><thead><tr>{h}</tr></thead><tbody>{b}</tbody></table></div>'


def fig(src, w, h, alt, cap):
    return (f'<figure class="cs-figure"><img src="{src}" width="{w}" height="{h}" alt="{alt}" loading="lazy" decoding="async">'
            f'<figcaption>{cap}</figcaption></figure>')


ANATOMY = """<div class="anatomy" role="img" aria-label="Share of each batch-1 decode step the GPU spent computing: 18 percent on Windows, 22 percent on WSL2. The rest was spent waiting for the next kernel launch.">
  <div class="an-row"><span class="an-label">Windows 11</span><span class="an-track"><span class="an-busy" style="width:18%"></span></span><span class="an-val">18% busy</span></div>
  <div class="an-row"><span class="an-label">WSL2 Ubuntu</span><span class="an-track"><span class="an-busy" style="width:22%"></span></span><span class="an-val">22% busy</span></div>
  <p class="an-key"><i class="k-busy"></i>GPU computing <i class="k-idle"></i>GPU idle, waiting for the CPU to launch the next kernel</p>
</div>"""


GPU_BODY = f"""
<p class="lead">The standard advice about LLM inference is that decoding is limited by memory bandwidth. Every new token means reading all of the model&rsquo;s weights from GPU memory, so the speed limit is how fast you can stream bytes. I built nanoserve, an inference server written from scratch, expecting to optimise for exactly that. The first careful measurement said I was optimising the wrong thing.</p>

<h2>The number that didn&rsquo;t fit</h2>
<p>Qwen2.5-0.5B in fp16 is 943 MiB of weights, and my laptop&rsquo;s RTX 4060 sustains about 210 to 226 GB/s on a plain memory copy. If memory were the limit, one decode step at batch size 1 should take about 4.5 ms.</p>
{table(["Measure", "Windows 11", "WSL2 Ubuntu"], [
    ["Memory-bandwidth floor per step", "~4.5 ms", "~4.5 ms"],
    ["Actual batch-1 step (eager transformers)", "23.7 ms", "16.6 ms"],
    ["Cost of launching one small kernel", "7.8&ndash;15 &micro;s", "6.8&ndash;9.2 &micro;s"],
    ["GPU utilisation during decode", "<strong>18%</strong>", "<strong>22%</strong>"],
])}
<p>The step was four to five times slower than the bandwidth floor. Profiling showed why: the GPU was busy for only about a fifth of each step. The rest of the time it sat idle while the CPU issued the next of roughly 1,000 to 1,350 small kernels.</p>
{ANATOMY}

<h2>The tell: batching was almost free</h2>
<p>If most of each step is a fixed launch cost, a bigger batch should cost almost nothing extra. That is exactly what happened. Step time went from 28 ms at batch 1 to 34 ms at batch 32, so throughput went from 35.5 to 941.8 tokens per second: a 26&times; gain for 20% more time per step.</p>

<h2>I blamed Windows first, and I was wrong</h2>
<p>My first theory was the Windows display driver model (WDDM), which routes kernel launches through the operating system&rsquo;s scheduler. I predicted Linux would be much faster. The measurements didn&rsquo;t back that up:</p>
<ul>
<li>Two consecutive runs of the same Linux setup measured the small-kernel cost at 6.8 &micro;s and 9.2 &micro;s. That 35% spread overlaps the Windows range.</li>
<li>The two setups also ran different PyTorch builds, which changed the number of device ops per step from 1,350 to 1,014 for identical model code. That is a library difference, not an OS one.</li>
<li>Utilisation was 18% against 22%. Both were overhead-bound.</li>
</ul>
<p class="pull">On this hardware, the number of kernels is what moves decode time. The operating system is not.</p>

<h2>What I changed because of it</h2>
<p>Once the bottleneck was clear, every change that paid off was one that cut the number of ops per step:</p>
{table(["Change", "Why it mattered here"], [
    ["RoPE cos/sin computed once per step", "Positions are the same in all 24 layers; the old code built 48 identical tensors per step"],
    ["Fused RMSNorm", "Replaced an 8-kernel hand-written norm used at 48 places per step"],
    ["Grouped-query attention inside SDPA", "Stopped materialising a 7&times; expanded copy of K and V"],
    ["One pinned host-to-device copy for step metadata", "Was six separate small transfers per step"],
], num_from=99)}
<p>Together with a faster way of mapping tokens to cache slots, these took the batch-1 step from 33.7 ms to 28.2 ms, 16% faster.</p>
<p>Then the fused Triton paged-attention kernel replaced about ten ops per layer with one. Device ops per step fell from 1,014 to 682, GPU utilisation at batch 32 rose from 23% to 36%, and nanoserve clearly beat eager transformers for the first time: 1.23&times; at batch 8.</p>
{fig("/assets/img/nanoserve-kernel.webp", 1540, 588,
     "Left: attention time against context length for the torch and Triton backends. Right: the Triton kernel's speed-up, falling from about 12 times at short context to about 2 to 4 times at 4096 tokens.",
     "The kernel&rsquo;s speed-up shrinks as context grows, which surprised me. At batch 1 the torch path takes about the same time at every context length, because it is paying for ten kernel launches, not for the data.")}

<h2>Four measurements that lied first</h2>
<p>Before any of these numbers could be trusted, four bugs in the measurement itself had to go. Each one produced a plausible-looking wrong answer.</p>
<ul>
<li><strong>Clock ramp.</strong> The GPU idles at 210 MHz and boosts to 2,595 MHz. Whatever ran first was measured cold, which once produced &ldquo;batch 32 is faster than batch 1&rdquo; and a fake 3.4&times; win. Now there are 8 seconds of sustained work before measuring, repeated before every row.</li>
<li><strong>Double-counted kernels.</strong> The profiler attributes time to both an op and its kernel. Summing both reported 166% GPU utilisation.</li>
<li><strong>Mismatched runs.</strong> Busy time from a profiled run was being divided by wall time from an unprofiled one.</li>
<li><strong>Noise.</strong> Every configuration is now timed twice and flagged if the runs disagree by more than 15%.</li>
</ul>

<h2>Where this leaves nanoserve</h2>
<p>Against vLLM in its strongest setup (torch.compile plus CUDA graphs), on the same GPU and the same requests, the honest comparison is:</p>
{table(["Server", "Output tokens/s", "vs vLLM"], [
    ["vLLM, compiled with CUDA graphs", "2,103.5", "1.00&times;"],
    ["nanoserve, continuous batching + Triton", "663.0", "0.32&times;"],
    ["Static batching, best batch size", "236.9", "0.11&times;"],
])}
<p>The biggest part of that gap is the same story. vLLM captures its decode step as CUDA graphs once and replays them, while nanoserve re-issues around 680 kernels every step from Python. So the next change is CUDA graphs for decode. The shapes are static, so the step can be captured once and replayed. That attacks the time spent waiting, which is still most of each step, instead of the time spent working.</p>

<h2>The takeaway</h2>
<p>Measure the shape of the bottleneck on your own hardware before optimising for it. &ldquo;Decode is memory-bound&rdquo; may well hold for a large model on a datacenter GPU. For a 0.5B model on a laptop GPU, the real step took four to five times longer than the memory floor, and the gap was all launch overhead.</p>
"""


BLUR_BODY = f"""
<p class="lead">ST-BEMD is a 2-D empirical mode decomposition I built this summer. It bends its envelopes along the local ridge direction, so on fingerprints it should keep each ridge&rsquo;s orientation intact better than the standard, direction-blind version. On 30 real prints, orientation error dropped from 13.71&deg; to 8.25&deg;, and every single print improved. This note is about why that number does not mean what it looks like it means.</p>

<h2>Two changes, one name</h2>
<p>Compared with the 2003 baseline, ST-BEMD changes two things at once. The envelope goes from a global RBF interpolation to a local weighted average, and the averaging kernel goes from a circle to an ellipse stretched along the ridges. The method is named after the second change, so I ran a version with only the first one: the same local averaging, but with a circular kernel.</p>
{table(["Version", "Orientation error (30 prints)", "Step"], [
    ["Baseline: global RBF, circular", "13.71&deg;", ""],
    ["Local average, circular kernel", "9.43&deg;", "&minus;4.29&deg; from the envelope"],
    ["ST-BEMD: local average, elliptical kernel", "8.25&deg;", "&minus;1.18&deg; from the anisotropy"],
])}
<p>About 78% of the improvement comes from the local envelope, which is an existing idea, not from the anisotropy the method is named after. The anisotropy&rsquo;s own effect is real (better on 70% of prints, p = 0.001), but small. Worse, it shrinks as ridges curve: +1.42&deg;, +1.13&deg; and +0.20&deg; from low to high curvature. The whole premise of the method predicts the opposite.</p>

<h2>Then I tested the metric</h2>
<p>The orientation error compares the orientation field of the extracted layer with the orientation field of the input. That made me wonder how estimators that know nothing about orientation would score.</p>
{table(["Estimator", "Orientation error"], [
    ["Return the input unchanged", "<strong>0.00&deg;</strong>"],
    ["Subtract a Gaussian blur (&sigma; = 4)", "<strong>4.23&deg;</strong>"],
    ["Subtract a Gaussian blur (&sigma; = 1)", "7.26&deg;"],
    ["ST-BEMD", "8.25&deg;"],
    ["Local average, circular kernel", "9.43&deg;"],
    ["Baseline", "13.71&deg;"],
])}
<p>Doing nothing scores a perfect zero. Subtracting a blurred copy of the image scores about twice as well as my method. The metric&rsquo;s best possible answer is to leave the input alone.</p>

<h2>What the metric was really measuring</h2>
<p>To check this properly, I picked the blur width on half the prints and scored on the other half, so the control couldn&rsquo;t be tuned to the test set. I also added a second measure, IMF validity: how close the extracted layer is to having zero local mean, which is the thing sifting is supposed to achieve. Lower is better.</p>
{table(["Held out, 15 prints", "Orientation error", "IMF validity"], [
    ["Baseline", "15.91&deg;", "<strong>0.131</strong>"],
    ["Local average, circular kernel", "10.08&deg;", "0.210"],
    ["ST-BEMD", "9.34&deg;", "0.185"],
    ["Gaussian blur control", "<strong>4.86&deg;</strong>", "0.383"],
])}
<p>Across all ten estimators the two measures are anti-correlated at r = &minus;0.94. Scoring well on orientation means having sifted less.</p>
{fig("/assets/img/stbemd-metric-tradeoff.webp", 1056, 718,
     "Scatter of orientation error against IMF validity. The Gaussian blur controls sit top left: low orientation error but poor validity. The baseline sits bottom right. ST-BEMD and the circular local version are in between.",
     "The two measures pull against each other. The blur buys its orientation score by not doing the job.")}
<p class="pull">The orientation metric was largely measuring how little each estimator sifted.</p>
<p>So the 13.71&deg; to 8.25&deg; result supports a narrower claim: ST-BEMD&rsquo;s envelope disturbs the orientation field less than a global interpolant does. It does not show that it recovers orientation better. One small point does survive cleanly: against the circular local version, ST-BEMD is better on both measures (9.34&deg; vs 10.08&deg;, and 0.185 vs 0.210). Same machinery, only the kernel shape differs.</p>

<h2>A test that doing nothing can&rsquo;t win as easily</h2>
<p>To break the circularity, I took the reference orientation from the clean print and gave every method a noisy copy, so preserving the input is no longer enough. I also measured orientation with two unrelated instruments, a bank of Gabor filters and the structure tensor, so the method couldn&rsquo;t be graded by the same tool it steers by.</p>
{table(["Noise level", "Baseline", "ST-BEMD", "ST-BEMD ahead by"], [
    ["20 dB (light)", "10.04&deg;", "10.97&deg;", "&minus;0.93&deg;"],
    ["10 dB", "12.87&deg;", "12.57&deg;", "+0.30&deg;"],
    ["5 dB (heavy)", "18.33&deg;", "15.06&deg;", "<strong>+3.27&deg;</strong>"],
])}
{fig("/assets/img/stbemd-noise-test.webp", 978, 640,
     "Orientation error against the clean print as noise increases from 20 dB to 5 dB. ST-BEMD grows more slowly than the baseline and ends at 15.1 degrees against 18.3. The do-nothing line stays lowest throughout.",
     "With the reference taken from the clean print, ST-BEMD degrades more gracefully than the baseline as noise rises. Doing nothing is still the lowest line.")}
<p>With light noise ST-BEMD is slightly worse. With heavy noise it is ahead by 3.3&deg; (3.6&deg; with the second instrument), and both instruments agree on the ranking. That is the claim I can defend: <strong>direction-adaptive local envelopes are more robust to noise than global RBF interpolation.</strong></p>
<p>It is still not a clean win. Doing nothing remains the lowest-error entry, and the blur still beats every EMD method on orientation. This protocol is necessary, not sufficient.</p>

<h2>What I&rsquo;d tell myself in May</h2>
<p>Build the control before the method. If a metric gives its best score to an estimator that does nothing, it cannot reward an estimator for doing something. I only found this because I tried to beat my own number with something deliberately dumb, and it won.</p>
"""


BODIES = {"gpu-waiting-not-working": GPU_BODY, "gaussian-blur-beat-my-method": BLUR_BODY}


def reading_time(html):
    words = len(re.sub(r"<[^>]+>", " ", html).split())
    return max(1, round(words / 220))


def note_page(n, i):
    body = BODIES[n["slug"]]
    other = NOTES[(i + 1) % len(NOTES)]
    proj_name, proj_url = n["project"]
    ld = ('<script type="application/ld+json">{"@context":"https://schema.org","@type":"BlogPosting",'
          f'"headline":"{n["title"]}","description":"{n["dek"]}","datePublished":"{n["iso"]}",'
          f'"author":{{"@type":"Person","name":"Aaditya Kumawat","url":"{SITE}/"}},'
          f'"mainEntityOfPage":"{SITE}/notes/{n["slug"]}/"}}</script>\n')
    return head(f'{n["title"]} | Aaditya Kumawat', n["dek"], f'/notes/{n["slug"]}/', extra=ld, og=f'/assets/og/{n["slug"]}.png') + header() + f"""
<main id="main" class="wrap">
  <div class="cs-head">
    <a class="back" href="/notes/">{BACK} All notes</a>
    <h1 class="art-title">{n["title"]}</h1>
    <p class="cs-summary">{n["dek"]}</p>
  </div>
  <div class="art">
    <aside class="art-aside">
      <dl>
        <div><dt>Published</dt><dd><time datetime="{n["iso"]}">{n["date"]}</time></dd></div>
        <div><dt>Reading time</dt><dd>{reading_time(body)} min</dd></div>
        <div><dt>Project</dt><dd><a class="text-link" href="{proj_url}">{proj_name}</a></dd></div>
      </dl>
    </aside>
    <article class="art-body">
{body}
    </article>
  </div>
  <a class="next" href="/notes/{other["slug"]}/"><span class="next-label">Next note</span><span class="next-title">{other["title"]}</span></a>
</main>
""" + footer()


def notes_list_html(level=3):
    out = '<div class="list">'
    for n in NOTES:
        out += f"""
      <article class="item">
        <h{level} class="item-title"><a href="/notes/{n["slug"]}/">{n["title"]}</a></h{level}>
        <p class="item-text">{n["dek"]}<span class="by">From <a class="text-link" href="{n["project"][1]}">{n["project"][0]}</a></span></p>
        <p class="item-side"><span><time datetime="{n["iso"]}">{n["date"]}</time></span><span>{reading_time(BODIES[n["slug"]])} min read</span></p>
      </article>"""
    return out + "\n    </div>"


def notes_index():
    return head("Notes | Aaditya Kumawat", "Short write-ups by Aaditya Kumawat on what his projects measured, including the parts that didn't go to plan.", "/notes/") + header() + f"""
<main id="main" class="wrap">
  <div class="cs-head">
    <a class="back" href="/">{BACK} Home</a>
    <h1 class="cs-title">Notes</h1>
    <p class="cs-summary">Short write-ups on what my projects measured, including the parts that didn&rsquo;t go to plan.</p>
    <p class="feed-link"><a class="text-link" href="/notes/feed.xml">Subscribe with RSS</a></p>
  </div>
  <div class="notes-index">
    {notes_list_html(level=2)}
  </div>
</main>
""" + footer()


def build_notes():
    out = [("notes/index.html", notes_index()), ("notes/feed.xml", atom_feed())]
    for i, n in enumerate(NOTES):
        out.append((f'notes/{n["slug"]}/index.html', note_page(n, i)))
    return out


def atom_feed():
    from html import escape
    entries = ""
    for n in NOTES:
        url = f"{SITE}/notes/{n['slug']}/"
        entries += f"""  <entry>
    <title>{escape(n['title'])}</title>
    <link href="{url}"/>
    <id>{url}</id>
    <updated>{n['iso']}T00:00:00+05:30</updated>
    <summary>{escape(n['dek'])}</summary>
    <content type="html">{escape(BODIES[n['slug']])}</content>
  </entry>
"""
    latest = max(n["iso"] for n in NOTES)
    return f"""<?xml version="1.0" encoding="utf-8"?>
<feed xmlns="http://www.w3.org/2005/Atom">
  <title>Notes by Aaditya Kumawat</title>
  <subtitle>Short write-ups on what my projects measured.</subtitle>
  <link href="{SITE}/notes/feed.xml" rel="self"/>
  <link href="{SITE}/notes/"/>
  <id>{SITE}/notes/</id>
  <updated>{latest}T00:00:00+05:30</updated>
  <author><name>Aaditya Kumawat</name><uri>{SITE}/</uri></author>
{entries}</feed>
"""
