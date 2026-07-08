  function buildUI() {
    var root = el("div");
    root.id = "mp-app";

    var banner = el("div", "banner");
    banner.style.display = "none";
    root.appendChild(banner);
    els.banner = banner;

    buildHeader(root);
    buildPage(root, "settings");
    buildPage(root, "device");
    root.appendChild(buildSupportButton());

    var espApp = document.querySelector("esp-app");
    if (espApp) espApp.parentNode.insertBefore(root, espApp);
    else document.body.insertBefore(root, document.body.firstChild);

    els.root = root;
    switchTab("settings");
  }

  function buildSupportButton() {
    var link = document.createElement("a");
    link.className = "sp-support-btn";
    link.href = "https://www.buymeacoffee.com/jtenniswood";
    link.target = "_blank";
    link.rel = "noopener";
    link.innerHTML = '<img src="https://cdn.buymeacoffee.com/buttons/v2/default-yellow.png" alt="Buy Me A Coffee" height="60" style="border-radius:999px;">';
    return link;
  }

  function buildHeader(parent) {
    var header = el("div", "mp-header");
    var brand = el("div", "mp-brand");
    brand.textContent = "EspMedia";
    header.appendChild(brand);

    var nav = el("nav", "mp-nav");
    nav.setAttribute("aria-label", "Primary");
    [
      { id: "settings", label: "Settings" },
      { id: "device", label: "Device" }
    ].forEach(function (tab) {
      var node = el("div", "mp-tab");
      node.setAttribute("role", "tab");
      node.setAttribute("aria-selected", "false");
      node.textContent = tab.label;
      node.onclick = function () { switchTab(tab.id); };
      nav.appendChild(node);
      els["tab_" + tab.id] = node;
    });
    var docs = document.createElement("a");
    docs.className = "mp-tab mp-tab-docs";
    docs.href = "https://jtenniswood.github.io/esphome-media-player/";
    docs.target = "_blank";
    docs.rel = "noopener";
    docs.innerHTML = 'Docs <span class="mp-docs-icon">&#8599;</span>';
    nav.appendChild(docs);
    header.appendChild(nav);
    parent.appendChild(header);
  }

  function buildPage(parent, id) {
    var page = el("div", "mp-page");
    page.id = "mp-" + id;
    var wrap = el("div", "mp-wrap");
    page.appendChild(wrap);
    parent.appendChild(page);
    els[id + "Page"] = page;
    els[id + "Wrap"] = wrap;
  }

  function switchTab(tab) {
    currentTab = tab;
    ["settings", "device"].forEach(function (id) {
      els["tab_" + id].className = "mp-tab" + (id === tab ? " active" : "");
      els["tab_" + id].setAttribute("aria-selected", id === tab ? "true" : "false");
      els[id + "Page"].className = "mp-page" + (id === tab ? " active" : "");
    });
  }

  function scheduleRender() {
    if (isEditingSetting()) return;
    clearTimeout(renderTimer);
    renderTimer = setTimeout(renderAll, 120);
  }

  function renderAll() {
    renderTimer = null;
    renderSettings();
    renderDevice();
    switchTab(currentTab);
  }

  function renderSettings() {
    var wrap = els.settingsWrap;
    wrap.innerHTML = "";
    var content = el("div");

    content.appendChild(setupCard());
    content.appendChild(advancedCard());
    content.appendChild(playbackCard());
    content.appendChild(volumeCard());
    content.appendChild(idleScreenCard());
    content.appendChild(screenSaverCard());
    content.appendChild(nightScheduleCard());
    if (isDeveloperExperimentalMode()) content.appendChild(developerCard());

    wrap.appendChild(content);
  }

  function setupCard() {
    var body = el("div");
    body.appendChild(textField("Media Player", "media_player", "media_player.living_room", validateMediaPlayer));
    return card("Media Player", body, true);
  }

  function advancedCard() {
    var body = el("div");
    var linkedHint = el("div", "field-hint");
    linkedHint.style.fontSize = ".9rem";
    linkedHint.style.lineHeight = "1.45";
    linkedHint.textContent = "Optional secondary media entity, for use when your speaker has line in or hdmi in.";
    body.appendChild(linkedHint);
    body.appendChild(textField("Linked Media Player", "linked_media_player", "media_player.apple_tv", validateMediaPlayer));
    return card("Advanced", body, true);
  }

  function playbackCard() {
    var body = el("div");
    body.appendChild(toggleField("Track Clock", "show_remaining_time", null, trackClockModeText));
    body.appendChild(toggleField("Show Progress Bar", "show_progress_bar"));
    if (supportsTrackInfoDuration()) {
      body.appendChild(toggleField("Auto-Show Track Info", "auto_show_track_info"));
      body.appendChild(durationSelectField("Track Info Duration", "track_info_duration", TRACK_INFO_DURATION_OPTIONS, formatTrackInfoDuration));
    }
    return card("Playback", body, true);
  }

  function volumeCard() {
    var body = el("div");
    var timerWrap = el("div");
    var enabled = Number(S.speaker_panel_timeout) > 0;
    var badge = badgeFor(enabled);
    timerWrap.style.display = enabled ? "" : "none";
    body.appendChild(localToggleField("Speaker Panel Auto-Close", enabled, function (next) {
      var value = next
        ? normalizeDurationOption(lastSpeakerPanelTimeout || DEFAULT_SPEAKER_PANEL_TIMEOUT, SPEAKER_PANEL_TIMEOUT_OPTIONS, DEFAULT_SPEAKER_PANEL_TIMEOUT)
        : 0;
      S.speaker_panel_timeout = value;
      if (value > 0) lastSpeakerPanelTimeout = value;
      badge.className = "on-badge" + (value > 0 ? " active" : "");
      post(endpoint("speaker_panel_timeout") + "/set", { value: value }).then(renderAll);
    }));
    timerWrap.appendChild(durationSelectField("Timer", "speaker_panel_timeout", SPEAKER_PANEL_TIMEOUT_OPTIONS));
    body.appendChild(timerWrap);
    return card("Volume", body, true, badge);
  }

  function trackClockModeText() {
    return S.show_remaining_time ? "Time remaining" : "Track length";
  }

  function idleScreenCard() {
    var badge = badgeFor(S.paused_dimming_enabled);
    var body = el("div");
    var details = el("div");
    details.style.display = S.paused_dimming_enabled ? "" : "none";
    body.appendChild(sectionDescription("When playback is paused."));
    body.appendChild(toggleField("Dim when idle", "paused_dimming_enabled", null, null, function (enabled) {
      details.style.display = enabled ? "" : "none";
      badge.className = "on-badge" + (enabled ? " active" : "");
    }));
    details.appendChild(durationSelectField("Dim After", "dim_timeout", [5, 10, 30, 60, 120, 300, 600]));
    details.appendChild(rangeField("Day Dimmed Brightness", "day_dim_brightness"));
    details.appendChild(rangeField("Night Dimmed Brightness", "night_dim_brightness"));
    body.appendChild(details);
    return card("Idle Screen", body, true, badge);
  }

  function screenSaverCard() {
    var badge = badgeFor(S.screen_saver_enabled);
    var body = el("div");
    var details = el("div");
    details.style.display = S.screen_saver_enabled ? "" : "none";
    body.appendChild(sectionDescription("When playback is paused and the device has been idle for a while."));
    body.appendChild(toggleField("Screen Saver", "screen_saver_enabled", null, null, function (enabled) {
      details.style.display = enabled ? "" : "none";
      badge.className = "on-badge" + (enabled ? " active" : "");
    }));
    details.appendChild(durationSelectField("Start Screen Saver After", "screen_saver_timeout", [10, 30, 60, 120, 300, 600, 1800]));
    details.appendChild(screenSaverActionField("Daytime Screen Saver", "day_idle_action", function () {
      renderAll();
    }));
    var dayDetails = el("div");
    dayDetails.style.display = usesDayClockAction() ? "" : "none";
    dayDetails.appendChild(rangeField("Day Clock Brightness", "day_clock_brightness"));
    dayDetails.appendChild(el("div", "spacer-8"));
    details.appendChild(dayDetails);
    details.appendChild(screenSaverActionField("Evening Screen Saver", "night_idle_action", function () {
      renderAll();
    }));
    var eveningDetails = el("div");
    eveningDetails.style.display = usesEveningClockAction() ? "" : "none";
    eveningDetails.appendChild(rangeField("Evening Clock Brightness", "evening_clock_brightness"));
    details.appendChild(eveningDetails);
    body.appendChild(details);
    return card("Screen Saver", body, true, badge);
  }

  function nightScheduleCard() {
    var badge = badgeFor(S.schedule_enabled);
    var body = el("div");
    body.appendChild(sectionDescription("Configure overnight device behaviour."));
    body.appendChild(toggleField("Schedule Screen Off", "schedule_enabled", null, null, function (enabled) {
      details.style.display = enabled ? "" : "none";
      badge.className = "on-badge" + (enabled ? " active" : "");
    }));

    var details = el("div");
    details.style.display = S.schedule_enabled ? "" : "none";
    details.appendChild(hourSelectField("On Time", "schedule_on_hour"));
    details.appendChild(hourSelectField("Off Time", "schedule_off_hour"));
    details.appendChild(durationSelectField("When Woken, Idle Time To Screen Off", "schedule_wake_timeout"));
    body.appendChild(details);
    return card("Night Schedule", body, true, badge);
  }

  function developerCard() {
    var badge = badgeFor(S.developer_experimental_features);
    var body = el("div");
    body.appendChild(toggleField("Developer/Experimental Features", "developer_experimental_features", null, null, function (enabled) {
      badge.className = "on-badge" + (enabled ? " active" : "");
    }));
    return card("Developer", body, true, badge);
  }

  function screenBrightnessCard() {
    var body = el("div");
    body.appendChild(rangeField("Day Active Brightness", "day_active_brightness"));
    body.appendChild(rangeField("Night Active Brightness", "night_active_brightness"));
    return card("Screen Brightness", body, true);
  }

  function sectionDescription(text) {
    var description = el("p", "field-hint");
    description.style.fontSize = ".9rem";
    description.style.lineHeight = "1.45";
    description.style.marginTop = "-2px";
    description.style.marginBottom = "18px";
    description.textContent = text;
    return description;
  }

  function dayNightCard() {
    var body = el("div");
    body.appendChild(textField("Day/Night Source", "day_night_sensor", "binary_sensor.daytime", validateDayNightSensor));
    return card("Day/Night", body, true);
  }

  function screenToneCard() {
    var body = el("div");
    body.appendChild(rangeField("Day Screen Warmth", "screen_warmth_day"));
    body.appendChild(rangeField("Night Screen Warmth", "screen_warmth_night"));
    return card("Screen Tone", body, true);
  }

  function firmwareCard() {
    var body = el("div", "fw-body");
    var versionRow = el("div", "fw-row");
    var version = el("span", "fw-label");
    var installed = displayVersion(S.installed_version || "");
    version.innerHTML = '<span style="color:var(--text2)">Installed </span>' + esc(installed || "Dev");
    var checkWrap = el("div", "check-wrap");
    var status = el("span", "fw-status");
    status.innerHTML = firmwareInlineStatusText();
    var check = el("button", "btn btn-secondary btn-sm");
    check.textContent = firmwareButtonText();
    check.disabled = S.firmware_checking || S.firmware_state === "INSTALLING";
    check.onclick = function () {
      if (firmwareUpdateAvailable()) {
        installFirmwareUpdate();
        return;
      }
      S.firmware_checking = true;
      renderAll();
      post(endpoint("check_latest") + "/press");
      refreshPublicFirmwareState();
      setTimeout(function () {
        S.firmware_checking = false;
        refreshFirmwareState().then(renderAll);
      }, 10000);
    };
    checkWrap.appendChild(status);
    checkWrap.appendChild(check);
    versionRow.appendChild(version);
    versionRow.appendChild(checkWrap);
    body.appendChild(versionRow);

    var detail = firmwareDetailText();
    if (detail) {
      var detailNode = el("div", "fw-status");
      detailNode.innerHTML = detail;
      body.appendChild(detailNode);
    }

    var frequencyWrap = el("div");
    frequencyWrap.style.display = S.auto_update ? "" : "none";
    body.appendChild(toggleField("Auto Update", "auto_update", null, null, function (enabled) {
      frequencyWrap.style.display = enabled ? "" : "none";
    }));
    frequencyWrap.appendChild(selectField("Update Frequency", "update_frequency"));
    body.appendChild(frequencyWrap);
    return card("Firmware", body, true);
  }

  function renderDevice() {
    var wrap = els.deviceWrap;
    wrap.innerHTML = "";
    wrap.appendChild(clockCard());
    wrap.appendChild(dayNightCard());
    wrap.appendChild(screenBrightnessCard());
    if (supportsScreenTone()) wrap.appendChild(screenToneCard());
    if (supportsScreenRotation()) wrap.appendChild(rotationCard());
    wrap.appendChild(firmwareCard());
  }

  function clockCard() {
    var body = el("div");
    body.appendChild(segmentedSelectField("Clock Format", "clock_time_format"));
    body.appendChild(selectField("Timezone", "clock_timezone"));
    return card("Clock", body, true);
  }

  function rotationCard() {
    var body = el("div");
    body.appendChild(selectField("Screen Rotation", "screen_rotation"));
    return card("Rotation", body, true);
  }
