  function eid(domain, name) {
    return "/" + domain + "/" + encodeURIComponent(name);
  }

  function endpoint(key) {
    var e = ENTITIES[key];
    return eid(e.domain, e.name);
  }

  function slug(name) {
    return String(name || "")
      .toLowerCase()
      .replace(/[^a-z0-9]+/g, "_")
      .replace(/^_+|_+$/g, "");
  }

  var ID_TO_KEY = {};
  Object.keys(ENTITIES).forEach(function (key) {
    var e = ENTITIES[key];
    ID_TO_KEY[e.domain + "/" + e.name] = key;
    ID_TO_KEY[e.domain + "-" + slug(e.name)] = key;
    (e.fetchNames || []).forEach(function (name) {
      ID_TO_KEY[e.domain + "/" + name] = key;
      ID_TO_KEY[e.domain + "-" + slug(name)] = key;
    });
  });

  function eventId(d) {
    return (d && (d.name_id || d.id)) || "";
  }

  function safeGet(url) {
    return fetch(url, { cache: "no-store" })
      .then(function (r) {
        if (!r.ok) return null;
        return r.json();
      })
      .catch(function () {
        return null;
      });
  }

  function safeGetFirst(urls) {
    return Promise.all(urls.map(safeGet)).then(function (results) {
      for (var i = 0; i < results.length; i++) {
        if (results[i]) return results[i];
      }
      return null;
    });
  }

  function fetchUrlsForEntity(key) {
    var spec = ENTITIES[key];
    var names = [spec.name].concat(spec.fetchNames || []);
    var seen = {};
    return names.map(function (name) {
      var url = eid(spec.domain, name);
      if (spec.optionsKey) url += "?detail=all";
      return url;
    }).filter(function (url) {
      if (seen[url]) return false;
      seen[url] = true;
      return true;
    });
  }

  function post(url, params) {
    var fullUrl = params ? url + "?" + new URLSearchParams(params).toString() : url;
    return fetch(fullUrl, { method: "POST" }).then(function (r) {
      if (!r.ok) throw new Error("HTTP " + r.status);
      return r;
    }).catch(function (err) {
      console.error("POST " + fullUrl + " failed:", err);
      showBanner("Failed to save setting", "error");
      return null;
    });
  }

  function setInstalledVersion(value) {
    value = String(value == null ? "" : value).trim();
    if (!value) return;
    if (isSpecificFirmwareVersion(S.installed_version) && !isSpecificFirmwareVersion(value)) return;
    S.installed_version = value;
    S.update_available = firmwareUpdateAvailable();
  }

  function postQuiet(url) {
    return fetch(url, { method: "POST", keepalive: true }).catch(function () {
      return null;
    });
  }

  function isS3Display() {
    return S.device_profile === S3_DEVICE_PROFILE;
  }

  function isDeveloperExperimentalMode() {
    try {
      return new URLSearchParams(window.location.search).get("developer") === "experimental";
    } catch (_) {
      return false;
    }
  }

  function webActivityEndpoint(name) {
    return eid("button", name) + "/press";
  }

  function sendWebActivityHeartbeat() {
    if (!isS3Display()) return;
    webActivityStarted = true;
    webActivityClosed = false;
    postQuiet(webActivityEndpoint("Web Settings Heartbeat"));
  }

  function startWebActivityHeartbeat() {
    if (!isS3Display() || webActivityTimer) return;
    sendWebActivityHeartbeat();
    webActivityTimer = setInterval(sendWebActivityHeartbeat, WEB_ACTIVITY_HEARTBEAT_MS);
  }

  function stopWebActivityHeartbeat() {
    if (webActivityTimer) {
      clearInterval(webActivityTimer);
      webActivityTimer = null;
    }
    if (webActivityStarted && !webActivityClosed && isS3Display()) {
      webActivityClosed = true;
      postQuiet(webActivityEndpoint("Web Settings Closed"));
    }
  }

  function postText(url, value) {
    var body = new URLSearchParams();
    body.set("value", value == null ? "" : String(value));
    return fetch(url, {
      method: "POST",
      headers: { "Content-Type": "application/x-www-form-urlencoded" },
      body: body.toString()
    }).then(function (r) {
      if (!r.ok) throw new Error("HTTP " + r.status);
      return r;
    }).catch(function (err) {
      console.error("POST " + url + " failed:", err);
      showBanner("Failed to save setting", "error");
      return null;
    });
  }

  function applyEntityToState(key, data) {
    var spec = ENTITIES[key];
    if (!spec || !data) return;

    if (spec.firmwareVersion) {
      setInstalledVersion(data.state != null ? data.state : data.value);
      return;
    }

    if (spec.update) {
      S.firmware_state = String(data.state || "").trim().toUpperCase();
      setInstalledVersion(data.current_version || data.current || "");
      S.latest_version = data.latest_version || data.value || "";
      S.firmware_release_url = data.release_url || S.firmware_release_url || "";
      S.update_available = firmwareUpdateAvailable();
      if (S.firmware_state) S.firmware_checking = false;
      return;
    }

    if (spec.optionsKey && Array.isArray(data.option) && data.option.length) {
      S[spec.optionsKey] = data.option.slice();
    }

    var v = data.value != null ? data.value : data.state;
    if (spec.bool) {
      S[key] = v === true || v === "ON";
    } else if (spec.number) {
      var n = Number(v);
      if (!isNaN(n)) {
        S[key] = n;
        if (key === "speaker_panel_timeout" && n > 0) {
          lastSpeakerPanelTimeout = normalizeDurationOption(n, SPEAKER_PANEL_TIMEOUT_OPTIONS, DEFAULT_SPEAKER_PANEL_TIMEOUT);
        }
      }
    } else if (v != null) {
      S[key] = String(v);
    }

    if (key === "device_profile") {
      startWebActivityHeartbeat();
      if (S.device_profile !== lastPublicFirmwareProfile) {
        lastPublicFirmwareProfile = S.device_profile;
        refreshPublicFirmwareState().then(scheduleRender);
      }
    }
  }

  function fetchEntity(key) {
    var spec = ENTITIES[key];
    if (!spec || spec.skipFetch) return Promise.resolve();
    return safeGetFirst(fetchUrlsForEntity(key)).then(function (data) {
      if (data) applyEntityToState(key, data);
      return data;
    });
  }

  function fetchAllState() {
    return Promise.all(Object.keys(ENTITIES).map(fetchEntity));
  }

  function refreshFirmwareState() {
    return Promise.all([fetchEntity("firmware_update"), refreshPublicFirmwareState()]).then(function (results) {
      var data = results[0];
      if (!data && !results[1]) return;
      if (S.firmware_state !== "INSTALLING") stopFirmwareInstallRefresh();
      scheduleRender();
    });
  }

  function startFirmwareInstallRefresh() {
    stopFirmwareInstallRefresh();
    firmwareInstallRefreshStarted = Date.now();
    firmwareInstallRefreshTimer = setInterval(function () {
      if (Date.now() - firmwareInstallRefreshStarted > FIRMWARE_INSTALL_REFRESH_TIMEOUT_MS) {
        stopFirmwareInstallRefresh();
        return;
      }
      refreshFirmwareState();
    }, FIRMWARE_INSTALL_REFRESH_MS);
  }

  function stopFirmwareInstallRefresh() {
    if (!firmwareInstallRefreshTimer) return;
    clearInterval(firmwareInstallRefreshTimer);
    firmwareInstallRefreshTimer = null;
  }
