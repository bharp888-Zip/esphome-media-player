  function textField(label, key, placeholder, validator) {
    var f = field(label);
    var group = el("div", "input-group");
    var input = document.createElement("input");
    input.type = "text";
    input.value = S[key] || "";
    input.placeholder = placeholder || "";
    input.maxLength = 100;
    var save = el("button", "btn btn-primary");
    save.type = "button";
    save.textContent = "Save";
    var error = el("div", "field-error");
    save.onclick = function () {
      var value = input.value.trim();
      var msg = validator ? validator(value) : "";
      if (msg) {
        error.textContent = msg;
        return;
      }
      error.textContent = "";
      save.disabled = true;
      save.textContent = "Saving...";
      S[key] = value;
      postText(endpoint(key) + "/set", value).then(function (res) {
        save.disabled = false;
        save.textContent = "Save";
        if (res) showBanner("Saved", "success");
      });
    };
    group.appendChild(input);
    group.appendChild(save);
    f.appendChild(group);
    f.appendChild(error);
    return f;
  }

  function validateMediaPlayer(value) {
    if (!value) return "";
    return value.indexOf("media_player.") === 0 ? "" : "Use a media_player entity.";
  }

  function validateDayNightSensor(value) {
    if (!value) return "";
    if (value.indexOf("binary_sensor.") === 0 || value.indexOf("input_boolean.") === 0) return "";
    return "Use a binary_sensor or input_boolean entity.";
  }

  function toggleField(label, key, hint, modeText, onChange) {
    var f = field("");
    var row = el("div", "toggle-row");
    var text = el("span");
    text.textContent = label;
    var tog = el("div", S[key] ? "toggle on" : "toggle");
    var control = el("div", "toggle-control");
    var mode = modeText ? el("span", "toggle-mode") : null;
    if (mode) mode.textContent = modeText();
    tog.onclick = function () {
      S[key] = !S[key];
      tog.className = S[key] ? "toggle on" : "toggle";
      if (mode) mode.textContent = modeText();
      if (onChange) onChange(S[key]);
      post(endpoint(key) + (S[key] ? "/turn_on" : "/turn_off"));
    };
    row.appendChild(text);
    if (mode) control.appendChild(mode);
    control.appendChild(tog);
    row.appendChild(control);
    f.appendChild(row);
    if (hint) {
      var help = el("div", "field-hint");
      help.textContent = hint;
      f.appendChild(help);
    }
    return f;
  }

  function localToggleField(label, enabled, onChange) {
    var f = field("");
    var row = el("div", "toggle-row");
    var text = el("span");
    text.textContent = label;
    var tog = el("div", enabled ? "toggle on" : "toggle");
    tog.onclick = function () {
      enabled = !enabled;
      tog.className = enabled ? "toggle on" : "toggle";
      onChange(enabled);
    };
    row.appendChild(text);
    row.appendChild(tog);
    f.appendChild(row);
    return f;
  }

  function hourSelectField(label, key) {
    var f = field(label);
    f.appendChild(selectFromOptions(hourOptions(), clampNumber(Math.round(S[key]), 0, 23), function (value) {
      S[key] = Number(value);
      post(endpoint(key) + "/set", { value: S[key] });
    }, formatHour));
    return f;
  }

  function durationSelectField(label, key, options, formatter) {
    options = options || [10, 30, 60, 120, 300, 600, 1800, 3600];
    var value = normalizeDurationOption(S[key], options, 60);
    var f = field(label);
    f.appendChild(selectFromOptions(options, value, function (next) {
      S[key] = Number(next);
      if (key === "speaker_panel_timeout" && S[key] > 0) lastSpeakerPanelTimeout = S[key];
      post(endpoint(key) + "/set", { value: S[key] });
    }, formatter || formatDurationSeconds));
    return f;
  }

  function screenSaverActionField(label, key, onChange) {
    var options = supportsClockScreenSaver() ? ["Clock", "Screen Off", "Disabled"] : ["Screen Off", "Disabled"];
    var selected = normalizeScreenSaverAction(S[key]);
    if (options.indexOf(selected) === -1) selected = "Screen Off";
    var f = field(label);
    f.appendChild(selectFromOptions(options, selected, function (next) {
      S[key] = next;
      post(endpoint(key) + "/set", { option: next });
      if (onChange) onChange(next);
    }, screenSaverActionLabel));
    return f;
  }

  function selectFromOptions(options, selected, onChange, formatter) {
    var select = document.createElement("select");
    select.className = "select";
    options.forEach(function (value) {
      var opt = document.createElement("option");
      opt.value = value;
      opt.textContent = formatter ? formatter(value) : value;
      if (Number(value) === Number(selected) || value === selected) opt.selected = true;
      select.appendChild(opt);
    });
    select.onchange = function () {
      onChange(select.value);
    };
    return select;
  }

  function rangeField(label, key) {
    var spec = NUMBER_LIMITS[key];
    var f = field(label);
    var row = el("div", "range-wrap");
    var input = document.createElement("input");
    input.type = "range";
    input.min = spec.min;
    input.max = spec.max;
    input.step = spec.step;
    input.value = clampNumber(S[key], spec.min, spec.max);
    var value = el("span", "range-val");
    value.textContent = input.value + spec.suffix;
    input.oninput = function () {
      value.textContent = input.value + spec.suffix;
    };
    input.onchange = function () {
      S[key] = Number(input.value);
      post(endpoint(key) + "/set", { value: input.value });
    };
    row.appendChild(input);
    row.appendChild(value);
    f.appendChild(row);
    return f;
  }

  function selectField(label, key, onChange) {
    var f = field(label);
    var options = (S[key + "_options"] || []).slice();
    if ((key === "day_idle_action" || key === "night_idle_action") && !supportsClockScreenSaver()) {
      options = options.filter(function (option) { return normalizeScreenSaverAction(option) !== "Clock"; });
      if (normalizeScreenSaverAction(S[key]) === "Clock") S[key] = "Screen Off";
    }
    if (options.indexOf(S[key]) === -1 && S[key]) options.unshift(S[key]);
    if (!options.length) options.push(S[key] || "");
    var select = document.createElement("select");
    select.className = "select";
    options.forEach(function (option) {
      var opt = document.createElement("option");
      opt.value = option;
      opt.textContent = key === "clock_timezone" ? formatTimezoneOption(option) : option;
      if (option === S[key]) opt.selected = true;
      select.appendChild(opt);
    });
    select.onchange = function () {
      S[key] = select.value;
      post(endpoint(key) + "/set", { option: select.value });
      if (onChange) onChange(select.value);
    };
    f.appendChild(select);
    return f;
  }

  function segmentedSelectField(label, key, onChange) {
    var f = field(label);
    var options = (S[key + "_options"] || []).slice();
    if (options.indexOf(S[key]) === -1 && S[key]) options.unshift(S[key]);
    if (!options.length) options.push(S[key] || "");
    var group = el("div", "segmented");
    group.setAttribute("role", "tablist");
    options.forEach(function (option) {
      var button = el("button", "segmented-option" + (option === S[key] ? " active" : ""));
      button.type = "button";
      button.setAttribute("role", "tab");
      button.setAttribute("aria-selected", option === S[key] ? "true" : "false");
      button.textContent = option;
      button.onclick = function () {
        S[key] = option;
        Array.prototype.forEach.call(group.children, function (child) {
          var active = child.textContent === option;
          child.className = "segmented-option" + (active ? " active" : "");
          child.setAttribute("aria-selected", active ? "true" : "false");
        });
        post(endpoint(key) + "/set", { option: option });
        if (onChange) onChange(option);
      };
      group.appendChild(button);
    });
    f.appendChild(group);
    return f;
  }

  function field(labelText) {
    var f = el("div", "field");
    if (labelText) {
      var l = document.createElement("label");
      l.textContent = labelText;
      f.appendChild(l);
    }
    return f;
  }

  function card(title, bodyElement, defaultCollapsed, badge) {
    var c = el("div", "card");
    var cardKey = slug(title);
    var header = el("div", "card-header");
    var h = document.createElement("h3");
    h.textContent = title;
    var right = el("div", "card-header-right");
    if (badge) right.appendChild(badge);
    var chevron = el("span", "card-chevron");
    chevron.innerHTML = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><path d="M6 9l6 6 6-6"/></svg>';
    right.appendChild(chevron);
    header.appendChild(h);
    header.appendChild(right);
    var body = el("div", "card-body");
    body.appendChild(bodyElement);
    c.appendChild(header);
    c.appendChild(body);
    var collapsed = cardCollapsed.hasOwnProperty(cardKey) ? cardCollapsed[cardKey] : defaultCollapsed;
    if (collapsed) c.classList.add("collapsed");
    header.onclick = function (ev) {
      if (/^(INPUT|SELECT|TEXTAREA|BUTTON)$/.test(ev.target.tagName)) return;
      c.classList.toggle("collapsed");
      cardCollapsed[cardKey] = c.classList.contains("collapsed");
    };
    return c;
  }

  function badgeFor(active, text) {
    var b = el("span", "on-badge" + (active ? " active" : ""));
    b.textContent = text || "On";
    return b;
  }

  function clampNumber(value, min, max) {
    var n = Number(value);
    if (isNaN(n)) n = min;
    if (n < min) n = min;
    if (n > max) n = max;
    return n;
  }
