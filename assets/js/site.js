/* aadityakumawat.me: small, dependency-free behaviour. */
(function () {
  "use strict";

  var root = document.documentElement;
  root.classList.add("js");
  var reduceMotion = window.matchMedia("(prefers-reduced-motion: reduce)").matches;

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

  /* ---- Hero name: split into letters, then size it to fill the row exactly ---- */
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

    var spans = nameEl.querySelectorAll(".ch");
    var fit = function () {
      var avail = nameEl.clientWidth;
      if (!avail || !spans.length) return;
      nameEl.style.fontSize = "100px";
      // Measure the letters themselves: scrollWidth would report the box, not the text.
      var w = spans[spans.length - 1].getBoundingClientRect().right - spans[0].getBoundingClientRect().left;
      if (!w) return;
      // Small safety margin so the last letter's side bearing never clips.
      nameEl.style.fontSize = Math.floor((100 * avail / w) * 0.995 * 100) / 100 + "px";
    };
    fit();
    if (document.fonts && document.fonts.ready) document.fonts.ready.then(fit);
    var rT;
    window.addEventListener("resize", function () { clearTimeout(rT); rT = setTimeout(fit, 60); });
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
    var visible = true;
    var raf = 0, last = 0;

    var INK = [0, 0, 0];
    var PAPER = [250, 250, 249];
    var SIGNAL = "#ff4d00";

    var field = function (x, y) {
      // x, y in buffer pixels -> phase (without time)
      var S = Math.min(bw, bh);
      var u = (x - bw * 0.5) / S;
      var v = (y - bh * 0.52) / S;
      var uw = u + 0.035 * Math.sin(6.0 * v + 0.6) + 0.018 * Math.sin(13.0 * v);
      var vw = v + 0.03 * Math.sin(5.0 * u + 1.3);
      var r = Math.sqrt(uw * uw * 1.08 + vw * vw * 0.82);
      var th = Math.atan2(vw, uw);
      return { r: r, th: th };
    };

    var setup = function () {
      var rect = canvas.getBoundingClientRect();
      cssW = Math.max(1, Math.round(rect.width));
      cssH = Math.max(1, Math.round(rect.height));
      var dpr = Math.min(window.devicePixelRatio || 1, 2);
      canvas.width = Math.round(cssW * dpr);
      canvas.height = Math.round(cssH * dpr);
      ctx.setTransform(dpr, 0, 0, dpr, 0, 0);

      // Ridge buffer: cap the pixel count so each frame stays cheap.
      scale = Math.min(1.5, dpr, Math.sqrt(260000 / (cssW * cssH)));
      bw = Math.max(1, Math.round(cssW * scale));
      bh = Math.max(1, Math.round(cssH * scale));
      buf = document.createElement("canvas");
      buf.width = bw;
      buf.height = bh;
      bctx = buf.getContext("2d");
      img = bctx.createImageData(bw, bh);

      var S = Math.min(bw, bh);
      var spacing = 8.5 * scale; // ridge period in buffer pixels
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
          // finger-shaped mask with a soft, uneven edge (pressure falloff)
          var dx = (x - cx) / rx, dy = (y - cy) / (dy0(y, cy) * ry);
          var d = Math.pow(Math.pow(Math.abs(dx), 2.3) + Math.pow(Math.abs(dy), 2.3), 1 / 2.3);
          var edge = 1 - smooth(0.78, 1.0, d + 0.05 * Math.sin(x * 0.09) * Math.cos(y * 0.07));
          M[k] = edge * (0.82 + 0.18 * Math.sin(x * 0.031 + y * 0.017));
        }
      }
    };

    // top of the finger is rounder than the bottom
    function dy0(y, cy) { return y < cy ? 1.0 : 1.12; }
    function smooth(a, b, x) { var t = Math.min(1, Math.max(0, (x - a) / (b - a))); return t * t * (3 - 2 * t); }

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
      // px, py in CSS px. Phase gradient by finite differences, ridge runs perpendicular.
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
      ctx.fillStyle = "rgba(250,250,249,0.82)";
      ctx.fill();
      ctx.clip();
      ctx.strokeStyle = SIGNAL;
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
      ctx.strokeStyle = SIGNAL;
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
      if (!visible) return;
      if (now - last > 33) { last = now; render(now); }
      if (!reduceMotion) raf = requestAnimationFrame(loop);
    };
    var kick = function () { if (!raf) raf = requestAnimationFrame(loop); };

    setup();
    render(performance.now());
    kick();

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

    if ("IntersectionObserver" in window) {
      new IntersectionObserver(function (entries) {
        visible = entries[0].isIntersecting;
        if (visible) kick();
      }).observe(canvas);
    }
    document.addEventListener("visibilitychange", function () {
      visible = !document.hidden;
      if (visible) kick();
    });
    var sT;
    window.addEventListener("resize", function () {
      clearTimeout(sT);
      sT = setTimeout(function () { setup(); render(performance.now()); }, 120);
    });
  }
})();
