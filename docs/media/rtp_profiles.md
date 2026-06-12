# RTP Profiles

The third field of the `m=` line specifies the **RTP profile**.

Example:

```sdp
m=audio 40000 RTP/AVP 0 8 101
```

Here:

| Part      | Meaning       |
| --------- | ------------- |
| `audio`   | Media type    |
| `40000`   | RTP port      |
| `RTP/AVP` | RTP profile   |
| `0 8 101` | Payload types |

The RTP profile defines **how RTP packets should be interpreted and what additional features are available**.

---

## `RTP/AVP`

**Audio/Video Profile (AVP)**

```sdp
m=audio 40000 RTP/AVP 0 8
```

This is the original RTP profile defined for standard RTP.

Features:

* No media encryption
* Static and dynamic payload types
* Common in traditional SIP deployments

Typical codecs:

| Payload Type | Codec |
| ------------ | ----- |
| `0`          | PCMU  |
| `8`          | PCMA  |
| `9`          | G722  |
| `18`         | G729  |

This is one of the most common profiles in classic VoIP.

---

## `RTP/AVPF`

**Audio/Video Profile with Feedback**

```sdp
m=video 50000 RTP/AVPF 96
```

AVPF extends AVP by adding RTP feedback mechanisms.

Examples of feedback messages:

* Picture Loss Indication (PLI)
* Full Intra Request (FIR)
* Negative Acknowledgement (NACK)

These features are particularly useful for real-time video applications.

---

## `RTP/SAVP`

**Secure Audio/Video Profile**

```sdp
m=audio 40000 RTP/SAVP 0 8
```

SAVP is AVP with SRTP (Secure RTP).

Features:

* RTP payload encryption
* Message authentication
* Replay protection

This profile is used when media security is required.

---

## `RTP/SAVPF`

**Secure Audio/Video Profile with Feedback**

```sdp
m=audio 40000 RTP/SAVPF 111
```

SAVPF combines:

* SRTP encryption
* RTP feedback extensions

This profile is widely used by WebRTC.

---

## `UDP/TLS/RTP/SAVP`

```sdp
m=audio 9 UDP/TLS/RTP/SAVP 111
```

This profile indicates that:

* RTP is protected by SRTP
* DTLS is used to exchange encryption keys
* Media is transported over UDP

This is common in secure WebRTC deployments.

---

## `UDP/TLS/RTP/SAVPF`

```sdp
m=audio 9 UDP/TLS/RTP/SAVPF 111
```

This is the most common RTP profile found in WebRTC.

It provides:

* SRTP encryption
* DTLS key negotiation
* RTP feedback mechanisms
* Real-time media optimization

Modern browsers typically use this profile.

---

## What is the difference between AVP and AVPF?

| Profile | RTP Feedback |
| ------- | ------------ |
| AVP     | No           |
| AVPF    | Yes          |

AVPF allows endpoints to exchange control messages that improve media quality, especially for video streams.

---

## What is the difference between AVP and SAVP?

| Profile | Encryption |
| ------- | ---------- |
| AVP     | No         |
| SAVP    | Yes (SRTP) |

SAVP protects media from eavesdropping and tampering.

---

## Comparison table

| Profile           | Secure | Feedback | Typical Usage           |
| ----------------- | ------ | -------- | ----------------------- |
| RTP/AVP           | No     | No       | Traditional SIP         |
| RTP/AVPF          | No     | Yes      | Advanced video          |
| RTP/SAVP          | Yes    | No       | Secure SIP              |
| RTP/SAVPF         | Yes    | Yes      | Secure video and WebRTC |
| UDP/TLS/RTP/SAVP  | Yes    | No       | DTLS-SRTP               |
| UDP/TLS/RTP/SAVPF | Yes    | Yes      | Modern WebRTC           |

---

## Which profile should I expect?

### Traditional SIP phones

Most commonly:

```sdp
m=audio 40000 RTP/AVP 0 8 101
```

### Secure SIP deployments

Often:

```sdp
m=audio 40000 RTP/SAVP 0 8
```

### WebRTC

Typically:

```sdp
m=audio 9 UDP/TLS/RTP/SAVPF 111 0 8 101
```

---

!!! tip

    The RTP profile tells you much more than just "RTP".
    It immediately indicates whether the media is encrypted, whether RTP feedback is available, and whether the session is likely a traditional SIP call or a WebRTC connection.
