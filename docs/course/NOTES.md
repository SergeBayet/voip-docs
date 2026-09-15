# Teaching and maintenance notes

## Current shape — post-merge architecture

The user expanded the mission from “VoIP for an experienced Odoo developer” to **complete onboarding
for a new Odoo and VoIP team member**. The course has 28 core lessons in 8 modules, with focused
field lessons for active work. Lessons 1–11 build
the Odoo platform/contribution foundation; Lessons 12–26 cover the VoIP system; Lessons 27–28 turn the
maps into a debugging and contribution workflow. The decision is recorded in learning record 0006.

## Teaching contract

- Audience: competent Python/JavaScript developer, zero Odoo and zero telecom assumed.
- Diagram and analogy before jargon; never hide a new concept in a dense aside.
- Short, printable lessons with instant-feedback retrieval practice.
- Every implementation claim is checked against source; primary docs explain upstream concepts.
- Every lesson ends with a useful agent prompt that asks for evidence from the current checkout.

## Curriculum

1. Odoo platform: request path; repositories/branches; addon anatomy.
2. Odoo code: ORM; data/views/actions/translations; Owl; security.
3. Contribution: tests; run/debug/profile; shipping; VoIP workbench.
4. VoIP map: system cast; signaling/media; SIP lifecycle.
5. Calls: outbound; inbound; migration rationale.
6. Machine rooms: broker; tenant/provisioning; events/reconciliation.
7. Product: number purchase; routing/queues; voicemail; money; Call Flow; AI/TTS.
8. Shipping: cross-stack debugging; first-contribution capstone.

## Architecture anchors for this edition

- Supported architecture: shared Enterprise `voip-common`, Phone Service
  `phone-service-common`, the `voip-boi` provisioning policy, and the merged
  Community/Enterprise scheduled-call behavior.
- Stable code boundaries: `odoo/addons/mail/`, `odoo/addons/web/`,
  `enterprise/voip/`, `iap-apps/iap_services/phone_service/`, and
  `voip-infra/`.
- The source walkthrough intentionally contains no branch, commit, or line-number
  anchors. Use its `git status` and `rg` commands to resolve the code you have.

The current feedback layer covers the number-request email list link, complete DID flag/destination
visuals, scheduled-call phone and partner rules, Call-before-Done with hover Copy, and DID
destination auto-selection plus required-target validation. Offline routing now uses Wazo's Fail
Destination with valid `mobile_phone` then `phone`, storing routing before token revocation or
restoration. Restoration is attempted with available auth; a mint failure can be logged without
failing the routing response. A provisioned Wazo call and the pending
`X-Odoo-Conversation-Id` subroutine are still required to accept external call-record correlation.
Field lesson 0029 teaches that offline-forwarding boundary from first principles and keeps the
Wazo-server procedure explicitly separate from the committed Enterprise/IAP configuration.

The source walkthrough at `reference/source-walkthrough.html` is the slow code-reading companion:
plane view first, vertical stories, authored money/audio/ownership/transaction/provisioning/event/
browser/edge sittings, then source-derived Python and JavaScript function execution cards and
resource/test lists. The authored sittings explain rationale; generated cards explain visible
inputs, guards, branches, assignments, calls, returns and exception handling, not transitive effects.
Refresh with `python3 reference/build_source_walkthrough.py`; then run its `--check` mode against
the intended workspace. It requires Node and Acorn already installed in the Enterprise checkout,
does not import Odoo, and contacts no external service. The fingerprint rejects changed bodies
and added/removed names; it cannot certify deployment or validate authored rationale automatically.
Do not add line-number or temporary-branch links. Advanced-order/Number Request code is a separate
feature track, not established as released by the shared/scheduled-call merge assumption.

## Drift hotspots

- Enterprise Parrot is merged on `master`; old `master-parrot/enterprise` examples are historical.
- The public SIP edge is separate from Wazo. Browser and carrier signaling traverse the edge; media
  bypasses the edge and Phone Service.
- Customer callbacks carry the full event envelope in a scoped, expiring signed token. They do not
  use a detached HMAC body/header contract.
- A DID writes `destination_ref`; `user_id` is derived only for a direct user destination.
- An empty-inventory request is `voip.did.number.request`, not a placeholder DID. It owns the Telnyx
  status/comment thread and proposed digits. Phone Service sends `auto_proceed=false`; comments are
  the public approval/rejection path, fulfilled DIDs link back by the stable request UUID, and
  requirement resubmission uses that UUID to update and reapply the request's owned group.
- Queue authorship is `allowed_user_ids` + `allowed_call_group_ids`; there is no
  `voip.queue.agent.source` model. Users can join and leave assigned queues.
- Both global and user voicemail-message events are consumed. A failed audio pull currently has no
  dedicated retry cron/button.
- Call costs and monthly fees use remote per-line IAP idempotency. Initial number purchase still uses
  the classic authorize-token/capture saga and retains its documented capture-response-loss wedge.
- Advanced-request recovery commits Pending before scheduled submission and pulls adopted-number
  states to discover DIDs missing after lost callbacks. IAP now requires a ready PBX tenant before
  submitting the provider request, and it keeps polling an `ordered` parent until distinct successful
  adopted DIDs reach the requested quantity, covering late and replacement child orders. Stable-UUID
  retries reuse the carrier key, but Telnyx's Advanced Order replay semantics still require
  confirmation. Existing jobs and status handlers are reused.
- Transcription is request-triggered and has no scheduled cron backstop. TTS is base `voip` through
  Phone Service/Telnyx, not `voip_ai`.

## Refresh protocol

1. Resolve the actual target branches, SHAs, and deployment target; do not trust this note as a release-status record.
2. Read changed production code and tests before touching prose.
3. Update the canonical vault onboarding and its local mirror together when architecture facts change.
4. Run `python3 reference/build_onboarding.py`.
5. Update the smallest set of lessons and references; keep ownership paths and symbols stable.
6. Run `python3 reference/validate_course.py`, the source-note parser `--self-test` and freshness
   `--check`; open the course home and render every Mermaid diagram with the vendored browser library.
   Exercise correct/incorrect feedback, including a screen-reader-accessible correctness label.
7. Mirror to `voip-docs/docs/course` excluding repository-only files, local learning records and disposable Python caches (`__pycache__/`, `*.pyc`).
8. Diff both trees and report exactly what was and was not tested. No remote action without approval.

The superseded lessons in `lessons/archive/` are historical material and intentionally unlinked; do
not use them as current architecture evidence.

## Publication gate

The current docs repository/Pages site are public although the course is internal-only. The local
Pages workflow deliberately fails before checkout/build/upload, including manual dispatch. Do not
remove the guard before approval of both repository access and authenticated hosting. It does not
hide existing branches or remove the deployed site; those remote changes need explicit authority.
