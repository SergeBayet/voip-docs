# Teaching Notes — Parrot VoIP Course

## What this workspace is now (since 2026-07-06; refreshed 2026-08-07)
A **15-lesson / 4-module team-onboarding course** (see MISSION.md — pivot approved by the learner).
`index.html` is the course home; the whole folder is shareable as-is (diagram libs vendored → offline).
Built against enterprise `b8ab6403a14` + iap-apps `333b603a` + community `beed9ed0448a`
(2026-08-07 refresh; original build was 2026-07-06 @ `d416ce5b278`/`0e0600ba`).

### 2026-08-07 refresh — what changed (the branches were rebased; verify vs HEAD, not old hashes)
- **Renames swept everywhere** (doc + glossary + lessons): `voip.pbx.event`→`voip.phone.service.event`,
  `voip.audio.message`→`voip.sound`, `voip.queue.mixin`→`voip.activity.mixin`; doorbell route
  `/voip/api/event`→`/voip/api/phone_service/event`; event method `_handle_call_event()`→`_ack_then_process()`.
- **TTS re-platformed**: on-prem Piper/ONNX + `voip.voice` model are GONE; TTS is now a shop capability
  (`voip.sound._generate_tts_audio`→`PhoneServiceAPI.generate_speech`→Telnyx voices, language-filtered).
- **New subsystems added to the course**: Call Flow editor (`voip.call.flow`, L14) and `voip_ai`
  OpenAI-Whisper transcription + AI summary (L15). Music-on-hold (`voip.music.on.hold`) folded into L12.

## Audience & voice (apply to EVERY lesson)
- Written for **any new VoIP team member**: competent Odoo dev, ZERO telecom background.
  No personal references, no "as we discussed" — the reader is a stranger.
- **Diagram first.** Lead with a simple diagram (Mermaid preferred) before prose.
- **Always real-world examples / analogies.** Everyday anchor (switchboard, hotel, concierge,
  letterbox) before the formal version.
- **Start at a 12-year-old's level, then ramp.** Plain words + picture → earn the jargon →
  the precise version. Never introduce a concept as a dense aside (learning record 0003).
- Retrieval interactives with instant feedback; quiz choices SAME length.
- Short (8–12 min), beautiful, printable; cite sources heavily; ground in the onboarding doc
  (reference/onboarding.html) + code at HEAD.
- `lessons/TEMPLATE.html` is the single source of style + interaction machinery
  (makeSorter / makeQuiz / makeOrderer). Copy verbatim; don't fork the palette.

## The curriculum (v1 built 2026-07-06; L14–L15 added 2026-08-07)
Module 1 — The Map: 01 Odoo becomes a phone company · 02 Two planes · 03 SIP lifecycle
Module 2 — A Call's Life: 04 Outbound + caller-ID · 05 Inbound + incall/event relay · 06 Migration why
Module 3 — The Machine Rooms: 07 The shop (broker/capability API) · 08 Tenancy & provisioning · 09 Doorbells & robots
Module 4 — The Product: 10 Buy a number E2E · 11 Desks, teams & waiting rooms · 12 Voicemail/sound/MOH/TTS · 13 Following the money · **14 Call Flow editor** · **15 AI transcription & voices**

Old personal-arc lessons (pre-pivot L1–L4) live in `lessons/archive/` — superseded by 02–05.
The earlier webhook-reliability workspace (`../parrot-teach/`) was mined for L09's principles
(push-what-you-can, silent-200 anti-pattern, the reverted quarantine as cautionary tale).

## Course maintenance protocol
When the PRs move substantially: re-read the deltas → regenerate `parrot-onboarding.md`
(canonical vault + mirror, byte-identical) → rebuild `reference/onboarding.html`
(`reference/build_onboarding.py`) → touch only the lessons the change invalidates →
bump the sync date in `index.html` and the glossary footer.
Known fact-check from the build: tenant `PROVISIONING_TTL` is **2 h** (not 24 h) — L08 caught it.

## Personal learning threads
Individual learners' progression and coaching history live in `learning-records/` — which is
**gitignored**: it stays on the maintainer's machine and never ships in the team repo.

## Open threads to weave into future lessons / revisions
- Agent presence UI: the agentd login/pause surface has no business callers yet (L11 notes it
  honestly) — when the feature lands, L11 needs a section and maybe a new lesson.
- Kamailio-side push infra: the `call.push` wake mechanism is explicitly interim ("waiting for
  Kamailio", c0faf70bde1) — when it lands, L05/L06 need updates.
- Media deep-dive (NAT/ICE/TURN, the "silent call" ports story) is currently distributed
  (L02 payoff + glossary note); could become its own advanced lesson if debugging demand grows.
- Voicemail: recording download uses the confd URL prefix where upstream documents calld —
  verify against a live box; L12 flags it.
- `voip_ai` transcription has **no cron backstop** (cron test deleted) — a dropped trigger strands
  an artifact in `pending`; L15 flags it. Watch for a retry cron landing later.
- Community push-wake plumbing (mail/web service-worker: `waitingMessage`, `handleNotificationClick`,
  direct push send — dam@odoo) landed on `master-parrot` odoo; not yet woven into L05/L09 — do so if the
  softphone incoming-call wake story is asked about.
- `pr-107700-diagrams-updated.md` is stale (pre-refactor) — update or retire.
- NOT re-verified this pass (assumed still accurate): L05/L09 IAP-side controller/util filenames
  (`pbx_controller.py`, `wazo_events.py`), the `event_id = call_id:event_name` composition, the 12 h
  event GC interval. Spot-check these next refresh.
