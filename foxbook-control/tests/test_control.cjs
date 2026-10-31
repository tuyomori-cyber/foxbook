const assert = require('node:assert/strict');
const fs = require('node:fs');
const vm = require('node:vm');
const { test } = require('node:test');

const source = fs.readFileSync(`${__dirname}/../extension/control.js`, 'utf8');
const success = (output) => ({ success: true, output, error: null });
const device = (percent) => `intel_backlight,backlight,${percent},${percent}%,100\n`;
const settle = () => new Promise(setImmediate);

async function setup(brightnessResponse = success(device(60)), rotationResponse = success('normal')) {
  const elements = new Map();
  function element(id) {
    if (!elements.has(id)) elements.set(id, {
      value: '', textContent: '', disabled: true, listeners: {},
      addEventListener(event, handler) { this.listeners[event] = handler; },
    });
    return elements.get(id);
  }
  const buttons = ['audio_status', 'brightness_status', 'system_info', 'update_host', 'sync_score', 'rotation_status', 'toggle_rotation'].map((action) =>
    Object.assign(element(action), { dataset: { action }, textContent: action }));
  elements.set('rotation-toggle', element('toggle_rotation'));
  const calls = [];
  const replies = [success('Volume: 0.45'), brightnessResponse, rotationResponse];
  const timers = new Map();
  let timerId = 0;
  vm.runInNewContext(source, {
    document: { getElementById: element, querySelectorAll: () => buttons },
    browser: { runtime: { sendNativeMessage(host, request) {
      calls.push(JSON.parse(JSON.stringify(request)));
      const reply = replies.shift();
      return reply instanceof Error ? Promise.reject(reply) : Promise.resolve(reply);
    } } },
    window: { confirm: () => true }, console: { error() {} },
    setTimeout(callback) { timers.set(++timerId, callback); return timerId; },
    clearTimeout(id) { timers.delete(id); },
  });
  await settle();
  return { element, calls, replies, timers };
}

test('initialization loads volume then brightness and enables both sliders', async () => {
  const { element, calls, timers } = await setup();
  assert.deepEqual(calls, [{ action: 'audio_status' }, { action: 'brightness_status' }, { action: 'rotation_status' }]);
  assert.equal(element('volume-value').textContent, '45%');
  assert.equal(element('brightness-value').textContent, '60%');
  assert.equal(element('volume-slider').disabled, false);
  assert.equal(element('brightness-slider').disabled, false);
  assert.equal(timers.size, 0);
});

test('dragging only previews; release sends once and displays actual hardware value', async () => {
  const { element, calls, replies } = await setup();
  const slider = element('brightness-slider');
  slider.value = '54';
  slider.listeners.input();
  assert.equal(element('brightness-value').textContent, '54%');
  assert.equal(calls.length, 3);
  replies.push(success(device(53)));
  slider.listeners.change();
  assert.equal(slider.disabled, true);
  assert.equal(element('volume-slider').disabled, true);
  await settle();
  assert.deepEqual(calls[3], { action: 'set_brightness', brightness: 54 });
  assert.equal(element('brightness-value').textContent, '53%');
  assert.equal(Number(slider.value), 53);
  slider.listeners.change();
  assert.equal(calls.length, 4);
});

test('failed changes restore previous brightness and unlock controls', async () => {
  for (const reply of [
    { success: false, output: '', error: { code: 'PERMISSION_DENIED', message: '権限がありません' } },
    { success: false, output: '', error: { code: 'INVALID_REQUEST', message: '古いHost' } },
    new Error('connection failed'),
    success('malformed'),
  ]) {
    const { element, replies } = await setup();
    replies.push(reply);
    const slider = element('brightness-slider');
    slider.value = '80';
    slider.listeners.change();
    await settle();
    assert.equal(element('brightness-value').textContent, '60%');
    assert.equal(Number(slider.value), 60);
    assert.equal(slider.disabled, false);
    assert.notEqual(element('error-code').textContent, '');
  }
});

test('unavailable or invalid initial brightness leaves only brightness disabled', async () => {
  for (const reply of [success('bad data'), success(device(101)),
    { success: false, output: '', error: { code: 'UNKNOWN_ACTION', message: '未登録' } }]) {
    const { element } = await setup(reply);
    assert.equal(element('brightness-slider').disabled, true);
    assert.equal(element('volume-slider').disabled, false);
  }
});

test('brightness button refreshes current value', async () => {
  const { element, replies } = await setup();
  replies.push(success(device(25)));
  element('brightness_status').listeners.click();
  await settle();
  assert.equal(element('brightness-value').textContent, '25%');
});

test('rotation toggle displays confirmed direction and prevents repeated clicks while busy', async () => {
  const { element, calls, replies } = await setup();
  const button = element('rotation-toggle');
  assert.equal(button.disabled, false);
  assert.equal(button.textContent, '縦画面にする');
  replies.push(success('90'));
  button.listeners.click();
  assert.equal(button.disabled, true);
  button.listeners.click();
  await settle();
  assert.deepEqual(calls.slice(3), [{ action: 'toggle_rotation' }]);
  assert.equal(button.textContent, '横画面にする');
  assert.equal(element('rotation-value').textContent, '現在の向き：縦画面');
  assert.equal(button.disabled, false);
});

test('rotation failures disable toggling until a successful refresh', async () => {
  for (const reply of [success('270'), new Error('connection failed'),
    { success: false, output: '', error: { code: 'UNKNOWN_ACTION', message: '未登録' } }]) {
    const { element, calls, replies } = await setup(undefined, reply);
    const button = element('rotation-toggle');
    assert.equal(button.disabled, true);
    button.listeners.click();
    assert.equal(calls.length, 3);
    replies.push(success('90'));
    element('rotation_status').listeners.click();
    await settle();
    assert.equal(button.disabled, false);
    replies.push(reply);
    button.listeners.click();
    await settle();
    assert.equal(button.disabled, true);
    assert.equal(element('rotation-value').textContent, '現在の向き：未取得');
    assert.equal(element('volume-slider').disabled, false);
    assert.notEqual(element('error-code').textContent, '');
  }
});
