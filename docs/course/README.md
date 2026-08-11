# 🦜 The Parrot VoIP Course

A self-contained onboarding curriculum for engineers joining Odoo's VoIP team:
**13 short lessons in 4 modules** that take you from "what's a SIP?" to tracing a
purchase, a call, a voicemail and a charge across the whole Parrot stack —
enterprise `voip` → IAP `phone_service` → Wazo (Asterisk + Kamailio + rtpengine) → Telnyx.

> ⚠️ **Internal only.** These lessons describe unreleased architecture and security
> reasoning for open PRs (odoo/enterprise#107700 · odoo/iap-apps#1370). Don't host or
> mirror them outside Odoo infrastructure.

## Getting started

```bash
git clone <this-repo>
xdg-open parrot-voip-teaching/index.html   # macOS: open · Windows: start
```

That's it. Everything is plain HTML with the diagram libraries vendored in `vendor/`,
so it works fully offline. Take the lessons **in order** — each one leans on the
previous — and do the interactive exercises; that's where it sticks. Budget ~2½ hours
total, in 8–12 minute sittings.

| Module | Lessons | You come out able to… |
|---|---|---|
| 1 · The Map | 1–3 | name the four machines, the golden rules, the two planes, and every SIP message in a call |
| 2 · A Call's Life | 4–6 | trace outbound and inbound calls hop-by-hop, and argue why the Telnyx-direct world was replaced |
| 3 · The Machine Rooms | 7–9 | explain the broker, structural tenancy, the 11-step floor build, and the webhook/robot reliability playbook |
| 4 · The Product | 10–13 | walk a number purchase, routing (users/groups/queues), voicemail, and billing end-to-end |

When anything is fuzzy, **interrupt your agent**: open a Claude Code session in the
repos and ask it to show the real message, the real code path, or to quiz you harder.

## What's in the folder

```
index.html                 ← course home (start here)
lessons/0001…0013-*.html   ← the 13 lessons (TEMPLATE.html = authoring template)
lessons/archive/           ← superseded pre-course drafts, kept for history
reference/onboarding.html  ← the living Onboarding Guide, rendered (source: parrot-onboarding.md)
reference/glossary.html    ← canonical vocabulary, plane-tagged
reference/build_onboarding.py ← regenerates onboarding.html from the markdown source
vendor/                    ← mermaid + marked, vendored so everything works offline
MISSION.md · NOTES.md · RESOURCES.md ← course mission, authoring/maintenance notes, sources
```

## Keeping it alive

The course is generated against a specific state of the PRs (see the sync date in the
`index.html` header — currently **2026-07-06**, enterprise `d416ce5b278` /
iap-apps `0e0600ba`). When the branches move substantially:

1. Regenerate `parrot-onboarding.md` from a re-read of the deltas (it is the source of
   truth every lesson cites), then run `python3 reference/build_onboarding.py`.
2. Update only the lessons the change invalidates (protocol + known drift-hotspots in
   `NOTES.md`), following `lessons/TEMPLATE.html` — including its cross-linking rules.
3. Bump the sync date in `index.html` and the glossary footer, commit, push.

The short version: ask your agent to *"re-verify the Parrot course against the current
branches"* — the whole protocol is written down in `NOTES.md`.
