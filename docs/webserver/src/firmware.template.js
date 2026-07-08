  function isSpecificFirmwareVersion(version) {
    var value = String(version == null ? "" : version).trim().toLowerCase();
    return !!value && value !== "dev" && value !== "0.0.0";
  }

  function firmwareVersionsSame(a, b) {
    return String(a == null ? "" : a).trim().toLowerCase() ===
      String(b == null ? "" : b).trim().toLowerCase();
  }

  function firmwareManifestSlug() {
    var profile = String(S.device_profile || "").trim();
    return FIRMWARE_MANIFEST_SLUGS[profile] || "";
  }

  function publicFirmwareManifestUrl() {
    var manifestSlug = firmwareManifestSlug();
    return manifestSlug ? FIRMWARE_PUBLIC_MANIFEST_BASE + encodeURIComponent(manifestSlug) + "/manifest.json" : "";
  }

  function firmwareInfoFromPublicManifest(data) {
    if (!data || typeof data !== "object") return null;
    var version = String(data.version || "").trim();
    if (!isSpecificFirmwareVersion(version)) return null;
    var builds = Array.isArray(data.builds) ? data.builds : [];
    for (var i = 0; i < builds.length; i++) {
      var ota = (builds[i] || {}).ota || {};
      if (!ota.path) continue;
      return {
        latest_version: version,
        release_url: String(ota.release_url || "").trim()
      };
    }
    return null;
  }

  function setPublicFirmwareInfo(info) {
    if (!info) return false;
    var latest = String(info.latest_version || "").trim();
    if (!isSpecificFirmwareVersion(latest)) return false;
    S.latest_version = latest;
    if (info.release_url) S.firmware_release_url = info.release_url;
    S.update_available = firmwareUpdateAvailable();
    return true;
  }

  function refreshPublicFirmwareState() {
    var url = publicFirmwareManifestUrl();
    if (!url) return Promise.resolve(false);
    return safeGet(url).then(function (data) {
      return setPublicFirmwareInfo(firmwareInfoFromPublicManifest(data));
    });
  }

  function installedFirmwareMatchesPublicRelease() {
    return isSpecificFirmwareVersion(S.installed_version) &&
      isSpecificFirmwareVersion(S.latest_version) &&
      firmwareVersionsSame(S.installed_version, S.latest_version);
  }

  function publicFirmwareUpdateAvailable() {
    return isSpecificFirmwareVersion(S.latest_version) && !installedFirmwareMatchesPublicRelease();
  }

  function deviceFirmwareUpdateAvailable() {
    return S.firmware_state === "UPDATE AVAILABLE" && isSpecificFirmwareVersion(S.latest_version);
  }

  function firmwareUpdateAvailable() {
    return deviceFirmwareUpdateAvailable() || publicFirmwareUpdateAvailable();
  }

  function installFirmwareUpdate() {
    if (deviceFirmwareUpdateAvailable()) {
      S.firmware_state = "INSTALLING";
      renderAll();
      startFirmwareInstallRefresh();
      post(endpoint("firmware_update") + "/install");
      return;
    }

    S.firmware_checking = true;
    renderAll();
    post(endpoint("check_latest") + "/press");
    refreshPublicFirmwareState();
    setTimeout(function () {
      S.firmware_checking = false;
      fetchEntity("firmware_update").then(function () {
        if (deviceFirmwareUpdateAvailable()) {
          S.firmware_state = "INSTALLING";
          renderAll();
          startFirmwareInstallRefresh();
          post(endpoint("firmware_update") + "/install");
          return;
        }
        renderAll();
      });
    }, 10000);
  }

  function firmwareInlineStatusText() {
    if (S.firmware_state === "INSTALLING") return "Installing...";
    if (S.firmware_checking) return "Checking...";
    if (firmwareUpdateAvailable()) return "";
    if (S.firmware_state === "NO UPDATE" || S.firmware_state === "UP_TO_DATE") return "Up to date";
    if (installedFirmwareMatchesPublicRelease()) return "Up to date";
    return "";
  }

  function firmwareDetailText() {
    if (S.firmware_state === "INSTALLING") return "Installing update...";
    if (firmwareUpdateAvailable()) {
      var text = "Latest public version: " + esc(displayVersion(S.latest_version));
      if (S.firmware_release_url) {
        text += ' <a href="' + escAttr(S.firmware_release_url) + '" target="_blank" rel="noopener">release notes</a>';
      }
      return text;
    }
    if (S.firmware_checking) return "Checking public firmware...";
    return "";
  }

  function firmwareButtonText() {
    if (S.firmware_state === "INSTALLING") return "Installing...";
    if (firmwareUpdateAvailable()) return "Install Update";
    return S.firmware_checking ? "Checking..." : "Check for Update";
  }
