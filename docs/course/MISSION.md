# Mission: The Parrot VoIP Course — team onboarding curriculum

## Why (pivoted 2026-07-06, learner-approved)
This workspace originally existed to tutor one engineer on the Parrot system. It now produces and
maintains **a 13-lesson onboarding course for anyone joining the VoIP team**: a new team member who
completes it should understand every layer of the system — enterprise `voip`, IAP `phone_service`,
Wazo (Asterisk + Kamailio + rtpengine), Telnyx — and be ready to contribute: discuss architecture,
place changes in the right layer, and trace any flow end to end.

The original learner remains learner #1 and continues through the same course; their personal
progression lives in `learning-records/`, not in the lessons.

## Success looks like (for any course graduate)
- Given any component (Kamailio, Asterisk, rtpengine, Telnyx, IAP, the softphone), they can say
  what it does, which **plane** it lives on, and who it talks to — from memory.
- They can trace a real flow end-to-end (buy a number, place/receive a call, leave a voicemail,
  get billed) and name every hop, protocol, and credential involved.
- In a design discussion they can argue *where* a feature belongs (enterprise vs shop vs Wazo)
  and state the trade-offs — including the golden rules (DB never talks to Telnyx **or** Wazo;
  media is the one carve-out; tenancy is structural; idempotent robots everywhere).
- They can read a bug report ("call connects but silent", "wrong caller-ID", "cost = 0",
  "browser won't ring") and know which layer/plane to look in first.

## Constraints
- Audience: competent Odoo/Python developer, **zero telecom background** assumed.
- Lessons are short (8–12 min), diagram-first, analogy-first, with retrieval interactives.
- Ground everything in the living onboarding doc + the code at HEAD — never parametric memory.
- The course must be regenerated when the PRs move substantially (same living-doc discipline as
  `parrot-onboarding.md`); `index.html` header carries the sync date.

## Out of scope (for now)
- Becoming a Kamailio/Asterisk *config* expert (a colleague owns the VPS setup).
- Deep PSTN / SS7 carrier internals below Telnyx.
- Building a softphone UI from scratch.
