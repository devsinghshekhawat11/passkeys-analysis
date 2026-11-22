# H1 test: why Selective sites block security-key and phone passkey setup

## What we are testing
Hypothesis H1: the 20 "Selective" sites in Ramat et al. (0% on F09 HSK-Setup and F10 Cross-Device-Setup, yet sign-in with phones/keys works) ask the browser for a passkey **only on this device** when you create one. They do this by sending `authenticatorAttachment: "platform"` (or `hints: ["client-device"]`) in the registration request. Google's web.dev passkey checklist recommends exactly this for promoted creation.

- If most Selective sites send `platform` → the inconsistency is caused by a guideline/library setting (a guidance conflict), not by the site "not supporting" keys.
- If they send nothing restrictive → the cause is elsewhere (browser UI, site-side checks), and H1 is rejected.

Control group: test 5 Standard sites (e.g. GitHub, Google, Microsoft, Amazon, Shopify). They should NOT send `platform`.

## Devices
- Required: one Windows 11 or macOS laptop with Chrome (the paper used Windows 11 + Chrome).
- Nice to have: an Android phone (to see whether the QR / "use a phone" option appears), and a USB security key if you have one.
- Use your own test accounts. You do not need to finish creating a passkey; you can cancel the browser dialog once the options are logged.

## Steps per site
1. Sign in to the site in Chrome and go to the page with "Add passkey" (usually Security settings).
2. Open DevTools (F12) → Console.
3. Paste the snippet below and press Enter. It only prints to your own console; it sends nothing anywhere.
4. Click "Add passkey". The console prints a block starting `[H1 create]`.
5. Screenshot the console line and the browser dialog (does it offer "Use a phone or tablet" / "Use a security key"?). Cancel the dialog.
6. Optional: sign out, paste the snippet again on the sign-in page, start passkey sign-in, and note the `[H1 get]` line.
7. Record the row in the table below.

## Console snippet
```js
(() => {
  const strip = (o) => JSON.parse(JSON.stringify(o, (k, v) =>
    (v instanceof ArrayBuffer || ArrayBuffer.isView(v)) ? `<${v.byteLength} bytes>` : v));
  const c = navigator.credentials.create.bind(navigator.credentials);
  const g = navigator.credentials.get.bind(navigator.credentials);
  navigator.credentials.create = (opts) => {
    const p = opts && opts.publicKey;
    if (p) console.log('[H1 create]', location.hostname, JSON.stringify(strip({
      authenticatorSelection: p.authenticatorSelection, hints: p.hints,
      attestation: p.attestation, excludeCredentials: (p.excludeCredentials || []).length,
      mediation: opts.mediation })));
    return c(opts);
  };
  navigator.credentials.get = (opts) => {
    const p = opts && opts.publicKey;
    if (p) console.log('[H1 get]', location.hostname, JSON.stringify(strip({
      allowCredentials: (p.allowCredentials || []).map(a => a.transports),
      hints: p.hints, userVerification: p.userVerification, mediation: opts.mediation })));
    return g(opts);
  };
  console.log('H1 logger ready');
})();
```
If nothing prints, the site may open the dialog in an iframe or a popup; note "not captured" and move on.

## Record sheet
| Site | Cluster | authenticatorAttachment | hints | residentKey | Dialog offered phone? | Dialog offered key? | Notes |
| --- | --- | --- | --- | --- | --- | --- | --- |
| PayPal | Selective | | | | | | |

Selective sites (paper Table 1): PayPal, Target, Best Buy, Pixiv, Shop, Konami, SumUp, Money Forward, Cash App, Link, Lnk, Free Tax USA, Webull, Syncfusion, Marshmallow, Marketcircle, Binance, OneLog, Tailscale (+1 more in Table 1).
