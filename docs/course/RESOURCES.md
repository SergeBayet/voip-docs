# Odoo VoIP onboarding resources

Primary sources are ordered from our implementation outward. Source code wins when a lesson and a
document disagree.

## Current local implementation

- `master/odoo` — Community framework and addons: HTTP, ORM, security, web client, mail, IAP client.
- `master/enterprise` — Enterprise addons; `voip/` is the core product and `voip_ai/` adds call
  transcription. Integration addons include CRM, Helpdesk, Project, Sales, Subscriptions, SMS, HR
  and Recruitment.
- `master/iap-apps/iap_services/phone_service` — hosted broker, Telnyx integration, Wazo
  provisioning, events, number lifecycle, regulatory resources, TTS and billing.
- `master/iap-apps/iap_odoo` — shared IAP transaction server, including keyed
  `/iap/1/authorize_capture`.
- `upgrade` — migrations for modules such as `voip`, `voip_crm`, `crm_voip`, `voip_hr` and legacy
  `voip_onsip`.
- `voip-infra` — versioned Kamailio edge configuration and test harness.
- [`parrot-onboarding.md`](/home/odoo/Data/Dev/Odoo/parrot-onboarding.md) — living cross-system map;
  canonical twin in the Obsidian vault.
- [`parrot-local-testing-guide.md`](/home/odoo/Data/Dev/Odoo/parrot-local-testing-guide.md) — local
  Enterprise plus shared-staging workflow and triage guide.

## Official Odoo developer documentation

- [Developer documentation](https://www.odoo.com/documentation/master/developer.html)
- [Server framework 101](https://www.odoo.com/documentation/master/developer/tutorials/server_framework_101.html)
- [Backend ORM reference](https://www.odoo.com/documentation/master/developer/reference/backend.html)
- [Web framework reference](https://www.odoo.com/documentation/master/developer/reference/frontend.html)
- [Security reference](https://www.odoo.com/documentation/master/developer/reference/backend/security.html)
- [Testing reference](https://www.odoo.com/documentation/master/developer/reference/backend/testing.html)
- [Contributing](https://www.odoo.com/documentation/master/contributing.html)

## Telecom and provider primary sources

- [RFC 3261 — SIP](https://www.rfc-editor.org/rfc/rfc3261.html)
- [RFC 7118 — SIP over WebSocket](https://www.rfc-editor.org/rfc/rfc7118.html)
- [MDN WebRTC API](https://developer.mozilla.org/en-US/docs/Web/API/WebRTC_API)
- [Kamailio documentation](https://www.kamailio.org/w/documentation/)
- [Wazo Platform documentation](https://wazo-platform.org/documentation/)
- [Wazo source organization](https://github.com/wazo-platform)
- [Wazo Confd](https://github.com/wazo-platform/wazo-confd)
  Configuration service and REST API. Use for: distinguishing stored PBX intent from live call
  execution.
- [Wazo subroutines and pre-dial handlers](https://beta.wazo-platform.org/uc-doc/api_sdk/subroutine)
  Supported Asterisk extension points. Use for: custom dialplan behavior and outbound SIP headers.
- [Asterisk PJSIP_HEADER](https://docs.asterisk.org/Latest_API/API_Documentation/Dialplan_Functions/PJSIP_HEADER/)
  Authoritative channel/header semantics. Use for: proving why an outbound header belongs in a
  pre-dial handler.
- [Telnyx number orders](https://developers.telnyx.com/docs/numbers/phone-numbers/number-orders)
- [Telnyx advanced orders](https://developers.telnyx.com/docs/numbers/phone-numbers/advanced-orders)
- [Telnyx regulatory requirements](https://developers.telnyx.com/docs/numbers/phone-numbers/regulatory-requirements/index)
- [Telnyx SIP trunking](https://developers.telnyx.com/docs/voice/sip-trunking/get-started)
- [Telnyx webhooks](https://developers.telnyx.com/docs/voice/programmable-voice/voice-api-webhooks)

## Practitioner communities

- [Kamailio mailing lists](https://lists.kamailio.org/)
- [Asterisk Community](https://community.asterisk.org/)
- [Wazo community links](https://wazo-platform.org/)

## Known evidence gaps

- Automated edge tests prove signaling configuration; real audio still needs an integration call.
- Shared staging proves the configured environment at one moment, not production readiness.
- IAP Phone Service release/merge status is changeable; verify the current remote state before making
  an external status claim.
