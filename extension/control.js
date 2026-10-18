"use strict";

const HOST_NAME = "foxbook_control";
const RESPONSE_TIMEOUT_MS = 10_000;
const UPDATE_TIMEOUT_MS = 40_000;
const SYNC_TIMEOUT_MS = 910_000;
const buttons = [...document.querySelectorAll("button[data-action]")];
const logoutButton = document.getElementById("cage-logout");
const status = document.getElementById("status");
const output = document.getElementById("output");
const errorCode = document.getElementById("error-code");
const volumeSlider = document.getElementById("volume-slider");
const volumeValue = document.getElementById("volume-value");
const brightnessSlider = document.getElementById("brightness-slider");
const brightnessValue = document.getElementById("brightness-value");
let currentRequest = 0;
let confirmedVolume = null;
let confirmedBrightness = null;

function showResult(message, text = "", code = "") {
  status.textContent = message;
  output.textContent = text;
  output.hidden = !text;
  errorCode.textContent = code;
  errorCode.hidden = !code;
}

function showVolume(value) {
  volumeSlider.value = Math.min(100, Math.max(0, value));
  volumeValue.textContent = `${value}%`;
}

function readVolume(text) {
  const match = /^Volume:\s*(\d+(?:\.\d+)?)/m.exec(text);
  if (!match) return false;
  const value = Math.round(Number(match[1]) * 100);
  if (!Number.isFinite(value)) return false;
  confirmedVolume = value;
  showVolume(value);
  return true;
}

function showBrightness(value) {
  brightnessSlider.value = Math.min(100, Math.max(1, value));
  brightnessValue.textContent = `${value}%`;
}

function readBrightness(text) {
  const match = /^[^,\r\n]+,backlight,\d+,(\d+)%,\d+\s*$/.exec(text.trim());
  if (!match) return false;
  const value = Number(match[1]);
  if (!Number.isInteger(value) || value < 0 || value > 100) return false;
  confirmedBrightness = value;
  showBrightness(value);
  return true;
}

function requestStatus(action, request = { action }) {
  const isUpdate = action === "update_host";
  const isSync = action === "sync_score";
  const isSet = action === "set_volume" || action === "set_brightness";
  if (isUpdate && !window.confirm("更新元のリポジトリからNative Hostを再インストールします。続けますか？")) return;
  const requestId = ++currentRequest;
  const label = action === "set_volume" ? "音量" : action === "set_brightness" ? "輝度" : buttons.find((button) => button.dataset.action === action).textContent.trim();
  buttons.forEach((button) => { button.disabled = true; });
  volumeSlider.disabled = true;
  brightnessSlider.disabled = true;
  showResult(isUpdate ? "Native Hostを更新中…" : isSync ? "Dropboxから楽譜を同期中…" : isSet ? `${label}を変更中…` : `${label}を取得中…`);

  let timer;
  const timeout = new Promise((_, reject) => {
    timer = setTimeout(() => reject(new Error("応答待機が時間内に完了しませんでした")), isSync ? SYNC_TIMEOUT_MS : isUpdate ? UPDATE_TIMEOUT_MS : RESPONSE_TIMEOUT_MS);
  });

  return Promise.race([
    browser.runtime.sendNativeMessage(HOST_NAME, request),
    timeout,
  ]).then((response) => {
    if (requestId !== currentRequest) return;
    if (!response || typeof response.success !== "boolean" || typeof response.output !== "string") {
      showResult("システム機能から正しい応答を受け取れませんでした。", "", "HOST_UNAVAILABLE");
    } else if (response.success && response.error === null) {
      if (action === "audio_status" && !readVolume(response.output)) {
        showResult("音量の取得結果を読み取れませんでした。", response.output, "COMMAND_FAILED");
      } else if ((action === "brightness_status" || action === "set_brightness") && !readBrightness(response.output)) {
        showResult("輝度の取得結果を読み取れませんでした。輝度ボタンで再取得してください。", "", "COMMAND_FAILED");
      } else if (action === "set_brightness") {
        showResult("輝度を変更しました。", `${confirmedBrightness}%`);
      } else if (action === "set_volume") {
        confirmedVolume = request.volume;
        showVolume(confirmedVolume);
        showResult("音量を変更しました。", `${confirmedVolume}%`);
      } else {
        showResult(isUpdate ? "Native Hostを更新しました。" : isSync ? "楽譜の同期が完了しました。" : `${label}を取得しました。`, response.output);
      }
    } else if (!response.success && response.error && typeof response.error.code === "string" && typeof response.error.message === "string") {
      const message = (isSet || action === "brightness_status") && ["INVALID_REQUEST", "UNKNOWN_ACTION"].includes(response.error.code)
        ? "Native Hostが古い可能性があります。Hostを更新してください。"
        : response.error.message;
      showResult(message, "", response.error.code);
    } else {
      showResult("システム機能から正しい応答を受け取れませんでした。", "", "HOST_UNAVAILABLE");
    }
  }).catch((error) => {
    if (requestId !== currentRequest) return;
    console.error("Native Messaging エラー:", error);
    const message = error.message === "応答待機が時間内に完了しませんでした"
      ? "システム機能から応答がありません。"
      : "システム機能に接続できません。";
    showResult(message, "", "HOST_UNAVAILABLE");
  }).finally(() => {
    clearTimeout(timer);
    if (requestId === currentRequest) {
      if (action === "set_volume" && confirmedVolume !== request.volume && confirmedVolume !== null) showVolume(confirmedVolume);
      if (action === "set_brightness" && confirmedBrightness !== null) showBrightness(confirmedBrightness);
      buttons.forEach((button) => { button.disabled = false; });
      volumeSlider.disabled = confirmedVolume === null;
      brightnessSlider.disabled = confirmedBrightness === null;
    }
  });
}

buttons.forEach((button) => {
  button.addEventListener("click", () => requestStatus(button.dataset.action));
});

volumeSlider.addEventListener("input", () => {
  volumeValue.textContent = `${volumeSlider.value}%`;
});

volumeSlider.addEventListener("change", () => {
  const volume = Number(volumeSlider.value);
  if (volume !== confirmedVolume) requestStatus("set_volume", { action: "set_volume", volume });
});

brightnessSlider.addEventListener("input", () => {
  brightnessValue.textContent = `${brightnessSlider.value}%`;
});

brightnessSlider.addEventListener("change", () => {
  const brightness = Number(brightnessSlider.value);
  if (brightness !== confirmedBrightness) requestStatus("set_brightness", { action: "set_brightness", brightness });
});

requestStatus("audio_status").then(() => requestStatus("brightness_status"));

logoutButton.addEventListener("click", async () => {
  if (!window.confirm("Cageのログインセッションを終了します。開いている作業は失われます。続けますか？")) return;
  logoutButton.disabled = true;
  showResult("Cageからログアウトしています…");
  let timer;
  try {
    const timeout = new Promise((_, reject) => {
      timer = setTimeout(() => reject(new Error("応答待機が10秒を超えました")), RESPONSE_TIMEOUT_MS);
    });
    const response = await Promise.race([
      browser.runtime.sendNativeMessage(HOST_NAME, { action: "cage_logout" }), timeout,
    ]);
    if (response?.success === true && response.error === null) {
      showResult("ログアウト要求を送りました。");
    } else if (response?.success === false && typeof response.error?.message === "string") {
      showResult(response.error.message, "", response.error.code || "");
    } else {
      showResult("システム機能から正しい応答を受け取れませんでした。", "", "HOST_UNAVAILABLE");
    }
  } catch (error) {
    console.error("Cageログアウトに失敗しました:", error);
    showResult("Cageからログアウトできませんでした。", "", "HOST_UNAVAILABLE");
  } finally {
    clearTimeout(timer);
    logoutButton.disabled = false;
  }
});
