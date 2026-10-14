"use strict";

const HOST_NAME = "foxbook_control";
const RESPONSE_TIMEOUT_MS = 10_000;
const UPDATE_TIMEOUT_MS = 40_000;
const buttons = [...document.querySelectorAll("button[data-action]")];
const logoutButton = document.getElementById("cage-logout");
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

function requestStatus(action) {
  const isUpdate = action === "update_host";
  if (isUpdate && !window.confirm("更新元のリポジトリからNative Hostを再インストールします。続けますか？")) return;
  const requestId = ++currentRequest;
  const label = buttons.find((button) => button.dataset.action === action).textContent.trim();
  buttons.forEach((button) => { button.disabled = true; });
  showResult(isUpdate ? "Native Hostを更新中…" : `${label}を取得中…`);

  let timer;
  const timeout = new Promise((_, reject) => {
    timer = setTimeout(() => reject(new Error("応答待機が時間内に完了しませんでした")), isUpdate ? UPDATE_TIMEOUT_MS : RESPONSE_TIMEOUT_MS);
  });

  Promise.race([
    browser.runtime.sendNativeMessage(HOST_NAME, { action }),
    timeout,
  ]).then((response) => {
    if (requestId !== currentRequest) return;
    if (!response || typeof response.success !== "boolean" || typeof response.output !== "string") {
      showResult("システム機能から正しい応答を受け取れませんでした。", "", "HOST_UNAVAILABLE");
    } else if (response.success && response.error === null) {
      showResult(isUpdate ? "Native Hostを更新しました。" : `${label}を取得しました。`, response.output);
    } else if (!response.success && response.error && typeof response.error.code === "string" && typeof response.error.message === "string") {
      showResult(response.error.message, "", response.error.code);
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
    if (requestId === currentRequest) buttons.forEach((button) => { button.disabled = false; });
  });
}

buttons.forEach((button) => {
  button.addEventListener("click", () => requestStatus(button.dataset.action));
});

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
