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

  // ---------------------------------------------------------------- reliable taps
  // Touch browsers drop the click of a tap that follows a pan/fling within ~300 ms and
  // delay clicks in general. On touch we act on the finger-up of a short tap and swallow
  // the click that may follow; mouse and keyboard keep using the normal click.
  var lastTouch = 0;
  var TAP_SLOP = 12;
  function onTap(el, fn) {
    var down = null, fired = 0;
    el.addEventListener("pointerdown", function (ev) {
      if (ev.pointerType !== "mouse") { lastTouch = Date.now(); down = { id: ev.pointerId, x: ev.clientX, y: ev.clientY }; }
    });
    el.addEventListener("pointerup", function (ev) {
      if (!down || ev.pointerId !== down.id) return;
      var d = Math.abs(ev.clientX - down.x) + Math.abs(ev.clientY - down.y);
      down = null;
      lastTouch = Date.now();
      if (d > TAP_SLOP) return;
      fired = Date.now();
      fn(ev, false);
    });
    el.addEventListener("pointercancel", function () { down = null; });
    el.addEventListener("click", function (ev) {
      if (Date.now() - fired < 800) { ev.preventDefault(); ev.stopPropagation(); return; }
      fn(ev, true);
    }, true);
  }

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
    cb.addEventListener("change", apply);         // mouse / keyboard (native toggle)
    onTap(cb.closest("label") || cb, function (ev, fromClick) {
      if (fromClick) return;                      // native click toggles, change -> apply
      cb.checked = !cb.checked;                   // touch: toggle on finger-up
      apply();
    });
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
    hideTip();   // a tooltip must never survive a change of view
    resetGesture();
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
      else onTap(a, function () { stack = stack.slice(0, i + 1); show(s.cell, true); });
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
        var role = (info.roles || {})[p] || "";
        h += '<tr><td>' + esc(ROLE_KO[role] || role) + '</td><td><span class="netlink" data-net="' + esc(p) + '">' + esc(p) + "</span></td></tr>";
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
    h += '<h3>사용법</h3><div class="why">블록 클릭/탭 → 내부 보기 · Esc → 상위 · 휠 또는 두 손가락 → 확대/축소 · 드래그 → 이동 · 넷 클릭 → 강조 고정 · 소자 탭 → 정보 · F/더블클릭 → 화면 맞춤</div>';
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
  var TYPE_KO = { nmos: "NMOS", pmos: "PMOS", res: "저항", cap: "커패시터", ind: "인덕터",
                  vsrc: "전압원", isrc: "전류원", inst: "블록", diode: "다이오드", bjt: "BJT" };
  var ROLE_KO = { "in": "입력", out: "출력", clk: "클럭", bias: "바이어스", power: "전원",
                  ground: "접지", inout: "입출력" };
  function devTip(cell, inst) {
    var info = (cellInfo(cell).insts || {})[inst];
    if (!info) return inst;
    var t = inst + "  (" + (TYPE_KO[info.type] || info.type) + ")";
    var p = info.params || {};
    var keys = ["w", "l", "m", "r", "c", "l"];
    var shown = {};
    keys.forEach(function (k) { if (p[k] !== undefined && !shown[k]) { t += "\n" + k.toUpperCase() + " = " + p[k]; shown[k] = 1; } });
    if (info.ref) t += "\n→ " + (cellInfo(info.ref).display || info.ref) + "  (클릭해서 열기)";
    Object.keys(info.pins).forEach(function (pn) { t += "\n" + pn + " : " + info.pins[pn]; });
    return t;
  }

  function showTipFor(target, cx, cy) {
    var g = target.closest ? target.closest(".symg") : null;
    var netEl = target.closest ? target.closest("[data-net]") : null;
    var r = canvas.getBoundingClientRect();
    var text = null;
    if (g && !netEl) text = devTip(current(), g.getAttribute("data-inst"));
    else if (netEl) text = "넷: " + netEl.getAttribute("data-net");
    if (!text) { hideTip(); return null; }
    tip.textContent = text;
    tip.hidden = false;
    tip.style.left = Math.max(4, Math.min(cx - r.left + 14, r.width - 290)) + "px";
    tip.style.top = Math.max(4, Math.min(cy - r.top + 14, r.height - 60)) + "px";
    return netEl;
  }
  canvas.addEventListener("mousemove", function (ev) {
    // touch screens emit compatibility mouse events after a tap: ignore them, or a
    // tooltip pops up on whatever is under the finger in the view we just opened
    if (Date.now() - lastTouch < 800) return;
    var netEl = showTipFor(ev.target, ev.clientX, ev.clientY);
    if (netEl) { if (!sticky) hl(netEl.getAttribute("data-net")); }
    else if (!sticky) clearHL();
  });
  function hideTip() { tip.hidden = true; tip.textContent = ""; }
  canvas.addEventListener("mouseleave", function () { hideTip(); if (!sticky) clearHL(); });

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

  // ---------------------------------------------------------------- pointer gestures
  // One finger / mouse drag = pan, two fingers = pinch zoom, wheel = zoom.
  // Every pointer is tracked by id and captured by the canvas, and pointercancel /
  // lostpointercapture end the gesture, so a cancelled touch can never leave a stale
  // drag behind (that stale drag is what threw the drawing off-screen on the next tap).
  var pointers = {};
  var gesture = null;
  var moved = false;
  var multi = false;

  function geom(s, vb) {
    var r = s.getBoundingClientRect();
    var sc = Math.min(r.width / vb[2], r.height / vb[3]) || 1;
    return { r: r, sc: sc, ox: (r.width - vb[2] * sc) / 2, oy: (r.height - vb[3] * sc) / 2 };
  }
  function toUser(s, vb, cx, cy) {
    var g = geom(s, vb);
    return { x: vb[0] + (cx - g.r.left - g.ox) / g.sc, y: vb[1] + (cy - g.r.top - g.oy) / g.sc };
  }
  function clampK(cell, vb, k) {
    var b = svgOf(cell).getAttribute("data-bounds").split(",").map(Number);
    var w0 = b[2] - b[0];
    var w = vb[2] * k;
    if (w < w0 * 0.05) k = (w0 * 0.05) / vb[2];
    if (w > w0 * 20) k = (w0 * 20) / vb[2];
    return k;
  }
  function zoomAt(vb, mx, my, k) {
    return [mx - (mx - vb[0]) * k, my - (my - vb[1]) * k, vb[2] * k, vb[3] * k];
  }
  function resetGesture() { pointers = {}; gesture = null; }
  function startGesture() {
    var ids = Object.keys(pointers);
    if (!ids.length) { gesture = null; return; }
    var vb = getVB(current()).slice();
    if (ids.length === 1) {
      var p = pointers[ids[0]];
      gesture = { vb: vb, x: p.x, y: p.y };
    } else {
      var a = pointers[ids[0]], b = pointers[ids[1]];
      gesture = { vb: vb, x: (a.x + b.x) / 2, y: (a.y + b.y) / 2, dist: Math.hypot(a.x - b.x, a.y - b.y) || 1 };
    }
  }
  function endPointer(ev) {
    // lostpointercapture bubbles up from the element that held the implicit touch capture
    // when the canvas takes over; only the canvas losing capture ends the gesture
    if (ev.type === "lostpointercapture" && ev.target !== canvas) return;
    if (!(ev.pointerId in pointers)) return;
    delete pointers[ev.pointerId];
    svgOf(current()).classList.remove("dragging");
    startGesture();            // pinch -> pan hand-over without a jump
  }

  canvas.addEventListener("wheel", function (ev) {
    var s = svgOf(current());
    if (!s.contains(ev.target) && ev.target !== s) return;
    ev.preventDefault();
    hideTip();
    var vb = getVB(current()).slice();
    var m = toUser(s, vb, ev.clientX, ev.clientY);
    var k = clampK(current(), vb, Math.exp(ev.deltaY * 0.0015));
    setVB(current(), zoomAt(vb, m.x, m.y, k));
  }, { passive: false });

  canvas.addEventListener("pointerdown", function (ev) {
    var s = svgOf(current());
    if (!s.contains(ev.target) && ev.target !== s) return;
    if (ev.pointerType === "mouse" && ev.button !== 0) return;
    if (ev.pointerType !== "mouse") { hideTip(); lastTouch = Date.now(); }
    if (!Object.keys(pointers).length) { moved = false; multi = false; }
    pointers[ev.pointerId] = { x: ev.clientX, y: ev.clientY };
    if (Object.keys(pointers).length > 1) multi = true;
    // capture only once a real drag/pinch starts: capturing on pointerdown would retarget
    // the following click to the canvas and break clicking blocks / nets
    if (Object.keys(pointers).length > 1) capture(ev.pointerId);
    startGesture();
  });
  function capture(id) {
    try { if (!canvas.hasPointerCapture(id)) canvas.setPointerCapture(id); } catch (e) {}
  }
  canvas.addEventListener("pointermove", function (ev) {
    if (!(ev.pointerId in pointers) || !gesture) return;
    pointers[ev.pointerId] = { x: ev.clientX, y: ev.clientY };
    var s = svgOf(current());
    var ids = Object.keys(pointers);
    var vb = gesture.vb;
    if (ids.length === 1) {
      var dx = ev.clientX - gesture.x, dy = ev.clientY - gesture.y;
      var slop = ev.pointerType === "mouse" ? 4 : 12;               // a thumb tap wobbles
      if (!moved && Math.abs(dx) + Math.abs(dy) <= slop) return;   // still a tap
      moved = true;
      capture(ev.pointerId);
      s.classList.add("dragging");
      hideTip();
      var sc = geom(s, vb).sc;
      setVB(current(), [vb[0] - dx / sc, vb[1] - dy / sc, vb[2], vb[3]]);
    } else {
      var a = pointers[ids[0]], b = pointers[ids[1]];
      var mx = (a.x + b.x) / 2, my = (a.y + b.y) / 2;
      var dist = Math.hypot(a.x - b.x, a.y - b.y) || 1;
      moved = true;
      hideTip();
      var anchor = toUser(s, vb, gesture.x, gesture.y);
      var k = clampK(current(), vb, gesture.dist / dist);
      var nvb = zoomAt(vb, anchor.x, anchor.y, k);
      var sc2 = geom(s, nvb).sc;
      nvb[0] -= (mx - gesture.x) / sc2;
      nvb[1] -= (my - gesture.y) / sc2;
      setVB(current(), nvb);
    }
  });
  ["pointerup", "pointercancel", "lostpointercapture"].forEach(function (t) {
    canvas.addEventListener(t, endPointer);
  });

  // what a click (mouse) or a tap (touch) on the drawing does
  function canvasAction(target, cx, cy, isTouch) {
    var g = target.closest ? target.closest(".symg.clickable") : null;
    var netEl = target.closest ? target.closest("[data-net]") : null;
    if (netEl && !g) {
      var n = netEl.getAttribute("data-net");
      sticky = sticky === n ? null : n;
      if (sticky) hl(sticky); else clearHL();
      if (isTouch) { if (sticky) showTipFor(target, cx, cy); else hideTip(); }
      return;
    }
    if (g) { hideTip(); descend(g.getAttribute("data-inst"), g.getAttribute("data-ref")); return; }
    sticky = null; clearHL();
    if (isTouch) showTipFor(target, cx, cy);   // tap a transistor -> its W/L and nets
    else hideTip();
  }
  var canvasTapAt = 0;
  canvas.addEventListener("pointerup", function (ev) {
    if (ev.pointerType === "mouse" || moved || multi) return;
    if (Object.keys(pointers).length) return;            // other fingers still down
    lastTouch = Date.now();
    canvasTapAt = Date.now();
    canvasAction(ev.target, ev.clientX, ev.clientY, true);
  });
  canvas.addEventListener("click", function (ev) {
    if (Date.now() - canvasTapAt < 800) return;          // already handled as a tap
    if (moved) { moved = false; return; }
    canvasAction(ev.target, ev.clientX, ev.clientY, false);
  });
  canvas.addEventListener("dblclick", function () { fit(current()); });

  onTap(document.getElementById("btn-up"), function () { up(); });
  var pptBtn = document.getElementById("btn-ppt");
  if (pptBtn) onTap(pptBtn, function () {
    var el = document.getElementById("hsch-pptx");
    var bin = atob(el.textContent.trim());
    var arr = new Uint8Array(bin.length);
    for (var i = 0; i < bin.length; i++) arr[i] = bin.charCodeAt(i);
    var blob = new Blob([arr], { type: "application/vnd.openxmlformats-officedocument.presentationml.presentation" });
    var a = document.createElement("a");
    a.href = URL.createObjectURL(blob);
    a.download = el.getAttribute("data-name") || "schematic.pptx";
    document.body.appendChild(a);
    a.click();
    setTimeout(function () { URL.revokeObjectURL(a.href); a.remove(); }, 2000);
  });
  onTap(document.getElementById("btn-fit"), function () { fit(current()); });
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
