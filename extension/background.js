"use strict";

function openControlPage() {
  return browser.tabs.create({ url: browser.runtime.getURL("control.html") });
}

browser.action.onClicked.addListener(() => {
  openControlPage().catch((error) => console.error("制御ページを開けません:", error));
});
