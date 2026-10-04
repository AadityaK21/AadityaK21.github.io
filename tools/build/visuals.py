"""Hand-built visuals shared by the home page rows and the case-study heroes."""

SEXTANT_TERM = """<pre class="term" aria-label="Terminal output from a Sextant run"><span class="c"># cluster, fuse, write entities with provenance</span>
<span class="p">$</span> sextant resolve
  1451 source records, 470 candidate pairs
  1187 entities written, 4201 properties,
  4201 provenance records
  dedup ratio 0.1819  (1451 records -&gt; 1187 entities)

<span class="c"># the lineage round trip</span>
<span class="p">$</span> sextant explain
lineage round trip
  1187 entities, 4201 properties
  <span class="ok">4201 verified, 0 failed  -&gt;  100.00%</span>

<span class="c"># a quarter of arrivals at Rotterdam</span>
<span class="p">$</span> sextant query --type Port --where locode=NLRTM \\
    --link arrivals --from 2026-04-01 --to 2026-07-01
  24 result(s)
  cost
    index_used           TIDX
    keys_scanned         25
    bloom_rejections     0
    elapsed_us           347</pre>"""


SEXTANT_TERM_SHORT = """<pre class="term" aria-label="Terminal output from a Sextant run"><span class="c"># cluster, fuse, write entities with provenance</span>
<span class="p">$</span> sextant resolve
  1451 source records, 470 candidate pairs
  1187 entities written, 4201 properties,
  4201 provenance records
  dedup ratio 0.1819  (1451 records -&gt; 1187 entities)

<span class="c"># the lineage round trip</span>
<span class="p">$</span> sextant explain
lineage round trip
  1187 entities, 4201 properties
  <span class="ok">4201 verified, 0 failed  -&gt;  100.00%</span></pre>"""

def bar(label, value, pct, ours=False, inside=False):
    cls = "bar-fill is-ours" if ours else "bar-fill"
    vcls = "bar-val inside" if inside else "bar-val"
    return (f'<div class="bar"><span>{label}</span><span class="bar-track" style="--w:{pct}%">'
            f'<span class="{cls}"></span><span class="{vcls}">{value}</span></span></div>')


NANOSERVE_BARS = f"""<div class="bars" role="img" aria-label="Output throughput: static batching 61.0 tokens per second, nanoserve 100.4. p99 time to first token: static batching 60.8 seconds, nanoserve 5.2 seconds.">
  <div>
    <p class="bars-h">Output throughput <span>tokens/s, higher is better</span></p>
    {bar("Static batching", "61.0", 50.6)}
    {bar("nanoserve", "100.4", 83.3, ours=True)}
  </div>
  <div>
    <p class="bars-h">p99 time to first token <span>seconds, lower is better</span></p>
    {bar("Static batching", "60.8 s", 83.3)}
    {bar("nanoserve", "5.2 s", 7.1, ours=True)}
  </div>
  <p class="bars-note">RTX 4060 Laptop (8 GB), Qwen2.5-0.5B-Instruct in fp16, 32 concurrent requests with lognormal lengths.</p>
</div>"""


NANOSERVE_SIM = """<div class="sim" data-sim role="img" aria-label="Animation: the same stream of requests served by static batching and by continuous batching with six slots each. Static batching leaves slots idle while it waits for the longest request; continuous batching refills them and finishes more requests.">
  <canvas aria-hidden="true"></canvas>
  <p class="sim-note">Same requests, six slots each. Striped slots are idle, waiting for the slowest request in the batch. This is a simulation; the measured numbers are in the case study.</p>
</div>"""


COMPANYHUB_MOCK = """<div class="mock" role="img" aria-label="Company Hub home page: the exact questions they'll ask, with companies and their difficulty mix">
  <div class="mock-bar"><i></i><i></i><i></i></div>
  <div class="mock-body">
    <div>
      <p class="mock-h">the exact <em>questions</em> they&rsquo;ll ask.</p>
      <p class="mock-stat">3,400 questions across 656 companies</p>
    </div>
    <div class="mock-list" aria-hidden="true">
      <div class="mock-co"><b>Google</b><span class="spectrum"><i style="flex:22"></i><i style="flex:55"></i><i style="flex:23"></i></span></div>
      <div class="mock-co"><b>Amazon</b><span class="spectrum"><i style="flex:28"></i><i style="flex:54"></i><i style="flex:18"></i></span></div>
      <div class="mock-co"><b>Microsoft</b><span class="spectrum"><i style="flex:30"></i><i style="flex:52"></i><i style="flex:18"></i></span></div>
    </div>
  </div>
</div>"""
