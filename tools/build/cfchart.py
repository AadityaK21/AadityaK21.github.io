"""Codeforces rating chart, built at generation time from the public API.

Data: codeforces.com/api/user.rating?handle=codeleon (fetched 5 Oct 2026).
To refresh, paste the new rows here and rebuild.
"""
import datetime as dt
from html import escape

IST = dt.timezone(dt.timedelta(hours=5, minutes=30))
HANDLE = "codeleon"
ROWS = [  # contestId, name, rank, old, new, ratingUpdateTimeSeconds
    (2241, "Codeforces Round 1107 (Div. 3)", 2013, 0, 541, 1782838200),
    (2242, "Educational Codeforces Round 192", 2289, 541, 919, 1783355700),
    (2246, "Codeforces Round 1108 (Div. 2)", 1042, 919, 1252, 1783875000),
    (2244, "Codeforces Round 1109 (Div. 3)", 1255, 1252, 1417, 1784047800),
    (2245, "Codeforces Round 1110 (Div. 1 + Div. 2)", 854, 1417, 1610, 1784222100),
    (2250, "Codeforces Round 1112 (Div. 2)", 244, 1610, 1759, 1785085500),
    (2252, "Codeforces Round 1115 (Div. 2)", 324, 1759, 1848, 1786034100),
    (2253, "Educational Codeforces Round 193", 170, 1848, 1926, 1786120500),
    (2257, "Codeforces Round 1117 (Div. 2)", 446, 1926, 1935, 1786984500),
]
YMIN, YMAX, CM = 400, 2050, 1900


def _d(ts):
    return dt.datetime.fromtimestamp(ts, IST)


def chart():
    t0 = dt.datetime(2026, 6, 27, tzinfo=IST).timestamp()
    t1 = dt.datetime(2026, 8, 21, tzinfo=IST).timestamp()
    X = lambda ts: (ts - t0) / (t1 - t0) * 100
    Y = lambda r: (1 - (r - YMIN) / (YMAX - YMIN)) * 100

    pts = [(X(r[5]), Y(r[4]), r) for r in ROWS]
    path = "M" + " L".join(f"{x * 10:.1f},{y * 10:.1f}" for x, y, _ in pts)
    grid = "".join(
        f'<line x1="0" x2="1000" y1="{Y(v) * 10:.1f}" y2="{Y(v) * 10:.1f}" class="cf-grid" vector-effect="non-scaling-stroke"/>'
        for v in (500, 1000, 1500))
    th = f'<line x1="0" x2="1000" y1="{Y(CM) * 10:.1f}" y2="{Y(CM) * 10:.1f}" class="cf-cm" vector-effect="non-scaling-stroke"/>'
    ylabels = "".join(f'<span class="cf-y" style="top:{Y(v):.2f}%">{v:,}</span>' for v in (500, 1000, 1500))

    buttons = ""
    for i, (x, y, r) in enumerate(pts):
        cid, name, rank, old, new, ts = r
        delta = new - old
        when = _d(ts).strftime("%-d %b %Y")
        tip = f"{name}\n{when}\nRank {rank:,}\n{old if old else 'Unrated'} → {new} ({'+' if delta >= 0 else ''}{delta})"
        aria = f"{name}, {when}: rank {rank}, rating {new}"
        cls = "cf-pt is-cm" if new >= CM else "cf-pt"
        buttons += (f'<button type="button" class="{cls}" style="left:{x:.2f}%;top:{y:.2f}%" '
                    f'data-tip="{escape(tip)}" aria-label="{escape(aria)}"></button>')

    first, best, last = pts[0], pts[7], pts[-1]
    labels = (
        f'<span class="cf-lab is-below" style="left:{first[0]:.2f}%;top:{first[1]:.2f}%">{first[2][4]}</span>'
        f'<span class="cf-lab is-note" style="left:{best[0]:.2f}%;top:{best[1]:.2f}%">rank 170</span>'
        f'<span class="cf-lab is-end" style="left:{last[0]:.2f}%;top:{last[1]:.2f}%">{last[2][4]}</span>'
    )
    xt = [("1 Jul", dt.datetime(2026, 7, 1, tzinfo=IST)), ("15 Jul", dt.datetime(2026, 7, 15, tzinfo=IST)),
          ("1 Aug", dt.datetime(2026, 8, 1, tzinfo=IST)), ("15 Aug", dt.datetime(2026, 8, 15, tzinfo=IST))]
    xlabels = "".join(f'<span style="left:{X(d.timestamp()):.2f}%">{l}</span>' for l, d in xt)

    rows_html = "".join(
        f"<tr><td>{_d(r[5]).strftime('%-d %b')}</td><td>{escape(r[1])}</td><td class=\"r\">{r[2]:,}</td>"
        f"<td class=\"r\">{r[4]}</td><td class=\"r\">{'+' if r[4] - r[3] >= 0 else ''}{r[4] - r[3]}</td></tr>"
        for r in ROWS)

    return f"""
    <figure class="cf" aria-labelledby="cf-title">
      <figcaption class="cf-cap"><span class="cf-title" id="cf-title">Codeforces rating</span><span class="cf-sub">From unrated to Candidate Master in 8 rated contests, June to August 2026. Hover or tap a point.</span></figcaption>
      <div class="cf-frame">
        <div class="cf-plot">
          <svg viewBox="0 0 1000 1000" preserveAspectRatio="none" aria-hidden="true" focusable="false">{grid}{th}<path d="{path}" class="cf-line" vector-effect="non-scaling-stroke"/></svg>
          {ylabels}
          <span class="cf-th" style="top:{Y(CM):.2f}%">Candidate Master, 1900</span>
          {labels}
          {buttons}
          <div class="cf-tip" role="status" hidden></div>
        </div>
        <div class="cf-x" aria-hidden="true">{xlabels}</div>
      </div>
      <details class="cf-table">
        <summary>Show as a table</summary>
        <div class="tbl"><table><thead><tr><th>Date</th><th>Contest</th><th class="r">Rank</th><th class="r">Rating</th><th class="r">Change</th></tr></thead><tbody>{rows_html}</tbody></table></div>
      </details>
    </figure>"""
