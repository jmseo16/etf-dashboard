(function () {
  "use strict";
  var DATA = JSON.parse(document.getElementById("hsch-data").textContent);
  var canvas = document.getElementById("canvas");
  var side = document.getElementById("side");
  var tip = document.getElementById("tip");
  var crumbs = document.getElementById("crumbs");
  var stack = [];            // [{cell, inst}]
  var views = {};
  var viewBoxes = {};
  var sticky = null;

  Array.prototype.forEach.call(document.querySelectorAll(".view"), function (v) {
    views[v.getAttribute("data-cell")] = v;
  });

  function store(k, v) { try { localStorage.setItem("hsch:" + k, v); } catch (e) {} }
  function load(k) { try { return localStorage.getItem("hsch:" + k); } catch (e) { return null; } }

  // ---------------------------------------------------------------- toggles
  var TOGGLES = { wl: "hide-wl", val: "hide-val", name: "hide-name", net: "show-net" };
  Array.prototype.forEach.call(document.querySelectorAll("[data-toggle]"), function (cb) {
    var key = cb.getAttribute("data-toggle");
    var saved = load("t-" + key);
    if (saved !== null) cb.checked = saved === "1";
    function apply() {
      var cls = TOGGLES[key];
      var on = cb.checked;
      if (cls.indexOf("hide-") === 0) document.body.classList.toggle(cls, !on);
      else document.body.classList.toggle(cls, on);
      store("t-" + key, on ? "1" : "0");
    }
    cb.addEventListener("change", apply);
    apply();
  });

  // ---------------------------------------------------------------- navigation
  function cellInfo(c) { return DATA.cells[c] || {}; }

  function show(cell, push) {
    if (!views[cell]) return;
    Object.keys(views).forEach(function (k) { views[k].hidden = k !== cell; });
    if (push === undefined) stack = [{ cell: cell, inst: null }];
    sticky = null;
    clearHL();
    if (!viewBoxes[cell]) fit(cell);
    renderCrumbs();
    renderSide();
    var sel = document.getElementById("cell-jump");
    sel.value = cell;
  }

  function current() { return stack[stack.length - 1].cell; }

  function descend(inst, ref) {
    if (!views[ref]) return;
    stack.push({ cell: ref, inst: inst });
    show(ref, true);
  }

  function up() {
    if (stack.length > 1) { stack.pop(); show(current(), true); }
  }

  function renderCrumbs() {
    crumbs.innerHTML = "";
    stack.forEach(function (s, i) {
      if (i) { var sp = document.createElement("span"); sp.className = "sep"; sp.textContent = "›"; crumbs.appendChild(sp); }
      var a = document.createElement("a");
      var info = cellInfo(s.cell);
      a.textContent = (s.inst ? s.inst + " : " : "") + (info.display || s.cell);
      if (i === stack.length - 1) a.className = "cur";
      else a.addEventListener("click", function () { stack = stack.slice(0, i + 1); show(s.cell, true); });
      crumbs.appendChild(a);
    });
  }

  // ---------------------------------------------------------------- side panel
  function esc(s) { return String(s).replace(/[&<>"]/g, function (c) { return { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" }[c]; }); }

  function renderSide() {
    var c = current();
    var info = cellInfo(c);
    var h = "<h2>" + esc(info.display || c) + "</h2>";
    h += '<div class="why">' + esc(info.label || "") + (info.auto ? " · 자동 생성 블록" : "") + "</div>";
    if (info.reason) h += '<div class="why">인식 근거: ' + esc(info.reason) + "</div>";
    // port mapping from parent
    if (stack.length > 1) {
      var parent = stack[stack.length - 2].cell;
      var inst = stack[stack.length - 1].inst;
      var pi = (cellInfo(parent).insts || {})[inst];
      if (pi) {
        h += "<h3>포트 연결 (" + esc(inst) + " @ " + esc(parent) + ")</h3><table>";
        Object.keys(pi.pins).forEach(function (p) {
          h += "<tr><td>" + esc(p) + '</td><td><span class="netlink" data-net="' + esc(p) + '">' + esc(pi.pins[p]) + "</span></td></tr>";
        });
        h += "</table>";
      }
    }
    if (info.ports && info.ports.length) {
      h += "<h3>포트</h3><table>";
      info.ports.forEach(function (p) {
        h += '<tr><td>' + esc((info.roles || {})[p] || "") + '</td><td><span class="netlink" data-net="' + esc(p) + '">' + esc(p) + "</span></td></tr>";
      });
      h += "</table>";
    }
    var v = info.verify;
    if (v) {
      h += "<h3>검증</h3>";
      h += "<div>" + (v.ok ? "✅ 연결 일치 (원본 netlist와 동일)" : "❌ 연결 불일치") + "</div>";
      (v.errors || []).forEach(function (e) { h += '<div class="warn">' + esc(e) + "</div>"; });
      if (v.lint) {
        h += '<div class="why">교차 ' + v.lint.crossings + " · 경고 " + (v.lint.warnings || []).length + "</div>";
        (v.lint.warnings || []).slice(0, 8).forEach(function (w) { h += '<div class="warn">' + esc(w) + "</div>"; });
      }
    }
    (info.warnings || []).forEach(function (w) { h += '<div class="warn">' + esc(w) + "</div>"; });
    h += '<h3>사용법</h3><div class="why">블록 클릭 → 내부 보기 · Esc → 상위 · 휠 → 확대/축소 · 드래그 → 이동 · 넷 클릭 → 강조 고정 · F → 화면 맞춤</div>';
    side.innerHTML = h;
    Array.prototype.forEach.call(side.querySelectorAll(".netlink"), function (el) {
      el.addEventListener("mouseenter", function () { hl(el.getAttribute("data-net")); });
      el.addEventListener("mouseleave", function () { if (!sticky) clearHL(); else hl(sticky); });
    });
  }

  // ---------------------------------------------------------------- highlight
  function svgOf(cell) { return views[cell].querySelector("svg"); }
  function clearHL() {
    Array.prototype.forEach.call(document.querySelectorAll(".hl"), function (e) { e.classList.remove("hl"); });
  }
  function hl(net) {
    clearHL();
    if (!net) return;
    var s = svgOf(current());
    Array.prototype.forEach.call(s.querySelectorAll('[data-net="' + (window.CSS && CSS.escape ? CSS.escape(net) : net) + '"]'), function (e) {
      e.classList.add("hl");
    });
  }

  // ---------------------------------------------------------------- tooltip
  function devTip(cell, inst) {
    var info = (cellInfo(cell).insts || {})[inst];
    if (!info) return inst;
    var t = inst + "  (" + info.type + ")";
    var p = info.params || {};
    var keys = ["w", "l", "m", "r", "c", "l"];
    var shown = {};
    keys.forEach(function (k) { if (p[k] !== undefined && !shown[k]) { t += "\n" + k.toUpperCase() + " = " + p[k]; shown[k] = 1; } });
    if (info.ref) t += "\n→ " + (cellInfo(info.ref).display || info.ref) + "  (클릭해서 열기)";
    Object.keys(info.pins).forEach(function (pn) { t += "\n" + pn + " : " + info.pins[pn]; });
    return t;
  }

  canvas.addEventListener("mousemove", function (ev) {
    var g = ev.target.closest ? ev.target.closest(".symg") : null;
    var netEl = ev.target.closest ? ev.target.closest("[data-net]") : null;
    var r = canvas.getBoundingClientRect();
    if (g && !netEl) {
      tip.textContent = devTip(current(), g.getAttribute("data-inst"));
      tip.hidden = false;
      tip.style.left = Math.min(ev.clientX - r.left + 14, r.width - 290) + "px";
      tip.style.top = (ev.clientY - r.top + 14) + "px";
    } else if (netEl) {
      tip.textContent = "net: " + netEl.getAttribute("data-net");
      tip.hidden = false;
      tip.style.left = Math.min(ev.clientX - r.left + 14, r.width - 290) + "px";
      tip.style.top = (ev.clientY - r.top + 14) + "px";
      if (!sticky) hl(netEl.getAttribute("data-net"));
    } else {
      tip.hidden = true;
      if (!sticky) clearHL();
    }
  });
  canvas.addEventListener("mouseleave", function () { tip.hidden = true; if (!sticky) clearHL(); });

  // ---------------------------------------------------------------- pan / zoom
  function getVB(cell) { return viewBoxes[cell]; }
  function setVB(cell, vb) {
    viewBoxes[cell] = vb;
    svgOf(cell).setAttribute("viewBox", vb.join(" "));
  }
  function fit(cell) {
    var b = svgOf(cell).getAttribute("data-bounds").split(",").map(Number);
    setVB(cell, [b[0], b[1], b[2] - b[0], b[3] - b[1]]);
  }

  var drag = null, moved = false;
  canvas.addEventListener("wheel", function (ev) {
    var s = svgOf(current());
    if (!s.contains(ev.target) && ev.target !== s) return;
    ev.preventDefault();
    var vb = getVB(current()).slice();
    var r = s.getBoundingClientRect();
    var scale = Math.min(r.width / vb[2], r.height / vb[3]);
    var ox = (r.width - vb[2] * scale) / 2, oy = (r.height - vb[3] * scale) / 2;
    var mx = vb[0] + (ev.clientX - r.left - ox) / scale;
    var my = vb[1] + (ev.clientY - r.top - oy) / scale;
    var k = Math.exp(ev.deltaY * 0.0015);
    vb[0] = mx - (mx - vb[0]) * k; vb[1] = my - (my - vb[1]) * k; vb[2] *= k; vb[3] *= k;
    setVB(current(), vb);
  }, { passive: false });

  canvas.addEventListener("pointerdown", function (ev) {
    if (ev.button !== 0) return;
    drag = { x: ev.clientX, y: ev.clientY, vb: getVB(current()).slice() };
    moved = false;
  });
  window.addEventListener("pointermove", function (ev) {
    if (!drag) return;
    var s = svgOf(current());
    var r = s.getBoundingClientRect();
    var vb = drag.vb;
    var scale = Math.min(r.width / vb[2], r.height / vb[3]);
    var dx = (ev.clientX - drag.x) / scale, dy = (ev.clientY - drag.y) / scale;
    if (Math.abs(ev.clientX - drag.x) + Math.abs(ev.clientY - drag.y) > 4) { moved = true; s.classList.add("dragging"); }
    if (moved) setVB(current(), [vb[0] - dx, vb[1] - dy, vb[2], vb[3]]);
  });
  window.addEventListener("pointerup", function () {
    if (drag) svgOf(current()).classList.remove("dragging");
    drag = null;
  });

  canvas.addEventListener("click", function (ev) {
    if (moved) { moved = false; return; }
    var g = ev.target.closest ? ev.target.closest(".symg.clickable") : null;
    var netEl = ev.target.closest ? ev.target.closest("[data-net]") : null;
    if (netEl && !g) {
      var n = netEl.getAttribute("data-net");
      sticky = sticky === n ? null : n;
      if (sticky) hl(sticky); else clearHL();
      return;
    }
    if (g) { descend(g.getAttribute("data-inst"), g.getAttribute("data-ref")); return; }
    sticky = null; clearHL();
  });
  canvas.addEventListener("dblclick", function () { fit(current()); });

  document.getElementById("btn-up").addEventListener("click", up);
  document.getElementById("btn-fit").addEventListener("click", function () { fit(current()); });
  document.addEventListener("keydown", function (ev) {
    var tg = ev.target || {};
    if ((tg.tagName === "INPUT" && tg.type !== "checkbox") || /select|textarea/i.test(tg.tagName || "")) return;
    if (ev.key === "Escape" || ev.key === "Backspace") { up(); ev.preventDefault(); }
    if (ev.key === "f" || ev.key === "F") fit(current());
  });

  var sel = document.getElementById("cell-jump");
  Object.keys(views).forEach(function (c) {
    var o = document.createElement("option");
    o.value = c; o.textContent = cellInfo(c).display || c;
    sel.appendChild(o);
  });
  sel.addEventListener("change", function () { show(sel.value); });

  // public hook for scripted screenshots / tests
  window.HSCH = {
    show: function (cell) { show(cell); },
    path: function (insts) {           // e.g. ["X_DFE","X_DFF","X_MASTER"]
      show(DATA.top);
      insts.forEach(function (i) {
        var info = (cellInfo(current()).insts || {})[i];
        if (info && info.ref) descend(i, info.ref);
      });
    },
    cells: function () { return Object.keys(views); }
  };
  show(DATA.top);
})();
