  function displayVersion(value) {
    var v = String(value || "").trim();
    if (!v) return "";
    return v.toLowerCase() === "dev" ? "Dev" : v;
  }

  function escAttr(s) {
    return esc(s).replace(/"/g, "&quot;");
  }

  function isEditingSetting() {
    var active = document.activeElement;
    if (!active || !els.root || !els.root.contains(active)) return false;
    return /^(INPUT|SELECT|TEXTAREA|BUTTON)$/.test(active.tagName);
  }

  function el(tag, cls) {
    var e = document.createElement(tag);
    if (cls) e.className = cls;
    return e;
  }

  function esc(s) {
    var d = document.createElement("div");
    d.textContent = s == null ? "" : String(s);
    return d.innerHTML;
  }

  var bannerTimer = null;
  function showBanner(message, type) {
    if (!els.banner) return;
    els.banner.textContent = message;
    els.banner.className = "banner banner-" + (type || "success");
    els.banner.style.display = "";
    clearTimeout(bannerTimer);
    bannerTimer = setTimeout(function () {
      els.banner.style.display = "none";
    }, 3500);
  }

  var ANSI_LEVEL = {
    "1;31": "log-error",
    "0;31": "log-error",
    "0;33": "log-warn",
    "0;32": "log-info",
    "0;35": "log-config",
    "0;36": "log-debug",
    "0;37": "log-verbose"
  };
  var ANSI_RE = /\033\[[\d;]*m/g;

  function appendLog(msg, lvl) {
    if (!els.logOutput) return;
    var line = document.createElement("div");
    line.className = "log-line";
    var text = String(msg || "");
    var match = text.match(/\033\[([\d;]+)m/);
    var cls = match ? ANSI_LEVEL[match[1]] : "";
    if (cls) line.classList.add(cls);
    else if (lvl === 1) line.classList.add("log-error");
    else if (lvl === 2) line.classList.add("log-warn");
    else if (lvl === 3) line.classList.add("log-info");
    else if (lvl === 4) line.classList.add("log-config");
    else if (lvl === 5) line.classList.add("log-debug");
    else if (lvl >= 6) line.classList.add("log-verbose");
    line.textContent = text.replace(ANSI_RE, "");
    var atBottom = els.logOutput.scrollHeight - els.logOutput.scrollTop - els.logOutput.clientHeight < 40;
    els.logOutput.appendChild(line);
    var overflow = els.logOutput.childNodes.length - 1000;
    for (var i = 0; i < overflow; i++) els.logOutput.removeChild(els.logOutput.firstChild);
    if (atBottom) els.logOutput.scrollTop = els.logOutput.scrollHeight;
  }

  function initSSE() {
    try {
      evtSource = new EventSource("/events");
      evtSource.addEventListener("open", function () {
        refreshFirmwareState();
      });
      evtSource.addEventListener("state", function (e) {
        try {
          var data = JSON.parse(e.data);
          var key = ID_TO_KEY[eventId(data)];
          if (!key) return;
          applyEntityToState(key, data);
          scheduleRender();
        } catch (_) {}
      });
      evtSource.addEventListener("log", function (e) {
        var data;
        try { data = JSON.parse(e.data); } catch (_) { data = { msg: e.data }; }
        appendLog(data.msg || e.data, data.lvl);
      });
    } catch (_) {}
  }
