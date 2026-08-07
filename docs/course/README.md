# Odoo VoIP Team Onboarding

A self-contained, internal course for engineers joining Odoo's VoIP team: **28 short core lessons
in 8 modules, plus focused field lessons**, from a first Odoo request to buying and billing a real
number, carrying calls through the edge/PBX, and shipping a tested first contribution.

Open [`index.html`](index.html) in a browser. Everything is plain HTML and the diagram library is
vendored, so the course works offline.

## Curriculum

| Module | Lessons | Outcome |
|---|---:|---|
| Odoo as a platform | 1–3 | Repositories, request path and addon anatomy |
| Writing Odoo code | 4–7 | ORM, data/views, Owl and security |
| Contribution loop | 8–11 | Tests, local debugging, shipping and the VoIP workbench |
| VoIP map | 12–14 | Components, signaling/media and SIP lifecycle |
| A call's life | 15–17 | Outbound, inbound and the move from Telnyx-direct |
| Machine rooms | 18–20 | Phone Service, structural tenancy, provisioning and events |
| Product | 21–26 | Buy Number, routing/queues, voicemail, billing, Call Flows and AI/TTS |
| Shipping VoIP work | 27–28 + field lessons | Cross-stack debugging, the first-contribution capstone and active feature reviews |

Budget about five hours in 8–12 minute sittings, plus the capstone task. Experienced Odoo developers
can start at Lesson 11 and use Lessons 1–10 as reference.

## Layout

```text
index.html                  course home
assets/                     shared course styles and interactions
lessons/0001…0028-*.html    core lessons; later numbers are field lessons
reference/                  onboarding, source walkthrough, validators, glossary, maps and checklists
vendor/                     offline Mermaid and Markdown renderer
MISSION.md                  audience and graduation outcomes
NOTES.md                    maintenance and drift protocol
RESOURCES.md                primary source shelf
learning-records/           local, unshipped teaching decisions
```

## Current teaching baseline

This edition treats the current merge wave as integrated architecture: the shared
`voip-common` Enterprise foundation, the `phone-service-common` Phone Service
foundation, the `voip-boi` provisioning-policy work, and the Community/Enterprise
scheduled-call changes. The course explains the resulting ownership and contracts;
it does not claim that a local checkout or source file proves deployment state.

The feedback acceptance pass keeps planned-call numbers selectable, places Call immediately before
Done, and preserves a blank linked contact when an automated activity merely accepts its prefill.
It also loads complete flag labels and destination visuals, routes number-request email recipients
to the Phone Numbers list, and makes the real DID form auto-select and require the destination target.
Offline routing now configures Wazo's Fail Destination from valid `mobile_phone` then `phone`, revokes
the wakeup token only after that route is stored. With neither number valid, routing clears the
fallback and then attempts wakeup restoration when auth is available; a successful routing response
does not prove token minting succeeded. Real-call acceptance still needs the pending Wazo
`X-Odoo-Conversation-Id` subroutine.

The advanced-number-order flow adds persistent Number Requests, status/comment callbacks, proposed
number display, and links from fulfilled DIDs back to their request. This is a separate feature
track: the shared/scheduled-call merge assumption does not prove its release or deployment.
Requests send
`auto_proceed=false`; administrators review and answer proposals through comments, and child-order
adoption plus charging starts only when Telnyx marks the request `ordered`. Successful submission
opens the request form directly. The buy footer has one contextual primary action, always first: **Search**
initially or after an error, **Request Numbers** after empty inventory, **Buy Credits** for
unaffordable results, and **Pay** or **Continue** for affordable results. **Search** remains as a
secondary retry only for empty or unaffordable results. Editing a criterion and immediately clicking
Search, Request Numbers, or Buy Credits performs the chosen action on the first click. Empty inventory includes the provider's
typed no-number response. The request form shows Area Code beneath Quantity and Requested On above
Requested By. Its provider-neutral **Contact Odoo's Phone Carrier** composer is separate from Odoo
chatter, uses a proof-of-address update placeholder and text-only send action, and reacts immediately
while the administrator types or clears the draft. Provider-originated entries use OdooBot without exposing employee email addresses.
Rejected-requirement resubmission updates the reusable group and reapplies it to the client-owned
advanced order so the provider evaluates the replacement values.
The recovery path saves/opens Pending first and submits through the existing scheduled job only after
the initial RPC commits. Stable-UUID retries reuse the carrier key, whose
Advanced Order replay semantics still need Telnyx confirmation. Request synchronization includes
adopted number states and reuses the normal DID handler, including old partially delivered requests.
Current-state reads avoid applying stale Telnyx status notifications, and failed Enterprise forwarding
does not undo IAP adoption. No new queue or order model is added.

Enterprise Parrot is part of the supported Enterprise line; historical feature worktrees are
useful only as history. Re-check the actual target branch and deployment state before making a
release claim. The source walkthrough reads the stable Enterprise, Community, IAP Phone Service
and `voip-infra` boundaries, and uses file paths plus symbols so readers can re-find code after
branches move.

## Keeping the twins aligned

The maintained course lives in two trees:

- `/home/odoo/Data/Dev/Odoo/parrot-voip-teaching`
- `/home/odoo/Data/Dev/Odoo/voip-docs/docs/course`

They must remain byte-identical except for repository metadata, `.gitignore`, local
`learning-records/`, and disposable Python caches (`__pycache__/`, `*.pyc`). Refresh the canonical onboarding Markdown first when architecture facts change,
rebuild `reference/onboarding.html`, update only affected lessons, then run the link/HTML checks and
compare the twins. Do not publish or push without explicit approval.

Run `python3 reference/validate_course.py` for offline page/link/JavaScript checks and
`python3 reference/build_source_walkthrough.py --check` for source-note freshness (Node/Acorn from
the Enterprise checkout are required). Browser rendering and live carrier/PBX acceptance remain
separate checks. The function companion supplies source-order execution notes; the authored
sittings explain money, audio, security and failure-design decisions.

The docs Pages workflow is blocked pending approval of repository and hosting access controls.
This local change does not make the already-public repository or existing Pages deployment private.
