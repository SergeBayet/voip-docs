# Mission: Odoo VoIP team onboarding

## Why

This workspace is the onboarding course for an engineer joining Odoo's VoIP team. A graduate must
be able to contribute inside the VoIP stack and still navigate ordinary Odoo work in another team.
The course therefore starts with the Odoo platform and contribution loop before teaching telephony.

## Audience

A competent Python/JavaScript developer with **no Odoo knowledge and no telecom knowledge assumed**.
Existing Odoo developers may use the accelerated path on the course home, but the lessons must never
depend on private history or unexplained internal vocabulary.

## Success looks like

A graduate can:

- trace one Odoo request through controller, ORM, security, data/view, Owl service and tests;
- choose the owning repository, addon and branch family for an ordinary Odoo or VoIP change;
- run, debug, test and hand off a small change using Odoo's established extension patterns;
- explain SIP signaling versus media and place the browser, Kamailio edge, Wazo and Telnyx correctly;
- trace number purchase, regulatory requirements, IAP charging, provisioning, inbound/outbound calls,
  events, queues, voicemail, Call Flows, call cost, transcription and TTS end to end;
- diagnose a symptom by naming the failed boundary and following stable identifiers;
- produce a minimal contribution with a failing check, root-cause fix and factual verification report.

## Shape and teaching constraints

- 28 short core lessons in 8 modules, plus focused field lessons for active work; roughly five hours
  of core reading and exercises.
- Diagram first, everyday analogy first, precise code contract second.
- Each lesson has retrieval practice, primary sources, a code path and an “ask your agent” prompt.
- Code at the verified checkout is authoritative. The rendered onboarding guide is a cross-system map,
  not permission to repeat stale claims.
- Security, money, ownership, accessibility and failure behavior are never simplified away.

## Deliberate limits

The course teaches enough PBX and carrier architecture to contribute safely; it is not operator
certification for Asterisk, Kamailio, Telnyx, Kubernetes or the production network. Deep operational
changes require the owning team's runbooks and supervision.
