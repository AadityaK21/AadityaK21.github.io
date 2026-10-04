from common import *
from visuals import SEXTANT_TERM, NANOSERVE_BARS, COMPANYHUB_MOCK

ORDER = ["sextant", "nanoserve", "legal-audio", "st-bemd", "company-hub"]
NAMES = {"sextant": "Sextant", "nanoserve": "nanoserve", "legal-audio": "Legal audio to notes",
         "st-bemd": "ST-BEMD", "company-hub": "Company Hub"}


def meta(items):
    return '<dl class="cs-meta">' + "".join(f"<div><dt>{k}</dt><dd>{v}</dd></div>" for k, v in items) + "</dl>"


def facts(items):
    return '<dl class="cs-facts">' + "".join(f"<div><dt>{l}</dt><dd>{v}</dd></div>" for v, l in items) + "</dl>"


def section(title, body):
    return f'<section class="cs-section"><h2>{title}</h2><div class="cs-body">{body}</div></section>'


def fig(src, w, h, alt, cap):
    return (f'<figure class="cs-figure"><img src="{src}" width="{w}" height="{h}" alt="{alt}" loading="lazy" decoding="async">'
            f'<figcaption>{cap}</figcaption></figure>')


def page(slug, title_tag, desc, title, summary, meta_items, hero_html, hero_cls, sections):
    i = ORDER.index(slug)
    nxt = ORDER[(i + 1) % len(ORDER)]
    return head(title_tag, desc, f"/work/{slug}/", og=f"/assets/og/{slug}.png") + header() + f"""
<main id="main" class="wrap">
  <div class="cs-head">
    <a class="back" href="/#work">{BACK} All work</a>
    <h1 class="cs-title">{title}</h1>
    <p class="cs-summary">{summary}</p>
    {meta(meta_items)}
  </div>
  <div class="cs-hero-visual {hero_cls}">{hero_html}</div>
  {''.join(sections)}
  <a class="next" href="/work/{nxt}/"><span class="next-label">Next project</span><span class="next-title">{NAMES[nxt]}</span></a>
</main>
""" + footer()


def build():
    out = []

    # ---------------- Sextant ----------------
    out.append(("work/sextant/index.html", page(
        "sextant", "Sextant: ontology and lineage platform | Aaditya Kumawat",
        "Sextant is a C++20 mini-Foundry: ontology, entity resolution and cell-level lineage over an LSM storage engine written from scratch. Every one of 4,201 values replays from its source row.",
        "Sextant",
        "A mini-Foundry for maritime data. It maps messy records onto an ontology, merges duplicates into real entities, and can prove where every single value came from.",
        [("When", "Jun&ndash;Aug 2026"), ("What", "Self-led project"), ("Stack", "C++20, React, TypeScript, CMake"),
         ("Links", f'<a href="{GITHUB}/sextant">Code on GitHub</a>')],
        SEXTANT_TERM, "",
        [
            section("Why it exists", """
<p>A data platform is only trustworthy if you can point at any number and ask where it came from, and get an answer you can check. Most systems keep that history as a log or a comment. In Sextant it is an invariant that the system tests.</p>
<p>The data is real and messy: port and vessel records from the NGA World Port Index (CSV), UN/LOCODE (CSV) and Finland&rsquo;s Digitraffic service (REST/JSON, including AIS ship positions). The same port shows up under different names, codes and coordinates in each source.</p>
<p>The name comes from navigation. A sextant fixes your position by combining several independent observations, which is what entity resolution does.</p>
"""),
            section("What I built", """
<h3>A storage engine underneath</h3>
<p>An LSM-tree key-value store with a write-ahead log, memtable, SSTables, bloom filters, a block cache, leveled compaction and crash recovery. I chose to build it instead of linking RocksDB, and I followed LevelDB&rsquo;s design closely, so this part is a reimplementation for learning rather than a new design.</p>
<h3>Everything on top is mine</h3>
<ul>
<li><strong>Ontology.</strong> A declarative schema over twelve keyspaces, with connectors for all three sources.</li>
<li><strong>Entity resolution.</strong> Blocking, pairwise scoring, veto-constrained clustering and fusion. 1,451 records become 1,187 entities.</li>
<li><strong>Cell-level lineage.</strong> Every property stores the raw source row and the chain of transforms that produced it.</li>
<li><strong>Query planner.</strong> It returns its plan and its cost (keys scanned, blocks read, bloom rejections, microseconds) with every answer.</li>
<li><strong>Interface.</strong> An HTTP API and a React front end with a lineage drawer, a link graph and a review queue.</li>
</ul>
"""),
            section("Results", facts([
                ("100%", "of 4,201 properties across 1,187 entities replay from their source row"),
                ("0.991", "F1 resolving 1,451 records into 1,187 entities"),
                ("1.53M", "batched writes per second at 1.20&times; write amplification"),
                ("418", "tests passing on Linux, Windows and macOS, clean under ASan, UBSan and TSan"),
            ]) + """
<p><code>sextant explain</code> walks every property of every entity, fetches the raw source row it names, re-applies the transform chain and checks that the result equals the stored value. It has a negative control, because a check that cannot fail is not a check.</p>
<p>Vetoes in the clustering step lift precision from 0.973 to 1.000. A three-month window query is answered in 359 &micro;s over 25 keys, where a full scan walks 92.</p>
"""),
            section("What the numbers don&rsquo;t say", """
<p class="note">The storage figures are microbenchmarks on synthetic keys on one machine. 1.53M writes per second is one process writing batched 100-byte values into a warm page cache. With <code>sync=true</code> the same engine does about 655 writes per second, which is the fsync floor, so the batched number is not a durability figure.</p>
"""),
        ])))

    # ---------------- nanoserve ----------------
    out.append(("work/nanoserve/index.html", page(
        "nanoserve", "nanoserve: LLM inference server from scratch | Aaditya Kumawat",
        "nanoserve is an LLM inference server written from scratch: paged KV cache, continuous batching, a fused Triton attention kernel and INT4/INT8 quantization. 1.65x throughput and 12x lower p99 TTFT over static batching.",
        "nanoserve",
        "An LLM inference server written from scratch, with no vLLM or TGI underneath. Built to find out where serving time actually goes.",
        [("When", "Jun&ndash;Jul 2026"), ("What", "Self-led project"), ("Stack", "PyTorch, Triton, CUDA"),
         ("Links", f'<a href="{GITHUB}/nanoserve">Code on GitHub</a>')],
        NANOSERVE_BARS, "",
        [
            section("Why it exists", """
<p>One request through a small model is fast. Serving is where the systems work is: hundreds of requests arrive with very different prompt and output lengths, GPU memory is finite, and you are judged on the slowest 1%, not the average.</p>
<p>Three things dominate. Memory is the constraint, not compute. The batch must never go stale, because a static batch of 32 spends most of its life as a batch of one while it waits for the longest sequence. And smaller weights buy more room for concurrent requests.</p>
"""),
            section("What I built", """
<ul>
<li><strong>Paged KV cache.</strong> A block allocator and per-sequence block tables, so wasted memory is bounded to less than one block per sequence.</li>
<li><strong>Continuous batching.</strong> A scheduler that re-decides the batch every step, with a token budget, chunked prefill and preemption by recompute.</li>
<li><strong>My own forward pass</strong> for Qwen2 against the paged cache. <code>transformers</code> supplies only the tokenizer and the raw weights.</li>
<li><strong>A fused Triton kernel</strong> for paged-attention decode, using online softmax over the block table.</li>
<li><strong>Weight-only quantization.</strong> INT8 per channel and group-wise INT4. INT4 hands about 700 MiB back to the KV cache.</li>
<li><strong>A benchmark harness</strong> with realistic lognormal traffic. vLLM runs the identical workload in a separate environment as an outside yardstick.</li>
</ul>
<p>The scheduler and block manager import no torch, so the bookkeeping bugs that hurt most in a serving engine are caught in fast CPU unit tests. The project has 92 tests.</p>
"""),
            section("Results", facts([
                ("1.65&times;", "output throughput over the best static batching (61.0 to 100.4 tokens/s)"),
                ("12&times;", "lower p99 time to first token (60.8 s to 5.2 s)"),
                ("2.1&ndash;12.5&times;", "speed-up of the Triton kernel over gather + SDPA, depending on batch and context"),
                ("~80%", "of decode time is launch overhead on this GPU, measured with a roofline probe"),
            ]) + fig("/assets/img/nanoserve-throughput.webp", 1540, 588,
                     "Two charts of output tokens per second against batch size. Static batching rises with batch size but stays well below the continuous batching line in both the skewed and uniform workloads.",
                     "Continuous batching against static batching at batch sizes 1 to 16. The gap is widest on skewed lengths, which is what real traffic looks like.")
              + fig("/assets/img/nanoserve-kernel.webp", 1540, 588,
                    "Left: attention time against context length for torch and Triton backends at batch 1, 8 and 32. Right: Triton speed-up against context length, falling from about 12 times at short context to about 2 to 4 times at 4096 tokens.",
                    "The kernel&rsquo;s speed-up shrinks with context at batch 1. That contradicted my prediction, and the raw timings explain why: at small batch the torch path is bound by kernel launches, not by memory traffic.")
              + """
<p>p99 end-to-end latency fell from 110.8 s to 65.4 s. The finding that decode is mostly launch-overhead bound, not memory-bandwidth bound, inverts the usual advice and drove the optimisations that followed.</p>
"""),
            section("What the numbers don&rsquo;t say", """
<p class="note">Everything is measured on one laptop GPU (RTX 4060, 8 GB) with one small model (Qwen2.5-0.5B-Instruct, fp16). The first four attempts at one measurement gave wrong but plausible numbers, from GPU clock ramp-up to double-counted kernels. The report keeps those bugs and their fixes on record.</p>
<p>Against vLLM in its strongest configuration on the same GPU, nanoserve reaches 0.32&times; of its throughput. Most of that gap is launch overhead that CUDA graphs would remove. The full story of finding that bottleneck is in the note <a class="text-link" href="/notes/gpu-waiting-not-working/">My GPU was waiting, not working</a>.</p>
"""),
        ])))

    # ---------------- Legal audio ----------------
    out.append(("work/legal-audio/index.html", page(
        "legal-audio", "Legal audio to notes: research at HEC Lausanne | Aaditya Kumawat",
        "A fully local pipeline that turns legal audio into speaker-attributed, citation-backed notes, built during a research internship at the Applied AI Laboratory, HEC Lausanne. 6.9% WER and 7.9% DER on Supreme Court audio.",
        "Legal audio",
        "A fully local pipeline that turns court audio into speaker-attributed notes, where every line links back to the moment it was said. Nothing leaves the machine.",
        [("When", "May&ndash;Jul 2026"), ("Role", "Research intern (remote)"), ("Where", "Applied AI Laboratory, HEC Lausanne"),
         ("Stack", "Python, Whisper, pyannote, local LLMs")],
        '<img src="/assets/img/legal-audio-app.webp" width="2000" height="1205" alt="The app in demo mode: note modes on the left, verbatim notes with speaker and timestamp citations in the middle, and the transcript on the right with the cited line highlighted.">', "",
        [
            section("Why it exists", """
<p>Recordings of legal proceedings are often privileged, so sending them to a cloud API is not an option. And a note about what a court said is only useful if it is easy to check against the record.</p>
<p>Most local meeting-notes tools feed a Whisper transcript to a language model and inherit every hallucination the model makes. For a document someone may rely on as an account of a hearing, that is the whole problem.</p>
"""),
            section("What I built", """
<ul>
<li><strong>A local pipeline.</strong> Whisper large-v3-turbo for speech recognition, pyannote for speaker diarization, and a 4-bit quantized language model, all on a consumer 8 GB GPU.</li>
<li><strong>Notes that cannot be made up.</strong> In model-selected extractive mode the LLM reads a numbered transcript and may only return integer sentence ids, enforced by a grammar constraint at decode time. The note text is then copied from the transcript by id, so it is byte-for-byte the record.</li>
<li><strong>Confidentiality you can verify.</strong> A run marked privileged refuses any non-loopback endpoint before inference starts, and every run writes a manifest of hashes and endpoints that can be re-checked later.</li>
<li><strong>A one-click check.</strong> In the app, every note is a button. Click it and the transcript scrolls to the source sentence and the audio seeks to that moment.</li>
</ul>
"""),
            section("Results", facts([
                ("6.9%", "word error rate on 62 minutes of gold Supreme Court audio (Oyez)"),
                ("7.9%", "diarization error rate on the same audio"),
                ("100%", "verbatim rate in the extractive mode, verified"),
                ("3.0&times;", "how much more often legally important words are misheard than average words"),
            ]) + """
<p>The evaluation harness covers WER, DER, a checklist-style LLM judge in the spirit of CheckEval, and planted prompt-injection tests against that judge.</p>
<p>I also built a speaker-label bias probe. It re-runs note selection on transcripts whose words are identical but whose speaker labels are anonymised or shuffled, and compares the result against a resampling noise floor. Relabelling alone shifted one speaker&rsquo;s share of the notes by 40.4 points, a failure that WER, DER and verbatim rate cannot see.</p>
"""),
            section("What the numbers don&rsquo;t say", """
<p class="note">Supreme Court oral argument is a floor, not a typical case: the recordings are unusually clean and the speakers unusually clear. Depositions and trial-court audio will be harder. The code is private.</p>
"""),
        ])))

    # ---------------- ST-BEMD ----------------
    out.append(("work/st-bemd/index.html", page(
        "st-bemd", "ST-BEMD: direction-adaptive 2-D EMD | Aaditya Kumawat",
        "ST-BEMD is a structure-tensor-guided empirical mode decomposition for 2-D signals. On 100 real fingerprints it cuts orientation error by 35.7% against isotropic BEMD.",
        "ST-BEMD",
        "A way to split 2-D signals such as fingerprints into their component layers, by bending the method along the ridges instead of treating every direction the same.",
        [("When", "May&ndash;Jul 2026"), ("What", "Self-led project"), ("Stack", "Python, NumPy, SciPy"),
         ("Links", f'<a href="{GITHUB}/stbemd-signal-processing">Code on GitHub</a>')],
        '<img src="/assets/img/stbemd-orientation.webp" width="1430" height="468" alt="A real fingerprint from SOCOFing, its ridge orientation map and its structure-tensor coherence map.">', "is-figure",
        [
            section("Why it exists", """
<p>Empirical mode decomposition splits a signal into layers, from the finest detail to the slowest trend. The 2-D version builds its upper and lower envelopes by interpolating between local maxima and minima the same way in every direction.</p>
<p>On a signal with strong direction, like a fingerprint, that is wrong. The envelope averages peaks from neighbouring ridges, so orientation bleeds across them.</p>
"""),
            section("What I built", """
<ol>
<li>Compute the structure tensor, which gives the local orientation and how strongly the image is oriented there (coherence).</li>
<li>At each pixel, build an elliptical kernel stretched along the ridge. The stretch grows with coherence.</li>
<li>Take the envelope as a kernel-weighted average of nearby extrema.</li>
</ol>
<p>Where coherence is zero the kernel becomes a circle, so the method falls back to ordinary 2-D EMD exactly where orientation is undefined.</p>
<p>The original formulation, taken literally, stretches the kernel across the ridge instead of along it, which makes things worse. Getting that geometry right is the difference between 39.3&deg; and 8.3&deg; of orientation error on a real print.</p>
<p>I wrote all four baselines from scratch: BEMD with a global RBF, Pseudo-BEMD, Serial-EMD and DEMD.</p>
"""),
            section("Results", facts([
                ("3.3&deg;", "better than the baseline at 5 dB noise, against the clean print, on two independent instruments"),
                ("35.7%", "lower self-referenced orientation error on 100 SOCOFing prints (12.87&deg; to 8.27&deg;); see the caveat below"),
                ("40.6%", "lower mean error on synthetic signals (3.08&deg; to 1.83&deg;)"),
                ("78%", "of the clean-data gain comes from the local envelope, not the anisotropy"),
            ]) + fig("/assets/img/stbemd-fingerprints.webp", 1420, 666,
                     "Left: orientation error for 30 prints, each with a blue isotropic point and an orange ST-BEMD point; every orange point is to the left. Right: error by ridge curvature, where both methods get worse but ST-BEMD stays lower.",
                     "Every one of 30 paired prints improves. Both methods get worse as ridges curve, and the gap holds across the range.")
              + """
<p>The local envelope is also faster, because it sums over a small window instead of solving a dense system over all extrema. How much faster depends heavily on the machine and the signal, so I don&rsquo;t quote one multiplier.</p>
"""),
            section("What the numbers don&rsquo;t say", """
<p class="note">The method changes two things at once, so I ran an ablation to separate them. About 78% of the gain comes from switching to a local averaged envelope, which is an existing idea, not from the anisotropy the method is named after. The anisotropy still helps on its own (better on 70% of prints, p = 0.001), but the effect is small, and it shrinks on highly curved ridges.</p>
<p class="note">The orientation metric itself has a bigger problem. It compares each extracted layer with its own input, so returning the input unchanged scores a perfect 0&deg; and subtracting a Gaussian blur scores 4.23&deg;, better than ST-BEMD. Read the 35.7% as &ldquo;disturbs the orientation field less than the baseline&rdquo;, not &ldquo;recovers orientation better&rdquo;. In a test that takes the reference from the clean print and feeds the methods a noisy one, ST-BEMD is 3.3&deg; ahead of the baseline at heavy noise (5 dB) and slightly behind at light noise.</p>
<p>I wrote up how I found this in the note <a class="text-link" href="/notes/gaussian-blur-beat-my-method/">A Gaussian blur beat my method</a>.</p>
"""),
        ])))

    # ---------------- Company Hub ----------------
    out.append(("work/company-hub/index.html", page(
        "company-hub", "Company Hub: interview prep platform | Aaditya Kumawat",
        "Company Hub is a live interview-prep platform at companyhub.fun that ranks 3,400 LeetCode questions across 656 companies by how often each company asks them.",
        "Company Hub",
        "A live interview-prep site that ranks LeetCode questions by how often each company actually asks them.",
        [("When", "Jun 2026 to now"), ("What", "Live product, built and run alone"), ("Stack", "Next.js 15, TypeScript, PostgreSQL, Prisma"),
         ("Links", '<a href="https://companyhub.fun">companyhub.fun</a><br><a href="' + GITHUB + '/leetcode-company-hub">Code on GitHub</a>')],
        COMPANYHUB_MOCK, "",
        [
            section("Why it exists", """
<p>When you prepare for a specific company, the useful question is what that company actually asks and how recently. Company Hub organises practice around that: every company has its own list of questions ranked by frequency, with filters for how recent the data is.</p>
<p>The question data comes from the open-source <a class="text-link" href="https://github.com/snehasishroy/leetcode-companywise-interview-questions">leetcode-companywise-interview-questions</a> dataset.</p>
"""),
            section("What I built", """
<ul>
<li><strong>Company explorer and problem bank.</strong> 3,400 questions across 656 companies, with difficulty mix, topic breakdowns and frequency per company.</li>
<li><strong>Accounts.</strong> Auth.js v5 with Google sign-in and TOTP two-factor authentication.</li>
<li><strong>Practice tools.</strong> LeetCode progress sync, graded spaced repetition, study sheets and a Monaco code editor that works in 9 languages.</li>
<li><strong>Data model.</strong> 21 Prisma models on PostgreSQL.</li>
</ul>
"""),
            section("Running it in production", """
<p>The interesting problems only appeared once real people used it.</p>
<ul>
<li><strong>Connection pool exhaustion.</strong> Serverless functions opened more database connections than PostgreSQL allowed. Moving to a transaction-mode pooler fixed it.</li>
<li><strong>Foreign-key violations (P2003).</strong> Stale sign-in tokens referred to user records that no longer existed, so writes failed. I traced the cause and fixed it.</li>
<li><strong>Abuse.</strong> Rate limiting and account lockout on sign-in.</li>
</ul>
"""),
        ])))

    # ---------------- 404 ----------------
    out.append(("404.html", head("Page not found | Aaditya Kumawat", "This page does not exist.", "/404.html") + header() + f"""
<main id="main" class="wrap lost">
  <h1>404</h1>
  <p class="cs-summary">This page doesn&rsquo;t exist. It may have moved when the site was rebuilt.</p>
  <p><a class="btn" href="/">Go to the home page<span class="btn-icon">{ARROW}</span></a></p>
</main>
""" + footer()))

    return out
