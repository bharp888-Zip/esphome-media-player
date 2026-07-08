(function () {
  "use strict";

  var CSS = __MEDIA_PLAYER_CSS__;

  var viewport = document.querySelector('meta[name="viewport"]');
  if (!viewport) {
    viewport = document.createElement("meta");
    viewport.name = "viewport";
    document.head.appendChild(viewport);
  }
  viewport.content = "width=device-width, initial-scale=1";

  var style = document.createElement("style");
  style.textContent = CSS;
  document.head.appendChild(style);

  var fonts = document.createElement("link");
  fonts.rel = "stylesheet";
  fonts.href = "https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap";
  document.head.appendChild(fonts);

  var faviconSvg = "<svg xmlns=\"http://www.w3.org/2000/svg\" viewBox=\"0 0 24 24\"><path fill=\"#5c73e7\" d=\"M12,3L2,12H5V20H19V12H22L12,3M12,8.5C14.34,8.5 16.46,9.43 18,10.94L16.8,12.12C15.58,10.91 13.88,10.17 12,10.17C10.12,10.17 8.42,10.91 7.2,12.12L6,10.94C7.54,9.43 9.66,8.5 12,8.5M12,11.83C13.4,11.83 14.67,12.39 15.6,13.3L14.4,14.47C13.79,13.87 12.94,13.5 12,13.5C11.06,13.5 10.21,13.87 9.6,14.47L8.4,13.3C9.33,12.39 10.6,11.83 12,11.83M12,15.17C12.94,15.17 13.7,15.91 13.7,16.83C13.7,17.75 12.94,18.5 12,18.5C11.06,18.5 10.3,17.75 10.3,16.83C10.3,15.91 11.06,15.17 12,15.17Z\"/></svg>";
  var favicon = document.createElement("link");
  favicon.rel = "icon";
  favicon.type = "image/svg+xml";
  favicon.href = "data:image/svg+xml," + encodeURIComponent(faviconSvg);
  document.head.appendChild(favicon);

  var SETTING_OPTIONS = __WEB_SETTING_OPTIONS__;
  var SPEAKER_PANEL_TIMEOUT_OPTIONS = SETTING_OPTIONS.speaker_panel_timeout;
  var TRACK_INFO_DURATION_OPTIONS = SETTING_OPTIONS.track_info_duration;
  var WEB_DEVICE_PROFILES = __WEB_DEVICE_PROFILES__;
  var WEB_ACTIVITY_HEARTBEAT_MS = 10000;
  var FIRMWARE_INSTALL_REFRESH_MS = 5000;
  var FIRMWARE_INSTALL_REFRESH_TIMEOUT_MS = 300000;
  var FIRMWARE_PUBLIC_MANIFEST_BASE = "https://jtenniswood.github.io/esphome-media-player/firmware/";
  var FIRMWARE_MANIFEST_SLUGS = __FIRMWARE_MANIFEST_SLUGS__;
  var DEFAULT_SPEAKER_PANEL_TIMEOUT = __DEFAULT_SPEAKER_PANEL_TIMEOUT__;

__SETTINGS_SCHEMA__

__DEVICE_PROFILE_HELPERS__

  var els = {};
  var currentTab = "settings";
  var renderTimer = null;
  var evtSource = null;
  var cardCollapsed = {};
  var lastSpeakerPanelTimeout = DEFAULT_SPEAKER_PANEL_TIMEOUT;
  var webActivityTimer = null;
  var webActivityStarted = false;
  var webActivityClosed = false;
  var firmwareInstallRefreshTimer = null;
  var firmwareInstallRefreshStarted = 0;
  var lastPublicFirmwareProfile = "";

__API_HELPERS__

__APP_UI__

__UI_FORMATTERS__

__UI_CONTROLS__

__FIRMWARE_HELPERS__

__APP_RUNTIME_HELPERS__

  buildUI();
  renderAll();
  fetchAllState().then(function () {
    return refreshPublicFirmwareState();
  }).then(function () {
    renderAll();
    startWebActivityHeartbeat();
  });
  initSSE();
  window.addEventListener("pagehide", stopWebActivityHeartbeat);
  window.addEventListener("beforeunload", stopWebActivityHeartbeat);
})();
