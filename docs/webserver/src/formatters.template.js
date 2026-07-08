  function usesDayClockAction() {
    return normalizeScreenSaverAction(S.day_idle_action) === "Clock";
  }

  function usesEveningClockAction() {
    return normalizeScreenSaverAction(S.night_idle_action) === "Clock";
  }

  function normalizeScreenSaverAction(value) {
    if (value === "Show Clock" || value === "Clock" || value === "On") return "Clock";
    if (value === "Turn Screen Off" || value === "Screen Off" || value === "Off") return "Screen Off";
    if (value === "Disabled") return "Disabled";
    return "Screen Off";
  }

  function screenSaverActionLabel(value) {
    return normalizeScreenSaverAction(value);
  }

  function hourOptions() {
    var options = [];
    for (var h = 0; h < 24; h++) options.push(h);
    return options;
  }

  function formatHour(value) {
    var h = Number(value);
    var suffix = h >= 12 ? "PM" : "AM";
    var hour = h % 12;
    if (hour === 0) hour = 12;
    return hour + ":00 " + suffix;
  }

  function normalizeDurationOption(value, options, fallback) {
    var n = Number(value);
    if (isNaN(n)) return fallback;
    var best = options[0];
    var bestDelta = Math.abs(n - best);
    options.forEach(function (option) {
      var delta = Math.abs(n - option);
      if (delta < bestDelta) {
        best = option;
        bestDelta = delta;
      }
    });
    return best;
  }

  function formatDurationSeconds(value) {
    var n = Number(value);
    if (n < 60) return n + " seconds";
    if (n === 60) return "1 minute";
    if (n < 3600) return Math.round(n / 60) + " minutes";
    return "1 hour";
  }

  function formatTrackInfoDuration(value) {
    var n = Number(value);
    return n === 0 ? "Always" : formatDurationSeconds(n);
  }

  function timezoneId(option) {
    var idx = String(option || "").indexOf(" (");
    return idx > 0 ? option.substring(0, idx) : String(option || "");
  }

  function formatGmtOffset(minutes) {
    var sign = minutes >= 0 ? "+" : "-";
    var abs = Math.abs(minutes);
    var h = Math.floor(abs / 60);
    var m = abs % 60;
    return "GMT" + sign + h + (m ? ":" + String(m).padStart(2, "0") : "");
  }

  function timezoneOffsetMinutes(tzId, date) {
    try {
      var parts = new Intl.DateTimeFormat("en-US", {
        timeZone: tzId,
        hourCycle: "h23",
        year: "numeric",
        month: "2-digit",
        day: "2-digit",
        hour: "2-digit",
        minute: "2-digit",
        second: "2-digit"
      }).formatToParts(date);
      var values = {};
      parts.forEach(function (part) {
        if (part.type !== "literal") values[part.type] = part.value;
      });
      var localAsUtc = Date.UTC(
        Number(values.year),
        Number(values.month) - 1,
        Number(values.day),
        Number(values.hour),
        Number(values.minute),
        Number(values.second)
      );
      return Math.round((localAsUtc - date.getTime()) / 60000);
    } catch (_) {
      return null;
    }
  }

  function formatTimezoneOption(option) {
    var tzId = timezoneId(option);
    var offset = timezoneOffsetMinutes(tzId, new Date());
    if (offset == null || !isFinite(offset)) return option;
    return tzId + " (" + formatGmtOffset(offset) + ")";
  }
