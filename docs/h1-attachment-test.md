# H1 test: why Selective sites block security-key and phone passkey setup

## Status: tested with logged data (paper Section 4.8)

Hypothesis H1: the "Selective" sites in Ramat et al. (0% on F09 HSK-Setup and F10 Cross-Device-Setup, yet sign-in with phones and keys works) ask the browser for a passkey **only on this device** when you create one, by sending `authenticatorAttachment: "platform"` (or `hints: ["client-device"]`) in the registration request.

We tested H1 without visiting any website, using the registration and sign-in options that Jannett et al. (USENIX Security 2026) logged for their PASSKEYS-RADAR study (`analysis/a12_join_webauthn.py`, `analysis/a13_webauthn_tests.py`):

| Question | Result (89 sites with logged options) |
| --- | --- |
| Do Selective sites send `authenticatorAttachment: "platform"`? | Yes: 13 of 14 (93%), against 12 of 74 Standard sites (Holm p < 0.001) |
| Do they use `hints: ["client-device"]` instead? | No. None of the Selective sites uses `hints`; one site in the whole set does |
| Is sign-in left open? | Yes: 11 of 14 send an empty `allowCredentials` or list no transports, so the browser offers every authenticator |
| Do Standard "control" sites avoid `platform`? | Mostly, but not all: 12 Standard sites send `platform` in their main flow (Google among them) and still pass F09, apparently through a second enrollment path |

H1 is confirmed. The correction to the original plan is that a Standard site such as Google is **not** a clean control: restricting the main flow is common, and what separates the Selective sites is having no alternative enrollment path.

## What still needs a manual check

The logs capture one registration call per site (the main passkey flow, around April 2025). Two gaps remain, and this protocol closes them:

1. **The 12 restricted sites that still pass F09.** Confirm that each offers a separate, unrestricted enrollment path (for example "Add a security key" in settings): Google, Yahoo, hCaptcha, Hyatt, DocuSign, Visma, Fastmail, ESL Gaming, Moneybird, Dinero, Passage, Turnkey.
2. **The 6 Selective sites without logged options.** Record what they send: Shop, Konami, Cash App, Free Tax USA, Syncfusion, Lowe's.

The full list of the 20 Selective sites (Ramat et al., Table 1, cluster 2) is: PayPal, Target, Best Buy, Pixiv, Shop, Konami, SumUp, Money Forward, Cash App, Link, Lnk, Free Tax USA, Webull, Syncfusion, Marshmallow, Marketcircle, Lowe's, Nintendo, Binance, OneLog. Tailscale and LGTM form the separate Experimental cluster.

## Devices
- Required: one Windows 11 or macOS laptop with Chrome (the original study used Windows 11 and Chrome).
- Nice to have: an Android phone (to see whether the QR / "use a phone" option appears), and a USB security key.
- Use your own test accounts. You do not need to finish creating a passkey; cancel the browser dialog once the options are logged.

## Steps per site
1. Sign in to the site in Chrome and go to the page with "Add passkey" (usually security settings). For the 12 sites in gap 1, also look for a separate security-key option and try it.
2. Open DevTools (F12) and go to the Console.
3. Paste the snippet below and press Enter. It only prints to your own console; it sends nothing anywhere.
4. Click "Add passkey" (or "Add security key"). The console prints a block starting `[H1 create]`.
5. Screenshot the console line and the browser dialog (does it offer "Use a phone or tablet" or "Use a security key"?). Cancel the dialog.
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
| Site | Gap | Flow tested | authenticatorAttachment | hints | residentKey | Dialog offered phone? | Dialog offered key? | Notes |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Google | 1 | Add security key | | | | | | |
