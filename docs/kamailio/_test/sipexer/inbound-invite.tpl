INVITE {{.ruri}} SIP/2.0
Via: SIP/2.0/{{.viaproto}} {{.viaaddr}}{{.viaextra}};branch=z9hG4bK.{{.branchid}}
From: "telnyx" <sip:{{.fromuser}}@{{.fromdomain}}>;tag={{.fromtag}}
To: <{{.touri}}>
Call-ID: {{.callid}}
CSeq: {{.cseqnum}} INVITE
Contact: <sip:{{.fromuser}}@{{.viaaddr}}>
X-Tags: {{.xtags}}
Max-Forwards: 70
Subject: sipexer inbound test
Content-Type: application/sdp
Content-Length: {{.contentlength}}

{{.sdpbody}}
