# Audio Codecs in VoIP

In VoIP, the codec is responsible for encoding and decoding audio streams.
It directly impacts:

* Audio quality
* Bandwidth consumption
* CPU usage
* Latency
* Packet loss resilience
* Compatibility with phones/providers

Choosing the right codec depends on the use case:

* Internal LAN calls
* Mobile/WebRTC calls
* SIP trunk compatibility
* Low bandwidth environments
* Recording/transcoding requirements

---

# PCM Codecs (G.711)

These are the historical telephony codecs.

## G.711 μ-law (u-law)

64\ \text{kbps}

Mainly used in:

* North America
* Japan

### Characteristics

| Property    | Value      |
| ----------- | ---------- |
| Bitrate     | 64 kbps    |
| Sample rate | 8 kHz      |
| Compression | None (PCM) |
| Latency     | Very low   |
| CPU usage   | Minimal    |

### Advantages

* Excellent compatibility
* Very low CPU usage
* Near-zero codec latency
* Widely supported by SIP providers
* No transcoding needed in many PSTN environments

### Drawbacks

* Consumes significant bandwidth
* Narrowband only
* Poor resilience to packet loss
* Audio quality lower than modern codecs

### Typical Use Cases

* SIP trunks
* Legacy PBX
* PSTN interoperability
* Internal enterprise telephony

---

## G.711 A-law (a-law)

Very similar to μ-law, but mainly used in:

* Europe
* Most of the world outside North America/Japan

### Difference with μ-law

The companding algorithm differs slightly.

In practice:

* Audio quality is nearly identical
* Devices/providers often support both

### Advantages

Same as μ-law:

* Extremely compatible
* Simple
* Reliable
* Low latency

### Drawbacks

Same as μ-law:

* High bandwidth usage
* Narrowband audio only

---

# Compressed Narrowband Codecs

## G.729

8\ \text{kbps}

Historically extremely popular for WAN links.

### Characteristics

| Property    | Value    |
| ----------- | -------- |
| Bitrate     | 8 kbps   |
| Sample rate | 8 kHz    |
| Compression | High     |
| CPU usage   | Moderate |

### Advantages

* Very low bandwidth consumption
* Good voice quality for its bitrate
* Historically common in enterprise WANs

### Drawbacks

* Patent/licensing history
* Worse quality than Opus
* Narrowband only
* More CPU intensive than G.711
* Less common today

### Typical Use Cases

* Legacy low-bandwidth links
* Older SIP infrastructures

---

## G.723.1

Very aggressive compression codec.

### Characteristics

| Property | Value          |
| -------- | -------------- |
| Bitrate  | 5.3 / 6.3 kbps |
| Latency  | High           |

### Advantages

* Extremely low bandwidth usage

### Drawbacks

* High latency
* Noticeably degraded quality
* Heavy CPU usage
* Mostly obsolete today

### Typical Use Cases

* Rare legacy deployments

---

# Wideband / HD Voice Codecs

## G.722

64\ \text{kbps}

One of the most important HD voice codecs.

### Characteristics

| Property    | Value    |
| ----------- | -------- |
| Sample rate | 16 kHz   |
| Audio range | Wideband |
| Quality     | HD Voice |

### Advantages

* Excellent voice clarity
* Widely supported by enterprise phones
* Low CPU usage
* Good interoperability

### Drawbacks

* Higher bandwidth than compressed codecs
* Less efficient than Opus

### Typical Use Cases

* Enterprise VoIP
* Modern SIP phones
* Internal calls

---

# Modern Internet Codec

## Opus

Probably the most important modern VoIP codec.

Created for:

* WebRTC
* Real-time internet communications
* Gaming/streaming/VoIP

### Characteristics

| Property             | Value                 |
| -------------------- | --------------------- |
| Bitrate              | 6–510 kbps            |
| Audio                | Narrowband → Fullband |
| Latency              | Extremely low         |
| Packet loss handling | Excellent             |

### Advantages

* Outstanding audio quality
* Extremely flexible bitrate
* Excellent packet loss resilience
* Very low latency
* Ideal for unstable internet/mobile networks
* Supports voice AND music
* Mandatory in WebRTC

### Drawbacks

* Slightly higher CPU usage
* Not universally supported by old SIP hardware
* Some providers still prefer G.711

### Typical Use Cases

* WebRTC
* Browser softphones
* Mobile VoIP
* Modern conferencing
* Internet telephony

---

# Other Common Codecs

## GSM

Old codec inspired by GSM mobile networks.

### Advantages

* Low bandwidth
* Historically common

### Drawbacks

* Poor modern audio quality
* Obsolete

---

## iLBC

Internet Low Bitrate Codec.

Designed specifically for packet loss resilience.

### Advantages

* Good resilience on unstable networks

### Drawbacks

* Largely replaced by Opus

---

# Narrowband vs Wideband vs Fullband

| Type       | Audio Range  | Perceived Quality  |
| ---------- | ------------ | ------------------ |
| Narrowband | ~300–3400 Hz | Traditional phone  |
| Wideband   | ~50–7000 Hz  | HD Voice           |
| Fullband   | ~20–20000 Hz | Near natural audio |

---

# Transcoding

A PBX may need to transcode when:

* Caller codec ≠ callee codec
* SIP trunk only supports G.711
* WebRTC uses Opus
* Recording formats differ

Example:

```text
WebRTC Client (Opus)
        ↓
     Asterisk
        ↓ transcoding
SIP Provider (G.711 alaw)
```

## Important

Transcoding increases:

* CPU usage
* Latency
* Complexity

Avoid unnecessary transcoding when possible.

---

# Packet Loss Sensitivity

| Codec | Packet Loss Tolerance |
| ----- | --------------------- |
| G.711 | Poor                  |
| G.729 | Medium                |
| G.722 | Medium                |
| Opus  | Excellent             |
| iLBC  | Excellent             |

---

# WebRTC Reality

WebRTC almost always uses:

* Opus for audio
* VP8/VP9/H264 for video

This is why many modern VoIP systems internally use Opus and transcode only when communicating with SIP trunks.

---

# Recommended Choices

## Internal SIP infrastructure

Recommended:

* G.722
* Opus

## SIP Trunk Compatibility

Recommended:

* G.711 alaw (Europe)
* G.711 ulaw (US)

## WebRTC

Recommended:

* Opus

## Poor Networks / Mobile

Recommended:

* Opus

## Legacy Hardware

Recommended:

* G.711
* G.729

---

# Quick Comparison Table

| Codec       | Quality   | Bandwidth     | CPU      | Packet Loss | Compatibility | Modern?    |
| ----------- | --------- | ------------- | -------- | ----------- | ------------- | ---------- |
| G.711 u-law | Good      | High          | Very low | Poor        | Excellent     | Yes        |
| G.711 a-law | Good      | High          | Very low | Poor        | Excellent     | Yes        |
| G.729       | Medium    | Very low      | Medium   | Medium      | Good          | Aging      |
| G.723.1     | Low       | Extremely low | High     | Poor        | Legacy        | No         |
| G.722       | Very good | High          | Low      | Medium      | Very good     | Yes        |
| Opus        | Excellent | Flexible      | Medium   | Excellent   | Growing       | Absolutely |
| GSM         | Low       | Low           | Low      | Poor        | Legacy        | No         |
| iLBC        | Medium    | Low           | Medium   | Excellent   | Limited       | Aging      |

---

# Practical Recommendation

Today, a very common modern architecture is:

```text
WebRTC clients  → Opus
Internal SIP    → G.722
SIP Trunks      → G.711 alaw/ulaw
```

This gives:

* Excellent browser/mobile quality
* Good compatibility with providers
* Minimal transcoding where unavoidable
