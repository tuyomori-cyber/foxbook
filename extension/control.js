"use strict";

const HOST_NAME = "foxbook_control";
const RESPONSE_TIMEOUT_MS = 10_000;
const button = document.getElementById("system-info");
const status = document.getElementById("status");
const output = document.getElementById("output");
const errorCode = document.getElementById("error-code");
let currentRequest = 0;

function showResult(message, text = "", code = "") {
  status.textContent = message;
  output.textContent = text;
  output.hidden = !text;
  errorCode.textContent = code;
  errorCode.hidden = !code;
}

function requestSystemInfo() {
  const requestId = ++currentRequest;
  button.disabled = true;
  showResult("実行中…");

  let timer;
  const timeout = new Promise((_, reject) => {
    timer = setTimeout(() => reject(new Error("応答待機が10秒を超えました")), RESPONSE_TIMEOUT_MS);
  });

  Promise.race([
    browser.runtime.sendNativeMessage(HOST_NAME, { action: "system_info" }),
    timeout,
  ]).then((response) => {
    if (requestId !== currentRequest) return;
    if (!response || typeof response.success !== "boolean" || typeof response.output !== "string") {
      showResult("システム機能から正しい応答を受け取れませんでした。", "", "HOST_UNAVAILABLE");
    } else if (response.success && response.error === null) {
      showResult("取得しました。", response.output);
    } else if (!response.success && response.error && typeof response.error.code === "string" && typeof response.error.message === "string") {
      showResult(response.error.message, "", response.error.code);
    } else {
      showResult("システム機能から正しい応答を受け取れませんでした。", "", "HOST_UNAVAILABLE");
    }
  }).catch((error) => {
    if (requestId !== currentRequest) return;
    console.error("Native Messaging エラー:", error);
    const message = error.message === "応答待機が10秒を超えました"
      ? "システム機能から応答がありません。"
      : "システム機能に接続できません。";
    showResult(message, "", "HOST_UNAVAILABLE");
  }).finally(() => {
    clearTimeout(timer);
    if (requestId === currentRequest) button.disabled = false;
  });
}

button.addEventListener("click", requestSystemInfo);
