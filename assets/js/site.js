/* aadityakumawat.me: small, dependency-free behaviour. */
(function () {
  "use strict";

  var root = document.documentElement;
  root.classList.add("js");
  var reduceMotion = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
  var canHover = window.matchMedia("(hover: hover) and (pointer: fine)").matches;

  /* ---- Theme colours, read from the CSS tokens so canvases follow the theme ---- */
  var hexToRgb = function (hex) {
    hex = (hex || "").trim().replace("#", "");
    if (hex.length === 3) hex = hex.split("").map(function (c) { return c + c; }).join("");
    var n = parseInt(hex, 16);
    if (isNaN(n)) return [0, 0, 0];
    return [(n >> 16) & 255, (n >> 8) & 255, n & 255];
  };
  var palette = {};
  var readPalette = function () {
    var cs = getComputedStyle(root);
    ["ink", "ink-2", "mute", "rule", "card", "paper", "paper-2", "signal", "bar-muted"].forEach(function (k) {
      palette[k] = cs.getPropertyValue("--" + k).trim();
    });
  };
  readPalette();

  /* ---- Light / dark switch ---- */
  var toggles = document.querySelectorAll("[data-theme-toggle]");
  var themeMeta = document.querySelector('meta[name="theme-color"]');
  var syncToggle = function () {
    var dark = root.getAttribute("data-theme") === "dark";
    toggles.forEach(function (b) {
      b.setAttribute("aria-pressed", dark ? "true" : "false");
      b.setAttribute("aria-label", dark ? "Switch to light mode" : "Switch to dark mode");
    });
    if (themeMeta) themeMeta.setAttribute("content", dark ? "#000000" : "#f1f1ef");
  };
  syncToggle();
  toggles.forEach(function (b) {
    b.addEventListener("click", function () {
      var dark = root.getAttribute("data-theme") !== "dark";
      if (dark) root.setAttribute("data-theme", "dark"); else root.removeAttribute("data-theme");
      try { localStorage.setItem("theme", dark ? "dark" : "light"); } catch (e) {}
      readPalette();
      syncToggle();
      window.dispatchEvent(new Event("themechange"));
    });
  });

  /* ---- Local time in New Delhi ---- */
  var clockEls = document.querySelectorAll("[data-clock]");
  var dateEls = document.querySelectorAll("[data-date]");
  if (clockEls.length || dateEls.length) {
    var tFmt = new Intl.DateTimeFormat("en-GB", { timeZone: "Asia/Kolkata", hour: "2-digit", minute: "2-digit", second: "2-digit", hour12: false });
    var tShort = new Intl.DateTimeFormat("en-GB", { timeZone: "Asia/Kolkata", hour: "2-digit", minute: "2-digit", hour12: false });
    var dFmt = new Intl.DateTimeFormat("en-GB", { timeZone: "Asia/Kolkata", weekday: "long", day: "numeric", month: "long" });
    var tick = function () {
      var now = new Date();
      clockEls.forEach(function (el) {
        el.textContent = (el.hasAttribute("data-short") ? tShort : tFmt).format(now) + " IST";
      });
      dateEls.forEach(function (el) { el.textContent = dFmt.format(now); });
    };
    tick();
    setInterval(tick, 1000);
  }

  /* ---- Footer year ---- */
  document.querySelectorAll("[data-year]").forEach(function (el) { el.textContent = new Date().getFullYear(); });

  /* ---- Last public push on GitHub ---- */
  var pushEl = document.querySelector("[data-lastpush]");
  if (pushEl && window.fetch) {
    var user = pushEl.getAttribute("data-lastpush");
    var KEY = "lastpush:" + user;
    var rtf = window.Intl && Intl.RelativeTimeFormat ? new Intl.RelativeTimeFormat("en", { numeric: "auto" }) : null;
    var ago = function (iso) {
      var s = (new Date(iso).getTime() - Date.now()) / 1000;
      var units = [["year", 31536000], ["month", 2592000], ["week", 604800], ["day", 86400], ["hour", 3600], ["minute", 60]];
      for (var i = 0; i < units.length; i++) {
        if (Math.abs(s) >= units[i][1] || units[i][0] === "minute") {
          var v = Math.round(s / units[i][1]);
          if (units[i][0] === "minute" && v === 0) return "just now";
          return rtf ? rtf.format(v, units[i][0]) : Math.abs(v) + " " + units[i][0] + "s ago";
        }
      }
    };
    var show = function (d) {
      if (!d) return;
      var a = pushEl.querySelector("a");
      var t = pushEl.querySelector("[data-ago]");
      a.textContent = d.repo;
      a.href = "https://github.com/" + user + "/" + d.repo;
      var paint = function () { t.textContent = ago(d.at); };
      paint();
      setInterval(paint, 60000);
      pushEl.hidden = false;
    };
    var cached = null;
    try { cached = JSON.parse(sessionStorage.getItem(KEY) || "null"); } catch (e) {}
    if (cached && Date.now() - cached.t < 10 * 60 * 1000) {
      show(cached.d);
    } else {
      // Public repos sorted by last push; the site's own repo is skipped so this shows project work.
      fetch("https://api.github.com/users/" + user + "/repos?sort=pushed&per_page=10", { headers: { Accept: "application/vnd.github+json" } })
        .then(function (r) { return r.ok ? r.json() : Promise.reject(r.status); })
        .then(function (repos) {
          var e = repos.filter(function (x) { return !x.fork && !/\.github\.io$/i.test(x.name); })[0];
          if (!e || !e.pushed_at) return;
          var d = { repo: e.name, at: e.pushed_at };
          try { sessionStorage.setItem(KEY, JSON.stringify({ t: Date.now(), d: d })); } catch (err) {}
          show(d);
        })
        .catch(function () { /* stay hidden */ });
    }
  }

  /* ---- Hero name: split into letters, size it to fill the row, react to the cursor ---- */
  var nameEl = document.querySelector("[data-fit]");
  if (nameEl) {
    var text = nameEl.textContent.trim();
    nameEl.setAttribute("aria-label", text);
    nameEl.textContent = "";
    Array.prototype.forEach.call(text, function (c, i) {
      var s = document.createElement("span");
      s.className = "ch";
      s.setAttribute("aria-hidden", "true");
      s.style.setProperty("--i", i);
      s.textContent = c === " " ? " " : c;
      nameEl.appendChild(s);
    });

    var spans = Array.prototype.slice.call(nameEl.querySelectorAll(".ch"));
    var fit = function () {
      var avail = nameEl.clientWidth;
      if (!avail || !spans.length) return;
      nameEl.style.fontSize = "100px";
      // Measure the letters themselves: scrollWidth would report the box, not the text.
      var w = spans[spans.length - 1].getBoundingClientRect().right - spans[0].getBoundingClientRect().left;
      if (!w) return;
      // Small safety margin so the last letter's side bearing never clips.
      nameEl.style.fontSize = Math.floor((100 * avail / w) * 0.985 * 100) / 100 + "px";
    };
    fit();
    if (document.fonts && document.fonts.ready) document.fonts.ready.then(fit);
    var rT;
    window.addEventListener("resize", function () { clearTimeout(rT); rT = setTimeout(fit, 60); });

    // Variable-font lens: letters near the pointer go thin and wide, then ease back.
    if (canHover && !reduceMotion) {
      var BASE_W = 760, BASE_S = 96, MIN_W = 230, MAX_S = 112;
      var state = spans.map(function () { return { w: BASE_W, s: BASE_S }; });
      var pointerX = 0, pointerY = 0, active = false, nraf = 0;
      var zone = nameEl.closest(".hero") || nameEl;
      var frame = function () {
        nraf = 0;
        var box = nameEl.getBoundingClientRect();
        var radius = Math.max(110, box.width * 0.11);
        var gap = Math.max(0, Math.abs(pointerY - (box.top + box.height / 2)) - box.height / 2);
        var vfac = active ? Math.exp(-Math.pow(gap / (box.height * 1.2), 2)) : 0;
        var moving = false;
        spans.forEach(function (sp, i) {
          var r = sp.getBoundingClientRect();
          var cx = (r.left + r.right) / 2;
          var inf = vfac ? Math.exp(-Math.pow((pointerX - cx) / radius, 2)) * vfac : 0;
          var tw = BASE_W - (BASE_W - MIN_W) * inf;
          var ts = BASE_S + (MAX_S - BASE_S) * inf;
          var st = state[i];
          st.w += (tw - st.w) * 0.16;
          st.s += (ts - st.s) * 0.16;
          if (Math.abs(tw - st.w) > 0.6 || Math.abs(ts - st.s) > 0.05) moving = true;
          else { st.w = tw; st.s = ts; }
          sp.style.fontVariationSettings = st.w === BASE_W && st.s === BASE_S ? "" : '"wght" ' + st.w.toFixed(0) + ', "wdth" ' + st.s.toFixed(1);
        });
        if (moving) nraf = requestAnimationFrame(frame);
      };
      var kickName = function () { if (!nraf) nraf = requestAnimationFrame(frame); };
      zone.addEventListener("pointermove", function (e) { pointerX = e.clientX; pointerY = e.clientY; active = true; kickName(); });
      zone.addEventListener("pointerleave", function () { active = false; kickName(); });
      window.addEventListener("scroll", function () { if (active) kickName(); }, { passive: true });
    }
  }

  /* ---- Copy email ---- */
  document.querySelectorAll("[data-copy]").forEach(function (btn) {
    var label = btn.querySelector(".copy-state");
    btn.addEventListener("click", function () {
      var value = btn.getAttribute("data-copy");
      var done = function (msg) {
        if (!label) return;
        label.textContent = msg;
        setTimeout(function () { label.textContent = "Copy email"; }, 1800);
      };
      if (navigator.clipboard && navigator.clipboard.writeText) {
        navigator.clipboard.writeText(value).then(function () { done("Copied"); }, function () { done("Press Ctrl+C"); });
      } else {
        done("Press Ctrl+C");
      }
    });
  });

  /* ---- Helper: run a draw loop only while the element is on screen ---- */
  var whileVisible = function (el, start, stop) {
    var onScreen = false;
    var update = function () {
      var want = onScreen && !document.hidden;
      if (want) start(); else stop();
    };
    if ("IntersectionObserver" in window) {
      new IntersectionObserver(function (entries) { onScreen = entries[0].isIntersecting; update(); }).observe(el);
    } else { onScreen = true; update(); }
    document.addEventListener("visibilitychange", update);
  };

  /* ---- Fingerprint ridge field ----
     A synthetic whorl: phase = w * r + theta, warped a little so it does not look
     like a target. Ridges are drawn where sin(phase) is high. Hovering shows the
     local ridge direction, which is perpendicular to the phase gradient. */
  var canvas = document.querySelector("[data-ridges]");
  if (canvas && canvas.getContext) {
    var ctx = canvas.getContext("2d");
    var host = canvas.parentElement;
    var readout = host.querySelector("[data-angle]");
    var buf, bctx, img, R, T, M, bw, bh, scale, omega, cssW, cssH;
    var pointer = null;
    var t0 = performance.now();
    var raf = 0, last = 0, running = false;
    var INK, PAPER;
    var setColors = function () { INK = hexToRgb(palette.ink); PAPER = hexToRgb(palette.card); };
    setColors();

    var field = function (x, y) {
      var S = Math.min(bw, bh);
      var u = (x - bw * 0.5) / S;
      var v = (y - bh * 0.52) / S;
      var uw = u + 0.035 * Math.sin(6.0 * v + 0.6) + 0.018 * Math.sin(13.0 * v);
      var vw = v + 0.03 * Math.sin(5.0 * u + 1.3);
      var r = Math.sqrt(uw * uw * 1.08 + vw * vw * 0.82);
      var th = Math.atan2(vw, uw);
      return { r: r, th: th };
    };

    function dy0(y, cy) { return y < cy ? 1.0 : 1.12; }
    function smooth(a, b, x) { var t = Math.min(1, Math.max(0, (x - a) / (b - a))); return t * t * (3 - 2 * t); }

    var setup = function () {
      var rect = canvas.getBoundingClientRect();
      cssW = Math.max(1, Math.round(rect.width));
      cssH = Math.max(1, Math.round(rect.height));
      var dpr = Math.min(window.devicePixelRatio || 1, 2);
      canvas.width = Math.round(cssW * dpr);
      canvas.height = Math.round(cssH * dpr);
      ctx.setTransform(dpr, 0, 0, dpr, 0, 0);

      scale = Math.min(1.5, dpr, Math.sqrt(260000 / (cssW * cssH)));
      bw = Math.max(1, Math.round(cssW * scale));
      bh = Math.max(1, Math.round(cssH * scale));
      buf = document.createElement("canvas");
      buf.width = bw;
      buf.height = bh;
      bctx = buf.getContext("2d");
      img = bctx.createImageData(bw, bh);

      var S = Math.min(bw, bh);
      var spacing = (parseFloat(canvas.getAttribute("data-spacing")) || 8.5) * scale;
      omega = (2 * Math.PI * S) / spacing;
      R = new Float32Array(bw * bh);
      T = new Float32Array(bw * bh);
      M = new Float32Array(bw * bh);
      var rx = Math.min(0.36 * bw, 0.3 * bh), ry = Math.min(0.42 * bh, 1.38 * rx), cx = bw * 0.5, cy = bh * 0.5;
      for (var y = 0; y < bh; y++) {
        for (var x = 0; x < bw; x++) {
          var k = y * bw + x;
          var f = field(x, y);
          R[k] = f.r;
          T[k] = f.th;
          var dx = (x - cx) / rx, dy = (y - cy) / (dy0(y, cy) * ry);
          var d = Math.pow(Math.pow(Math.abs(dx), 2.3) + Math.pow(Math.abs(dy), 2.3), 1 / 2.3);
          var edge = 1 - smooth(0.78, 1.0, d + 0.05 * Math.sin(x * 0.09) * Math.cos(y * 0.07));
          M[k] = edge * (0.82 + 0.18 * Math.sin(x * 0.031 + y * 0.017));
        }
      }
    };

    var render = function (now) {
      var t = reduceMotion ? 0 : (now - t0) / 1000 * 0.9;
      var data = img.data;
      for (var k = 0, n = bw * bh; k < n; k++) {
        var m = M[k];
        var a = 0;
        if (m > 0.001) {
          var s = Math.sin(omega * R[k] + T[k] - t);
          a = smooth(-0.05, 0.6, s) * m * 0.95;
        }
        var j = k * 4;
        data[j] = PAPER[0] + (INK[0] - PAPER[0]) * a;
        data[j + 1] = PAPER[1] + (INK[1] - PAPER[1]) * a;
        data[j + 2] = PAPER[2] + (INK[2] - PAPER[2]) * a;
        data[j + 3] = 255;
      }
      bctx.putImageData(img, 0, 0);
      ctx.imageSmoothingEnabled = true;
      ctx.imageSmoothingQuality = "high";
      ctx.drawImage(buf, 0, 0, cssW, cssH);
      if (pointer) drawLens(pointer.x, pointer.y);
    };

    var ridgeAngle = function (px, py) {
      var x = px * scale, y = py * scale, h = 0.75;
      var p = function (xx, yy) { var f = field(xx, yy); return omega * f.r + f.th; };
      var gx = (p(x + h, y) - p(x - h, y)) / (2 * h);
      var gy = (p(x, y + h) - p(x, y - h)) / (2 * h);
      return Math.atan2(gy, gx) + Math.PI / 2;
    };

    var drawLens = function (x, y) {
      var rad = Math.min(78, cssW * 0.2);
      ctx.save();
      ctx.beginPath();
      ctx.arc(x, y, rad, 0, Math.PI * 2);
      ctx.fillStyle = "rgba(" + PAPER.join(",") + ",0.84)";
      ctx.fill();
      ctx.clip();
      ctx.strokeStyle = palette.signal;
      ctx.lineCap = "round";
      ctx.lineWidth = 2;
      var step = 13;
      for (var gy = -rad; gy <= rad; gy += step) {
        for (var gx = -rad; gx <= rad; gx += step) {
          if (gx * gx + gy * gy > (rad - 6) * (rad - 6)) continue;
          var a = ridgeAngle(x + gx, y + gy);
          var l = 5;
          ctx.beginPath();
          ctx.moveTo(x + gx - Math.cos(a) * l, y + gy - Math.sin(a) * l);
          ctx.lineTo(x + gx + Math.cos(a) * l, y + gy + Math.sin(a) * l);
          ctx.stroke();
        }
      }
      ctx.restore();
      ctx.beginPath();
      ctx.arc(x, y, rad, 0, Math.PI * 2);
      ctx.strokeStyle = palette.signal;
      ctx.lineWidth = 1;
      ctx.stroke();
      if (readout) {
        var deg = ((-ridgeAngle(x, y) * 180) / Math.PI) % 180;
        if (deg < 0) deg += 180;
        readout.textContent = "Ridge direction here: " + Math.round(deg) + "°";
      }
    };

    var loop = function (now) {
      raf = 0;
      if (!running) return;
      if (now - last > 33) { last = now; render(now); }
      if (!reduceMotion) raf = requestAnimationFrame(loop);
    };
    var kick = function () { if (!raf) raf = requestAnimationFrame(loop); };

    setup();
    render(performance.now());
    whileVisible(canvas, function () { running = true; kick(); }, function () { running = false; });

    var onMove = function (e) {
      var r = canvas.getBoundingClientRect();
      pointer = { x: e.clientX - r.left, y: e.clientY - r.top };
      if (reduceMotion) render(performance.now()); else kick();
    };
    canvas.addEventListener("pointermove", onMove);
    canvas.addEventListener("pointerdown", onMove);
    canvas.addEventListener("pointerleave", function () {
      pointer = null;
      if (readout) readout.textContent = readout.getAttribute("data-default");
      render(performance.now());
    });
    window.addEventListener("themechange", function () { setColors(); render(performance.now()); });
    var sT;
    window.addEventListener("resize", function () {
      clearTimeout(sT);
      sT = setTimeout(function () { setup(); render(performance.now()); }, 120);
    });
  }

  /* ---- Batching simulation (nanoserve) ----
     The same stream of requests goes to two schedulers with the same number of
     slots. Static batching waits for the longest request in a batch before taking
     new work; continuous batching refills a slot the moment it frees up. */
  document.querySelectorAll("[data-sim]").forEach(function (box) {
    var cv = box.querySelector("canvas");
    if (!cv || !cv.getContext) return;
    var c = cv.getContext("2d");
    var SLOTS = 6, MAXLEN = 96, STEP_MS = 55;
    var W, H;

    var rng = function (seed) {
      return function () {
        seed |= 0; seed = (seed + 0x6d2b79f5) | 0;
        var t = Math.imul(seed ^ (seed >>> 15), 1 | seed);
        t = (t + Math.imul(t ^ (t >>> 7), 61 | t)) ^ t;
        return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
      };
    };
    var lengths = [];
    var makeLengths = function () {
      var r = rng(20260704);
      lengths = [];
      for (var i = 0; i < 4000; i++) {
        // lognormal output lengths, like the benchmark's traffic
        var u1 = Math.max(1e-9, r()), u2 = r();
        var z = Math.sqrt(-2 * Math.log(u1)) * Math.cos(2 * Math.PI * u2);
        lengths.push(Math.max(4, Math.min(MAXLEN, Math.round(Math.exp(3.0 + 0.75 * z)))));
      }
    };
    makeLengths();

    var makeSched = function (kind) {
      return { kind: kind, next: 0, slots: [], finished: 0, busy: 0, total: 0, flash: [] };
    };
    var A, B, steps;
    var reset = function () {
      A = makeSched("static");
      B = makeSched("continuous");
      for (var i = 0; i < SLOTS; i++) {
        A.slots.push(null); B.slots.push(null);
        A.flash.push(0); B.flash.push(0);
      }
      steps = 0;
    };
    reset();

    var take = function (s) { var len = lengths[s.next % lengths.length]; s.next++; return { len: len, done: 0 }; };
    var stepSched = function (s) {
      var i;
      if (s.kind === "static") {
        var allDone = s.slots.every(function (x) { return !x || x.done >= x.len; });
        if (allDone) for (i = 0; i < SLOTS; i++) s.slots[i] = take(s);
      } else {
        for (i = 0; i < SLOTS; i++) if (!s.slots[i] || s.slots[i].done >= s.slots[i].len) s.slots[i] = take(s);
      }
      for (i = 0; i < SLOTS; i++) {
        var x = s.slots[i];
        s.total++;
        if (x && x.done < x.len) {
          x.done++;
          s.busy++;
          if (x.done === x.len) { s.finished++; s.flash[i] = 1; }
        }
      }
      for (i = 0; i < SLOTS; i++) s.flash[i] = Math.max(0, s.flash[i] - 0.12);
    };
    var step = function () {
      stepSched(A); stepSched(B); steps++;
      if (steps > 2600) reset();
    };

    var size = function () {
      var r = cv.getBoundingClientRect();
      W = Math.max(1, Math.round(r.width));
      H = Math.max(1, Math.round(r.height));
      var dpr = Math.min(window.devicePixelRatio || 1, 2);
      cv.width = Math.round(W * dpr);
      cv.height = Math.round(H * dpr);
      c.setTransform(dpr, 0, 0, dpr, 0, 0);
    };

    var rr = function (x, y, w, h, r) {
      r = Math.min(r, h / 2, w / 2);
      c.beginPath();
      c.moveTo(x + r, y);
      c.arcTo(x + w, y, x + w, y + h, r);
      c.arcTo(x + w, y + h, x, y + h, r);
      c.arcTo(x, y + h, x, y, r);
      c.arcTo(x, y, x + w, y, r);
      c.closePath();
    };

    var drawPanel = function (s, title, y0, h) {
      var labelH = 26;
      c.textBaseline = "alphabetic";
      c.fillStyle = palette.ink;
      c.font = "600 13px Archivo, system-ui, sans-serif";
      c.textAlign = "left";
      c.fillText(title, 0, y0 + 15);
      c.textAlign = "right";
      c.font = "500 12px Archivo, system-ui, sans-serif";
      c.fillStyle = palette.mute;
      var util = s.total ? Math.round((100 * s.busy) / s.total) : 0;
      var finText = s.finished + " finished";
      c.font = "650 13px Archivo, system-ui, sans-serif";
      var finW = c.measureText(finText).width;
      c.fillStyle = palette.ink;
      c.fillText(finText, W, y0 + 15);
      c.font = "500 12px Archivo, system-ui, sans-serif";
      c.fillStyle = palette.mute;
      if (W > 300) c.fillText("slots busy " + util + "%", W - finW - 16, y0 + 15);
      var gap = 5;
      var laneH = (h - labelH - gap * (SLOTS - 1)) / SLOTS;
      for (var i = 0; i < SLOTS; i++) {
        var y = y0 + labelH + i * (laneH + gap);
        c.fillStyle = palette["paper"];
        rr(0, y, W, laneH, 4); c.fill();
        var x = s.slots[i];
        if (!x) continue;
        var idle = x.done >= x.len;
        var w = Math.max(3, (x.done / MAXLEN) * W);
        if (idle) {
          // finished early, now waiting for the slowest request in the batch
          c.save();
          rr(0, y, W, laneH, 4); c.clip();
          c.strokeStyle = palette.rule;
          c.lineWidth = 1;
          for (var hx = -laneH; hx < W; hx += 7) { c.beginPath(); c.moveTo(hx, y + laneH); c.lineTo(hx + laneH, y); c.stroke(); }
          c.restore();
        } else {
          c.fillStyle = palette.ink;
          rr(0, y, w, laneH, 4); c.fill();
        }
        if (s.flash[i] > 0) {
          c.globalAlpha = s.flash[i] * 0.6;
          c.fillStyle = palette.signal;
          rr(0, y, W, laneH, 4); c.fill();
          c.globalAlpha = 1;
        }
      }
    };

    var draw = function () {
      c.clearRect(0, 0, W, H);
      var gapPanels = 22;
      var ph = (H - gapPanels) / 2;
      drawPanel(A, "Static batching", 0, ph);
      drawPanel(B, "Continuous batching", ph + gapPanels, ph);
    };

    var timer = 0;
    var start = function () {
      if (timer || reduceMotion) return;
      timer = setInterval(function () { step(); draw(); }, STEP_MS);
    };
    var stop = function () { clearInterval(timer); timer = 0; };

    size();
    if (reduceMotion) { for (var i = 0; i < 700; i++) step(); }
    else { for (var j = 0; j < 160; j++) step(); }
    draw();
    whileVisible(cv, start, stop);
    window.addEventListener("themechange", draw);
    var zT;
    window.addEventListener("resize", function () { clearTimeout(zT); zT = setTimeout(function () { size(); draw(); }, 120); });
  });
})();
