# Kamailio Stateless Edge — P0 Verification Scenarios

> **Prerequisites for live execution:** A running edge (Kamailio + HAProxy up), IAP reachable (or stubbed
> with a tiny HTTP server returning the expected JSON), and Wazo reachable.
> These tests cannot be run in a dev-only environment without the full stack.

> **sipexer flag sensitivity:** Flag names below (`--template-file`, `-fv`, `-register`, `-t`, `-au`,
> `-ap`) match the common/current forms. sipexer is under active development and flag spellings can
> change between versions. **Always confirm with `sipexer -ex` and `sipexer --help` before scripting.**
> Adjust flag names to match your installed version.

---

## Tools

| Tool | Purpose |
|------|---------|
| `sipexer` | Primary SIP test client — speaks `ws`/`wss` natively, uses Go `text/template` templates |
| `sngrep` | Live SIP flow capture on the server |
| `kamcmd` | Runtime introspection of Kamailio state |

---

## Step 1: Start the edge and open SIP capture

```bash
sudo systemctl restart kamailio haproxy
sudo sngrep port 5060 or port 8080
```

Leave `sngrep` open in a separate terminal for all tests below.

---

## Step 2: REGISTER over WSS (validates WS handshake + REGISTER relay + Path + delegated 401)

No browser needed — sipexer speaks WSS natively.

```bash
# Replace creds with a real test user that Wazo accepts. Through HAProxy on :443.
sipexer -register -t wss \
  -fv "domain:voip.odoo.com" \
  -au "1001" -ap "<password>" \
  "wss://voip.odoo.com:443"
```

**Expected:** `200 OK` to the REGISTER.

**In `sngrep` confirm:**
- WS handshake OK
- REGISTER reaches Wazo with a `Path:` header containing `UDP_ADVERTISE_ADDR`
- The `401` is passed back and the authenticated retry returns `200 OK`

**Introspect:** `kamcmd ws.dump`

---

## Step 3: Inbound INVITE (simulates Telnyx → Wazo)

Send from a host whitelisted as `TELNYX_SRC_IP_*`. The DNIS must be a number IAP maps to your test tenant.

```bash
sipexer -t udp \
  --template-file docs/kamailio/_test/sipexer/inbound-invite.tpl \
  -fv "ruri:sip:+13125550123@voip.odoo.com" \
  -fv "touri:sip:+13125550123@voip.odoo.com" \
  -fv "xtags:tenant-test-001" \
  "udp:<edge_ip>:5060"
```

**Expected:** INVITE relayed to the correct `pbx_fqdn`.

**In `sngrep` + `xlog` confirm:**
- One IAP lookup, then a cache hit on the retry (`kamcmd htable.dump iapcache`)
- Credit gate passes
- INVITE relayed to the resolved Wazo with `Record-Route` present

**Negative tests:**
- An inactive-account number must return `403`
- An unknown number must return `404`

---

## Step 4: Outbound INVITE (simulates Wazo → Telnyx)

Send from the host whitelisted as `WAZO_SRC_IP`.

### 4a. CLI owned by the asserting tenant — passes through unchanged

```bash
sipexer -t udp \
  --template-file docs/kamailio/_test/sipexer/outbound-invite.tpl \
  -fv "ruri:sip:+442071234567@sip.telnyx.com" \
  -fv "touri:sip:+442071234567@sip.telnyx.com" \
  -fv "cli:+13125550123" \
  -fv "tenant:tenant-test-001" \
  "udp:<edge_ip>:5060"
```

**Expected:** INVITE relayed to `TELNYX_SIP_TARGET` with `From` unchanged.

### 4b. CLI NOT owned by the tenant — From rewritten to tenant default

```bash
sipexer -t udp \
  --template-file docs/kamailio/_test/sipexer/outbound-invite.tpl \
  -fv "ruri:sip:+442071234567@sip.telnyx.com" \
  -fv "touri:sip:+442071234567@sip.telnyx.com" \
  -fv "cli:+19998887777" \
  -fv "tenant:tenant-test-001" \
  "udp:<edge_ip>:5060"
```

**Expected:** INVITE relayed with `From` rewritten to the tenant's default DID.

### 4c. Missing X-Tenant-ID — rejected

Send using the outbound template without the `tenant` field (or set it to empty), or craft a raw INVITE without the header.

**Expected:** `403 Missing tenant assertion`.

**In `sngrep` + `xlog` confirm:** tenant trust and CLI authorisation behave as specified for all three sub-cases.

---

## Step 5: In-dialog teardown

After a real call (Step 6), hang up from each side. Confirm BYE is `loose_route`d and no transactions linger.

```bash
kamcmd tm.stats
```

**Expected:** `BYE` is forwarded without errors; `tm.stats` shows no stuck transactions after the call ends.

---

## Step 6: Two-way audio confirmation (browser or baresip)

> sipexer does not exercise the media path. This step requires a real SIP client.

Register a real `sip.js` browser (or `baresip`) and place/receive a call. Confirm:

- Audio flows Telnyx ⇆ Wazo ⇆ browser
- **Audio never passes through the edge** (edge is signalling-only; RTP goes direct between Telnyx and Wazo)

---

## Step 7: Statelessness check (no DB/disk state)

```bash
sudo lsof -p "$(pgrep -f 'kamailio.*-m' | head -1)" | grep -iE 'mysql|pgsql|\.db|/var/lib' || echo "no db/disk state — OK"
```

**Expected:** `no db/disk state — OK`

---

## Introspection reference

```bash
# Dump the IAP number cache
kamcmd htable.dump iapcache

# Dump the user→PBX cache
kamcmd htable.dump usercache

# List active WebSocket connections
kamcmd ws.dump

# Transaction stats
kamcmd tm.stats
```

---

## Template field reference

### `inbound-invite.tpl` custom fields (supply with `-fv`)

| Field | Description | Example |
|-------|-------------|---------|
| `xtags` | Telnyx X-Tags (tenant tag) | `tenant-test-001` |

Standard fields (`ruri`, `touri`, `fromuser`, `fromdomain`, `viaproto`, `viaaddr`, `viaextra`, `branchid`, `callid`, `cseqnum`, `fromtag`, `sdpbody`, `contentlength`) are auto-filled by sipexer.

### `outbound-invite.tpl` custom fields (supply with `-fv`)

| Field | Description | Example |
|-------|-------------|---------|
| `cli` | Presented caller ID (E.164) | `+13125550123` |
| `tenant` | Tenant assertion (X-Tenant-ID) | `tenant-test-001` |

Standard fields are auto-filled by sipexer.
