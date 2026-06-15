INVITE {{.ruri}} SIP/2.0
Via: SIP/2.0/{{.viaproto}} {{.viaaddr}}{{.viaextra}};branch=z9hG4bK.{{.branchid}}
From: <sip:{{.cli}}@{{.fromdomain}}>;tag={{.fromtag}}
To: <{{.touri}}>
Call-ID: {{.callid}}
CSeq: {{.cseqnum}} INVITE
Contact: <sip:{{.cli}}@{{.viaaddr}}>
X-Tenant-ID: {{.tenant}}
Max-Forwards: 70
Subject: sipexer outbound test
Content-Type: application/sdp
Content-Length: {{.contentlength}}

{{.sdpbody}}
