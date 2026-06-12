# SDP

SDP means **Session Description Protocol**.

It is not used to transport media.
It is used to **describe a media session**.

In VoIP, SDP is usually carried inside SIP messages such as:

* `INVITE`
* `200 OK`
* `ACK`
* sometimes `UPDATE` or `re-INVITE`

SDP answers questions like:

* What media type is used? Audio? Video?
* Which IP address should receive RTP?
* Which port should receive RTP?
* Which codecs are supported?
* Which codec was selected?
* Is the media encrypted?
* Is the media sent, received, or both?

## Example

```sdp
v=0
o=- 3747 3747 IN IP4 192.168.1.20
s=-
c=IN IP4 192.168.1.20
t=0 0
m=audio 40000 RTP/AVP 0 8 101
a=rtpmap:0 PCMU/8000
a=rtpmap:8 PCMA/8000
a=rtpmap:101 telephone-event/8000
a=fmtp:101 0-16
a=sendrecv
```

## Global structure

An SDP body is made of lines.

Each line has the following format:

```text
<letter>=<value>
```

Example:

```text
m=audio 40000 RTP/AVP 0 8 101
```

The letter before `=` defines the type of field.

Some fields describe the whole session.
Some fields describe one specific media stream.

## Session-level fields

### `v=` — Protocol version

```sdp
v=0
```

This is the SDP protocol version.

In practice, it is almost always:

```sdp
v=0
```

## `o=` — Origin

```sdp
o=- 3747 3747 IN IP4 192.168.1.20
```

The `o=` line identifies the creator of the SDP session.

Format:

```text
o=<username> <session-id> <session-version> <network-type> <address-type> <address>
```

Example:

```sdp
o=- 3747 3747 IN IP4 192.168.1.20
```

Meaning:

| Part           | Meaning                         |
| -------------- | ------------------------------- |
| `-`            | Username. `-` means no username |
| `3747`         | Session ID                      |
| `3747`         | Session version                 |
| `IN`           | Internet                        |
| `IP4`          | IPv4                            |
| `192.168.1.20` | Origin address                  |

The **session version** is important during re-INVITEs.
If the SDP changes, this value should increase.

!!! note

    ## `session-id` vs `session-version`

    The `o=` (origin) line has the following format:

    ```text
    o=<username> <session-id> <session-version> <network-type> <address-type> <address>
    ```

    Example:

    ```sdp
    o=- 123456789 1 IN IP4 192.168.1.20
    ```

    | Field           | Value          |
    | --------------- | -------------- |
    | Username        | `-`            |
    | Session ID      | `123456789`    |
    | Session Version | `1`            |
    | Network Type    | `IN`           |
    | Address Type    | `IP4`          |
    | Address         | `192.168.1.20` |

    ### `session-id`

    The **session-id** uniquely identifies an SDP session.

    It is created when the session is first established and should normally **remain unchanged** for the lifetime of that session.

    For example, if a call is put on hold or a codec changes, the `session-id` should still be the same.

    ### `session-version`

    The **session-version** is a revision number.

    Every time the SDP description changes, this value should be incremented.

    Typical reasons for increasing the session version include:

    * putting a call on hold
    * resuming a call
    * changing codecs
    * adding or removing a media stream
    * changing RTP ports
    * modifying media attributes

    ### Example

    Initial SDP:

    ```sdp
    o=- 123456789 1 IN IP4 192.168.1.20
    ```

    Call placed on hold:

    ```sdp
    o=- 123456789 2 IN IP4 192.168.1.20
    a=sendonly
    ```

    Video stream added:

    ```sdp
    o=- 123456789 3 IN IP4 192.168.1.20
    m=video 50000 RTP/AVP 96
    ```

    Notice that:

    * the **session-id** (`123456789`) never changes
    * the **session-version** increases (`1`, `2`, `3`)

    ### Why are they often the same number?

    Many examples and SIP implementations initialize both fields with the same value, often using a timestamp:

    ```sdp
    o=- 1749723000 1749723000 IN IP4 192.168.1.20
    ```

    After the SDP is modified, only the session version should change:

    ```sdp
    o=- 1749723000 1749723001 IN IP4 192.168.1.20
    ```

    ### Why does this matter?

    The remote endpoint can quickly determine whether it is dealing with:

    * **the same session** (same `session-id`)
    * **an updated SDP description** (higher `session-version`)

    This mechanism is especially important during SIP re-INVITEs and UPDATE requests.


## `s=` — Session name

```sdp
s=-
```

The session name is mandatory in SDP.

In VoIP, it is often unused, so we commonly see:

```sdp
s=-
```

## `c=` — Connection information

```sdp
c=IN IP4 192.168.1.20
```

The `c=` line tells the remote side where to send media.

Format:

```text
c=<network-type> <address-type> <connection-address>
```

Example:

```sdp
c=IN IP4 192.168.1.20
```

Meaning:

| Part           | Meaning                             |
| -------------- | ----------------------------------- |
| `IN`           | Internet                            |
| `IP4`          | IPv4                                |
| `192.168.1.20` | IP address where RTP should be sent |

This field can appear at session level or media level.

If it appears at session level, it applies to all media streams unless overridden.

## `t=` — Timing

```sdp
t=0 0
```

The `t=` line describes when the session is active.

In VoIP calls, we usually see:

```sdp
t=0 0
```

This means the session is permanent or not bounded by a specific start/end time.

## Media-level fields

## `m=` — Media description

```sdp
m=audio 40000 RTP/AVP 0 8 101
```

The `m=` line describes a media stream.

Format:

```text
m=<media> <port> <protocol> <formats>
```

Example:

```sdp
m=audio 40000 RTP/AVP 0 8 101
```

Meaning:

| Part      | Meaning       |
| --------- | ------------- |
| `audio`   | Media type    |
| `40000`   | RTP port      |
| `RTP/AVP` | [RTP profile](rtp_profiles.md) |
| `0 8 101` | Payload types |

In this example, the endpoint wants to receive audio on port `40000`.

The payload types are codec identifiers.

Common static payload types:

| Payload type | Codec              |
| ------------ | ------------------ |
| `0`          | PCMU / G.711 μ-law |
| `8`          | PCMA / G.711 A-law |
| `9`          | G722               |
| `18`         | G729               |

Dynamic payload types are usually in the range `96-127`.

Example:

```sdp
m=audio 40000 RTP/AVP 96
a=rtpmap:96 opus/48000/2
```

Here, payload type `96` means Opus for this specific session.

## `a=` — Attributes

The `a=` lines add extra information.

They are heavily used in VoIP.

## `a=rtpmap`

```sdp
a=rtpmap:0 PCMU/8000
a=rtpmap:8 PCMA/8000
a=rtpmap:101 telephone-event/8000
```

`rtpmap` maps a payload type to a codec.

Format:

```text
a=rtpmap:<payload-type> <encoding-name>/<clock-rate>[/channels]
```

Example:

```sdp
a=rtpmap:0 PCMU/8000
```

Meaning:

| Part   | Meaning      |
| ------ | ------------ |
| `0`    | Payload type |
| `PCMU` | Codec        |
| `8000` | Clock rate   |

For stereo codecs, we may see:

```sdp
a=rtpmap:96 opus/48000/2
```

Meaning:

| Part    | Meaning              |
| ------- | -------------------- |
| `96`    | Dynamic payload type |
| `opus`  | Codec                |
| `48000` | Clock rate           |
| `2`     | Number of channels   |

## `a=fmtp`

```sdp
a=fmtp:101 0-16
```

`fmtp` means **format parameters**.

It provides codec-specific parameters.

Example with DTMF:

```sdp
a=fmtp:101 0-16
```

This means payload type `101` supports DTMF events `0` to `16`.

Example with Opus:

```sdp
a=fmtp:96 minptime=10;useinbandfec=1
```

The meaning depends on the codec.

## `a=sendrecv`, `a=sendonly`, `a=recvonly`, `a=inactive`

These attributes describe media direction.

### `a=sendrecv`

```sdp
a=sendrecv
```

Both sides can send and receive media.

This is the normal state for a phone call.

### `a=sendonly`

```sdp
a=sendonly
```

The endpoint only sends media.

This is often used when putting the remote party on hold.

### `a=recvonly`

```sdp
a=recvonly
```

The endpoint only receives media.

This is often the opposite side of a hold scenario.

### `a=inactive`

```sdp
a=inactive
```

No media is sent or received.

## `a=ptime`

```sdp
a=ptime:20
```

Packetization time.

It indicates the preferred duration of audio in each RTP packet, in milliseconds.

Example:

```sdp
a=ptime:20
```

This means each RTP packet should contain 20 ms of audio.

## `a=maxptime`

```sdp
a=maxptime:60
```

Maximum packetization time.

It indicates the maximum duration of audio that can be placed in one RTP packet.

## `a=telephone-event`

DTMF tones are often sent using RTP events instead of audio tones.

Example:

```sdp
m=audio 40000 RTP/AVP 0 8 101
a=rtpmap:101 telephone-event/8000
a=fmtp:101 0-16
```

Here:

| Payload type | Meaning               |
| ------------ | --------------------- |
| `101`        | RTP telephone-event   |
| `0-16`       | Supported DTMF events |

This is used for digits like `0`, `1`, `2`, `*`, `#`, etc.

## SDP offer/answer

SIP commonly uses the SDP offer/answer model.

Example:

1. Caller sends an `INVITE` with SDP offer.
2. Callee replies with `200 OK` containing SDP answer.
3. Caller sends `ACK`.
4. RTP media starts using the negotiated IPs, ports, and codecs.

Simplified flow:

```text
Caller                         Callee
  |                               |
  | INVITE + SDP offer            |
  |------------------------------>|
  |                               |
  | 200 OK + SDP answer           |
  |<------------------------------|
  |                               |
  | ACK                           |
  |------------------------------>|
  |                               |
  | RTP media                     |
  |<=============================>|
```

## Codec negotiation

Example offer:

```sdp
m=audio 40000 RTP/AVP 0 8 101
a=rtpmap:0 PCMU/8000
a=rtpmap:8 PCMA/8000
a=rtpmap:101 telephone-event/8000
```

The caller offers:

| Payload type | Codec           |
| ------------ | --------------- |
| `0`          | PCMU            |
| `8`          | PCMA            |
| `101`        | telephone-event |

Example answer:

```sdp
m=audio 50000 RTP/AVP 8 101
a=rtpmap:8 PCMA/8000
a=rtpmap:101 telephone-event/8000
```

The callee accepts:

| Payload type | Codec           |
| ------------ | --------------- |
| `8`          | PCMA            |
| `101`        | telephone-event |

The call will use PCMA for audio.

## RTP ports

The port in the `m=` line is the port where the endpoint expects to receive RTP.

Example:

```sdp
m=audio 40000 RTP/AVP 0 8
```

This means:

```text
Send RTP audio to port 40000.
```

RTCP may use the next port, depending on configuration and protocol profile.

For example:

```text
RTP  -> 40000
RTCP -> 40001
```

However, this is not always guaranteed. Some systems use explicit RTCP attributes.

## `a=rtcp`

```sdp
a=rtcp:40001
```

This explicitly defines the RTCP port.

Example:

```sdp
m=audio 40000 RTP/AVP 0
a=rtcp:40001
```

Meaning:

| Protocol | Port    |
| -------- | ------- |
| RTP      | `40000` |
| RTCP     | `40001` |

## IPv4 and IPv6

IPv4 example:

```sdp
c=IN IP4 192.168.1.20
```

IPv6 example:

```sdp
c=IN IP6 2001:db8::1
```

## NAT problems

SDP contains IP addresses and ports.

This is important because SIP signaling and RTP media are separate.

A common problem is private IP addresses inside SDP.

Example:

```sdp
c=IN IP4 192.168.1.20
m=audio 40000 RTP/AVP 0 8
```

If the remote endpoint is on the public Internet, it cannot send RTP to `192.168.1.20`.

Symptoms:

* one-way audio
* no audio
* call connects but media is missing
* RTP is sent to the wrong IP

Solutions usually involve:

* correct NAT configuration
* RTP rewriting
* STUN/TURN/ICE for WebRTC
* media relay
* SBC
* Asterisk `external_media_address`
* Asterisk `local_net`

## Hold

A call can be placed on hold by changing SDP direction.

Common examples:

```sdp
a=sendonly
```

or:

```sdp
a=inactive
```

Older systems may also use:

```sdp
c=IN IP4 0.0.0.0
```

Modern implementations usually prefer direction attributes.

## Multiple media streams

SDP can describe multiple media streams.

Example with audio and video:

```sdp
v=0
o=- 1234 1234 IN IP4 192.168.1.20
s=-
c=IN IP4 192.168.1.20
t=0 0
m=audio 40000 RTP/AVP 0 8
a=rtpmap:0 PCMU/8000
a=rtpmap:8 PCMA/8000
m=video 50000 RTP/AVP 96
a=rtpmap:96 VP8/90000
```

Here there are two media streams:

| Media |    Port | Codec       |
| ----- | ------: | ----------- |
| Audio | `40000` | PCMU / PCMA |
| Video | `50000` | VP8         |

## Secure RTP

For encrypted media, SDP may contain crypto or fingerprint attributes.

## `RTP/SAVP`

```sdp
m=audio 40000 RTP/SAVP 0 8
```

`RTP/SAVP` means RTP with security.

## `RTP/SAVPF`

```sdp
m=audio 40000 RTP/SAVPF 111
```

`RTP/SAVPF` is common with WebRTC.

## `a=fingerprint`

```sdp
a=fingerprint:sha-256 12:34:56:...
```

Used by DTLS-SRTP.

This is common in WebRTC.

## `a=setup`

```sdp
a=setup:actpass
```

Used to negotiate the DTLS role.

Common values:

| Value     | Meaning                   |
| --------- | ------------------------- |
| `actpass` | Can be active or passive  |
| `active`  | Initiates DTLS connection |
| `passive` | Waits for DTLS connection |

## ICE candidates

WebRTC uses ICE to find the best media path.

Example:

```sdp
a=ice-ufrag:abc123
a=ice-pwd:xyz456
a=candidate:1 1 UDP 2130706431 192.168.1.20 50000 typ host
```

## `a=ice-ufrag`

```sdp
a=ice-ufrag:abc123
```

ICE username fragment.

## `a=ice-pwd`

```sdp
a=ice-pwd:xyz456
```

ICE password.

## `a=candidate`

```sdp
a=candidate:1 1 UDP 2130706431 192.168.1.20 50000 typ host
```

An ICE candidate describes a possible network path for media.

A candidate can be:

| Type    | Meaning                                               |
| ------- | ----------------------------------------------------- |
| `host`  | Local interface address                               |
| `srflx` | Server reflexive address, usually discovered via STUN |
| `relay` | Relayed address, usually through TURN                 |

## `a=end-of-candidates`

```sdp
a=end-of-candidates
```

Indicates that no more ICE candidates will be sent.

## WebRTC SDP example

```sdp
v=0
o=- 4611733056616230011 2 IN IP4 127.0.0.1
s=-
t=0 0
a=group:BUNDLE 0
a=msid-semantic: WMS
m=audio 9 UDP/TLS/RTP/SAVPF 111 0 8 101
c=IN IP4 0.0.0.0
a=rtcp:9 IN IP4 0.0.0.0
a=ice-ufrag:abc123
a=ice-pwd:xyz456
a=fingerprint:sha-256 12:34:56:78:90
a=setup:actpass
a=mid:0
a=sendrecv
a=rtpmap:111 opus/48000/2
a=rtpmap:0 PCMU/8000
a=rtpmap:8 PCMA/8000
a=rtpmap:101 telephone-event/8000
a=fmtp:101 0-16
a=candidate:1 1 UDP 2130706431 192.168.1.20 50000 typ host
a=end-of-candidates
```

Important differences with classic SIP/RTP:

| Classic SIP/RTP            | WebRTC                              |
| -------------------------- | ----------------------------------- |
| Often `RTP/AVP`            | Usually `UDP/TLS/RTP/SAVPF`         |
| RTP can be unencrypted     | Media must be encrypted             |
| Usually no ICE             | ICE is used                         |
| Direct RTP port in `m=`    | Port may be `9` with ICE candidates |
| Codecs like PCMA/PCMU/G722 | Opus is common                      |

## Common SDP fields

| Field | Meaning                                         |
| ----- | ----------------------------------------------- |
| `v=`  | SDP version                                     |
| `o=`  | Origin                                          |
| `s=`  | Session name                                    |
| `c=`  | Connection information                          |
| `t=`  | Timing                                          |
| `m=`  | Media description                               |
| `a=`  | Attribute                                       |
| `b=`  | Bandwidth                                       |
| `i=`  | Information                                     |
| `u=`  | URI                                             |
| `e=`  | Email                                           |
| `p=`  | Phone                                           |
| `r=`  | Repeat times                                    |
| `z=`  | Time zone adjustment                            |
| `k=`  | Encryption key, obsolete and should not be used |

## Common VoIP attributes

| Attribute             | Meaning                                        |
| --------------------- | ---------------------------------------------- |
| `a=rtpmap`            | Payload type to codec mapping                  |
| `a=fmtp`              | Codec-specific parameters                      |
| `a=sendrecv`          | Send and receive media                         |
| `a=sendonly`          | Send only                                      |
| `a=recvonly`          | Receive only                                   |
| `a=inactive`          | No media                                       |
| `a=ptime`             | Packetization time                             |
| `a=maxptime`          | Maximum packetization time                     |
| `a=rtcp`              | RTCP port                                      |
| `a=fingerprint`       | DTLS fingerprint                               |
| `a=setup`             | DTLS role negotiation                          |
| `a=ice-ufrag`         | ICE username fragment                          |
| `a=ice-pwd`           | ICE password                                   |
| `a=candidate`         | ICE candidate                                  |
| `a=end-of-candidates` | End of ICE candidates                          |
| `a=mid`               | Media identifier                               |
| `a=group:BUNDLE`      | Bundle multiple media streams on one transport |

## Troubleshooting checklist

When debugging SDP, check:

1. Is the IP address in `c=` reachable?
2. Is the RTP port in `m=` reachable?
3. Are the codecs compatible?
4. Is the selected payload type correctly mapped with `a=rtpmap`?
5. Is DTMF negotiated with `telephone-event`?
6. Is the media direction correct?
7. Is the call on hold?
8. Is SRTP required by one side but not the other?
9. For WebRTC, are ICE candidates present?
10. For WebRTC, is DTLS fingerprint present?
11. Is NAT rewriting required?
12. Is Asterisk using the correct external media address?

## Example: no audio because of private IP

Bad SDP:

```sdp
c=IN IP4 192.168.1.50
m=audio 30000 RTP/AVP 0
```

Problem:

The remote side is on the public Internet and cannot reach `192.168.1.50`.

Possible result:

```text
SIP call is connected, but there is no audio.
```

## Example: codec mismatch

Offer:

```sdp
m=audio 40000 RTP/AVP 0
a=rtpmap:0 PCMU/8000
```

Answer:

```sdp
m=audio 50000 RTP/AVP 8
a=rtpmap:8 PCMA/8000
```

Problem:

The answer selected `PCMA`, but the offer only proposed `PCMU`.

The answer should only select codecs that were present in the offer.

## Example: rejected media stream

```sdp
m=audio 0 RTP/AVP 0
```

A port set to `0` means the media stream is rejected or disabled.

## Asterisk notes

In Asterisk/PJSIP, SDP problems are often related to:

* endpoint codec configuration
* NAT settings
* transport configuration
* WebRTC profile
* SRTP settings
* direct media
* external media address
* local networks

Useful Asterisk CLI commands:

```bash
pjsip set logger on
rtp set debug on
rtp set debug off
core set verbose 5
core set debug 5
```

Useful files or settings to check:

```text
pjsip.conf
rtp.conf
external_media_address
external_signaling_address
local_net
allow
disallow
media_encryption
webrtc
direct_media
```

## Summary

SDP describes the media part of a call.

SIP decides who calls whom.
SDP decides how media should flow.

In most VoIP debugging sessions, SDP helps answer:

```text
Where should RTP be sent?
Which port should be used?
Which codec should be used?
Is media encrypted?
Is the call on hold?
Is NAT breaking the media path?
```
