# Setup

The distro used at time of writing: **Ubuntu 26.04 LTS**

## Adding Kamailio APT repository

First get and store the Kamailio signing key.
```bash
apt install gpg
wget -qO- https://deb.kamailio.org/kamailiodebkey.gpg | gpg --dearmor -o /usr/share/keyrings/kamailio.gpg
```

Then create a new file `/etc/apt/sources.list.d/kamailio.sources` with the content:
```
## See the sources.list(5) manual page for further settings.
Types: deb deb-src
URIs: http://deb.kamailio.org/kamailio61
Suites: resolute
Components: main
Signed-By: /usr/share/keyrings/kamailio.gpg
```

!!! tip "Note that `kamailio61` means the Kamailio v6.1 version."

!!! info "Also, `Suites: resolute` is the codename of the Ubuntu 26.04 distro."

Then do not forget to take into account the new APT repository by running:
```bash
apt update
```

## Package Installation

```bash
apt install kamailio
apt install kamailio-utils-modules curl # for http_client.so module
apt install kamailio-extra-modules libjansson4 # for jansson.so module
# for tls.so, outbound.so and websocket.so modules
apt install kamailio-tls-modules kamailio-outbound-modules kamailio-websocket-modules
apt install rsync # (optional, only if you want to rsync things)
```

There are many Kamailio packages specific for various modules. You can see all available with:
```bash
apt search kamailio
```

## Getting Started

To understand the core principles of the Kamailio configuration, read the official [getting started guide](https://www.kamailio.org/wikidocs/tutorials/getting-started/main/).

## Configuration Files

Kamailio configuration file is not just a set of 'parameter=value' line. It has active components for runtime, named routing blocks. A routing block is a group of actions that specify what should be done for each SIP message.

The actions are exported by Kamailio core or modules and are like functions exported by a library. Those actions can be combined in conditional statements like IF and SWITCH or in loops like WHILE. Modularity is provided by the ability to execute a routing block from another routing block.

!!! tip
    To copy all these configuration files, you can use:
    ```bash
    scp -r ./_etc_kamailio/* root@voip.test.odoo.com:/etc/kamailio/
    ```
    Or, to keep the folder in sync (transfers only what changed and removes files deleted locally), use `rsync` over SSH:
    ```bash
    rsync -avz --delete ./_etc_kamailio/ root@voip.test.odoo.com:/etc/kamailio/
    ```
    After copying the configuration files, the Kamailio service needs to be restarted for the changes to take effect. You can do this remotely over SSH:
    ```bash
    ssh root@voip.test.odoo.com systemctl restart kamailio
    ```
    To sync from local to the server and restart in a single command:
    ```bash
    rsync -avz --delete ./_etc_kamailio/ root@voip.test.odoo.com:/etc/kamailio/ && ssh root@voip.test.odoo.com systemctl restart kamailio
    ```

## Edge configuration

This deployment runs Kamailio as a **stateless, horizontally-scalable edge SIP
proxy** (no database, no media). It bridges three worlds — browsers (WebRTC over
WSS), the **Telnyx** carrier trunk, and per-region **Wazo** PBXes — and asks
**IAP Services** over REST who owns a number and whether a tenant may place a
call. Media (RTP/DTLS-SRTP) never traverses the edge.

### Certs

> /etc/ssl/kamailio/{fullchain,privkey}.pem = fixed paths awaited by tls.cfg;
> Symlink them onto the real X.509 cert pair.

```bash
install -d -m 755 /etc/ssl/kamailio
ln -sfn ../_.voip.odoo.com.crt /etc/ssl/kamailio/fullchain.pem
ln -sfn ../_.voip.odoo.com.key /etc/ssl/kamailio/privkey.pem
```

> private key: readable by the user that started the kamailio service, not everybody

```bash
chown <user>:kamailio /etc/ssl/_.voip.odoo.com.key
chmod 640 /etc/ssl/_.voip.odoo.com.key
systemctl restart kamailio
```


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

### HAProxy front (WSS termination + PROXY protocol)

Browsers connect over `wss://`. **HAProxy** terminates TLS and forwards plain
`ws` to Kamailio's `:8080` socket, prepending the **PROXY protocol** header
(`send-proxy-v2`) so Kamailio (`tcp_accept_haproxy=yes`) learns the real client
IP. The WebSocket upgrade is an HTTP `GET` with no `Content-Length`, so the edge
sets `tcp_accept_no_cl=yes` (gated on `WITH_WEBSOCKET`).

Place the TLS certificate at the path referenced by the `bind ... ssl crt`
line and adjust the `server` line to point at the local Kamailio `ws` socket.
