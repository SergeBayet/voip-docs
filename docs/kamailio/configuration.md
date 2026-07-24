# Configuration

This deployment runs Kamailio as a **stateless, horizontally-scalable edge SIP
proxy** (no database, no media). It bridges three worlds — browsers (WebRTC over
WSS), the **Telnyx** carrier trunk, and per-region **Wazo** PBXes — and asks
**IAP Services** over REST who owns a number and whether a tenant may place a
call. Media (RTP/DTLS-SRTP) never traverses the edge.

## Configuration Files

Kamailio configuration file is not just a set of 'parameter=value' line. It has active components for runtime, named routing blocks. A routing block is a group of actions that specify what should be done for each SIP message.

The actions are exported by Kamailio core or modules and are like functions exported by a library. Those actions can be combined in conditional statements like IF and SWITCH or in loops like WHILE. Modularity is provided by the ability to execute a routing block from another routing block.

!!! tip
    To copy all these configuration files, you can put yourself in the root of `brboi/voip-infra` GH repo and use:
    ```bash
    scp -r ./conf/kamailio/etc/kamailio/* root@edge-XXX.voip.test.odoo.com:/etc/kamailio/
    ```
    Or, to keep the folder in sync (transfers only what changed and removes files deleted locally), use `rsync` over SSH:
    ```bash
    rsync -avz ./conf/kamailio/etc/kamailio/ root@edge-XXX.voip.test.odoo.com:/etc/kamailio/
    ```
    The first time you also must configure the systemd kamailio service itself:
    ```bash
    rsync -avz ./conf/kamailio/etc/systemd/system/kamailio.service.d/ root@edge-XXX.voip.test.odoo.com:/etc/systemd/system/kamailio.service.d/ && ssh root@edge-XXX.voip.test.odoo.com systemctl daemon-reload
    ```
    After copying the configuration files, the Kamailio service needs to be restarted for the changes to take effect. You can do this remotely over SSH:
    ```bash
    ssh root@edge-XXX.voip.test.odoo.com systemctl restart kamailio
    ```
    To sync from local to the server and restart in a single command:
    ```bash
    rsync -avz ./conf/kamailio/etc/kamailio/ root@edge-XXX.voip.test.odoo.com:/etc/kamailio/ && ssh root@edge-XXX.voip.test.odoo.com systemctl restart kamailio
    ```

## Environment Variables
`/etc/kamailio/edge.env` file must contain:
```conf
NODE_ADVERTISE_FQDN=voip.test.odoo.com # The FQDN of this edge node
NODE_ADVERTISE_IP=x.y.z.a # The public IP address of this edge node
IAP_PHONE_SERVICE_BASE_URL=https://iap-services.odoo.com # The base url of the IAP Phone Service
TELNYX_HOST=sip.telnyx.com
TELNYX_PORT=5061
TELNYX_TRANSPORT=tls
# RFC 5626 flow-token signing secret (any long random string; identical on every node).
FLOW_TOKEN_SECRET=change-me-to-a-long-random-string
# Shared secret for IAP REST authentication — must match the IAP side.
EDGE_TOKEN=changeme
```

# --- BELOW DOCUMENTATION IN REVIEW ---

### Load order and entry point

`kamailio.cfg` is the entry point. It defines the feature toggles and flags, then
`import_file`s the rest in this order:

1. `custom_params.cfg` — operator-editable environment values (loaded **before**
   `globals.cfg` so its `#!define`s are visible everywhere).
2. `globals.cfg` — core/global parameters (`listen` sockets, TCP/PROXY-protocol).
3. `modules.cfg` — module loading + module parameters.
4. `routes.cfg` — `include_file`s every routing block under `routes/`.

!!! warning "Validate before deploying"
    Run `./docs/kamailio/check-config.sh` (loads the config in the official
    `ghcr.io/kamailio/kamailio:6.1.3-resolute` image via `kamailio -c`). A green
    run ends with `config file ok, exiting...` and exit code `0`.

### Environment `#!define`s an operator must set

These live in **`custom_params.cfg`** and must be set per deployment before the
edge will route correctly:

| Define | Purpose |
|--------|---------|
| `UDP_ADVERTISE_ADDR` | This node's **per-replica** address (FQDN or IP) routable from Wazo/Telnyx. Stamped into **Path** (on REGISTER) and **Record-Route** so the second leg of an inbound call returns to the exact replica holding the browser's WebSocket. Must be the node address, **not** the shared load-balancer VIP. Defined with `#!define` (not `#!subst`, which is not applied across `import_file`). |
| `IAP_BASE_URL` | Base URL of the IAP Services REST API (number→tenant→PBX, credit, allowed CLIs). Expected on the same LAN; called synchronously with a short timeout. |
| `TELNYX_SIP_TARGET` | The Telnyx signalling target URI for outbound calls (v0: a single UDP connection). |
| `TELNYX_SRC_IP_1`, `TELNYX_SRC_IP_2` | Trusted Telnyx source IPs (IP-auth allow-list; no DB). Inbound INVITEs are accepted only from these. |
| `WAZO_SRC_IP` | Trusted Wazo trunk source IP (IP-auth). The edge trusts the `X-Tenant-ID` header **only** from this source, never the browser's `From`. |
| `WAZO_FALLBACK_FQDN` | Bring-up fallback Wazo used when IAP returns no mapping (lets you test before IAP is live). |

TLS certificate path: the browser leg is **WSS terminated at HAProxy**, so the
certificate lives on HAProxy (`/etc/haproxy/certs/...`, see below), **not** on
Kamailio. Kamailio loads no `tls` module on the browser side.

### Routing blocks (`routes/`)

The edge replaces the default registrar/location/presence/pstn/voicemail routing
with a small set of edge blocks (the default files remain on disk for reference
but are not included):

| File | Role |
|------|------|
| `request_main.cfg` | Top-level `request_route`: sanity, CANCEL, in-dialog, REGISTER, then source classification (Telnyx / Wazo / WS) → the matching flow. |
| `reqinit.cfg` | Per-request initial checks; `set_contact_alias()` for WS REGISTER. |
| `trunks.cfg` | Classify the source by IP (`FROM_TELNYX` / `FROM_WAZO`) or transport (`FROM_WS`). |
| `iap.cfg` | `IAP_BY_NUMBER` / `IAP_BY_USER` REST lookups with in-RAM `htable` caching + **negative caching**. The argument is passed in `$var(iap_arg)` (this build's parser does not accept `route(NAME, "param")`); the result is read from `$rc`. |
| `register.cfg` | Relay REGISTER to the user's Wazo (IAP username→PBX), insert **Path**, delegate auth (pass the `401` through). |
| `inbound.cfg` | Telnyx → Wazo: `To`→IAP lookup, credit gate, `record_route`, relay. |
| `outbound.cfg` | Wazo → Telnyx: trust `X-Tenant-ID`, credit gate, verify/normalise CLI via IAP, relay to Telnyx. |
| `ws.cfg` | Accept the WebSocket upgrade (`ws_handle_handshake()`). |
| `withindialog.cfg` | Stateless in-dialog routing via `loose_route()`; route back to a WS browser with `handle_ruri_alias()`. |
| `relay.cfg` | Signalling-only stateful relay (`t_relay`); no media handling. |
