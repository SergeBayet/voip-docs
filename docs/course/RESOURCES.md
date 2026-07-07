# Parrot VoIP System Resources

## Knowledge

### Our own docs (primary — grounds everything in *our* system)
- [Parrot Onboarding Guide](/home/odoo/Data/Dev/Odoo/parrot-onboarding.md) — canonical at Obsidian vault `VoIP/parrot/parrot-onboarding.md`.
  The living source of truth: the four players, the buy / requirements / provisioning / inbound / outbound / billing stories, data shapes, crons, file map. Use for: how *our* system actually behaves.
- Wazo Architecture Session note — Obsidian vault `VoIP/parrot/Wazo Architecture Session.md`.
  Working notes on the Wazo migration: components, credential chain, dialplan compile-vs-interpret, decisions A–J, glossary, the silent-call failure mode. Use for: the *why* behind the migration.
- [Onboarding Excalidraw diagrams](/home/odoo/Data/Dev/Odoo/master-parrot/voip-wazo-onboarding/)
  12 diagrams: high-level overview, current-vs-future, inbound/outbound sequences, control plane, ports, credential chain, dialplan compile, tenancy. Use for: visual mental models. ⚠️ Predates the DB→IAP→WAZO refactor in places — trust the onboarding guide when they disagree.
- [Wazo internal DID routing note](/home/odoo/Data/Dev/Odoo/wazo-internal-did-routing.md) (2026-06-23)
  Why dialing a colleague's public DID is resolved to their extension before the INVITE (the softphone short-circuit). Use for: L04/L05 depth.
- `pr-107700-diagrams-updated.md` — deep-dive twin of the onboarding doc. ⚠️ **Stale** (pre-refactor, 2026-06-09); update or retire before citing.

### SIP / signaling (the control plane)
- [RFC 3261 — SIP: Session Initiation Protocol](https://www.rfc-editor.org/rfc/rfc3261.html)
  The canonical SIP spec. The control-plane / media-plane separation is foundational. Use for: ground-truth on SIP methods, proxies, dialogs.
- [Wikipedia: Session Initiation Protocol](https://en.wikipedia.org/wiki/Session_Initiation_Protocol)
  Accessible overview of SIP and the signaling-vs-media split. Use for: a readable first pass.

### Kamailio (the SIP edge)
- [Kamailio vs Asterisk — Nick vs Networking](https://nickvsnetworking.com/kamailio-vs-asterisk/)
  Clear, trusted explanation of SIP-proxy vs B2BUA and why you run both. Use for: the Kamailio/Asterisk division of labour.
- [Kamailio Wiki — FAQ](https://www.kamailio.org/wikidocs/tutorials/faq/main/)
  Official project FAQ. Use for: authoritative "what Kamailio is / isn't".

### Wazo (our PBX)
- [Wazo Platform — docs](https://wazo-platform.org/documentation/)
  The PBX we're adopting: Asterisk + Kamailio + rtpengine + Python microservices (confd, calld, auth, webhookd). Use for: component roles and REST APIs.
- [Wazo Platform C4 overview](https://beta.wazo-platform.org/blog/wazo-platform-c4-overview)
  Architecture-level view of the layers and services. Use for: how the microservices fit together.

### WebRTC / media (the media plane)
- [RFC 7118 — SIP over WebSocket](https://www.rfc-editor.org/rfc/rfc7118.html)
  How browsers carry SIP (the WSS transport our softphone uses). Use for: browser ↔ Kamailio signaling.
- [MDN — WebRTC API](https://developer.mozilla.org/en-US/docs/Web/API/WebRTC_API)
  The browser media stack (ICE / STUN / TURN, DTLS-SRTP). Use for: the media leg + NAT / "silent call" issues.

## Wisdom (Communities)
- [Kamailio users mailing list](https://lists.kamailio.org/) — high-signal; core devs answer. Use for: SIP-edge routing/config questions.
- [Asterisk Community forum](https://community.asterisk.org/) — Use for: dialplan, PJSIP, ARI questions.
- [Wazo Platform community](https://wazo-platform.org/) (forum/chat linked from the site) — Use for: Wazo provisioning / REST questions.
- *(Learner has not opted out of communities — surface these when a question needs practitioner wisdom.)*

## Gaps
- No single authoritative doc yet for *our exact* Wazo dialplan-compile mapping (Odoo 20 Callflow → wazo-confd). Will need to read the code once that lands; for now the Wazo session note §6 is the best we have.
