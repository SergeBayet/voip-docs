# Troubleshooting Tools

## Logs

### Kamailio

First, make sure the debug logging features are enabled:
```cfg
debug=3
log_stderror=yes
```

!!! info "Docs: [debug](https://www.kamailio.org/wikidocs/cookbooks/6.1.x/core/#debug), [log_stderror](https://www.kamailio.org/wikidocs/cookbooks/6.1.x/core/#log_stderror)"

!!! note "Then, run Kamailio with either:"
    If running as a service:
    ```bash
    journalctl -fu kamailio
    ```
    Or you could also start directly with:
    ```bash
    kamailio -DD -E
    ```

Then you can log with:
!!! example "`xlog("L_INFO", "REQ $rm from $si:$sp\n");`"

!!! info "Docs: [xlog function](https://kamailio.org/docs/modules/6.1.x/modules/xlog.html#xlog.f.xlog)"

## Network Packets Analysis

### tcpdump

Capture incoming network packets with:
```bash
tcpdump -ni any -A port 5060 -w sip.pcap
```

Then you can analyze the pcap file with i.e. Wireshark.

### Wireshark

[Download here](https://www.wireshark.org/download.html).

!!! tip "Useful filters"
    ```
    sip
    sip.Call-ID == "xxxx"
    ```

### sngrep

It is an interactive and live SIP capture Rolls Royce.

!!! info "[Github](https://github.com/irontec/sngrep)"

!!! example "Start listening with `sngrep`"

!!! example "Start listening on specific port with `sngrep -p 5060`"

!!! example "Read a pcap file with `sngrep -I file.pcap`"

!!! example "Write a pcap file with `sngrep -o trace.pcap`"

### Homer / SIPCAPTURE

This is the *de facto* standard nowadays for SIP observability.

!!! info "[Github](https://github.com/SIPp/sipp), [Main Website](https://sipcapture.org/), [Homer 11 Docs](https://sipcapture.github.io/homer/)"

Architecture:
```
SIP endpoint
      |
      v
   Kamailio
      |
      +---- HEP ----> Homer
```

Kamailio send a copy of all SIP messages to HOMER.

We can then search a Call-ID, see complete dialogs, transactions, debug past issues...

Kamailio Modules:
```cfg
loadmodule "sipcapture.so"
loadmodule "hep.so"
```

!!! example "Configure and use"
    ```cfg
    hep_id = 1
    modparam("hep", "hep_id", "[hep_destination]10.0.0.20:9060;transport=udp")
    ```

    ```cfg
    sip_capture(); // add in the routes you want to capture
    ```

!!! info "Examples: [Kamailio](https://github.com/sipcapture/homer/wiki/Examples%3A-Kamailio), [Asterisk](https://github.com/sipcapture/homer/wiki/Examples%3A-Asterisk)", [sngrep](https://github.com/sipcapture/homer/wiki/Examples%3A-sngrep)

## SIP Testing Tools

### SIPp

It is probably the most used tool with Kamailio.

!!! info "[Github](https://github.com/SIPp/sipp), [Documentation](https://sipp.readthedocs.io/)"

It can send REGISTER, INVITE, simulate UAC and UAS, generate load, play XML scenarios...

!!! example "Send a call with `sipp voip.test.odoo.com -sn uac`"

!!! example "Register with `sipp voip.test.odoo.com -sn register`"

!!! example "Generate 100 calls per second with `sipp voip.test.odoo.com -sn uac -r 100 -rp 1000`"

### SIPexer

Easier and more lightweight alternative than SIPp.

Useful to i.e.:
- check an endpoint replies
- quickly test a REGISTER
- or any other simple dialog
- unit testing

!!! info "[Github](https://github.com/miconda/sipexer)"

!!! example "Register"
    ```bash
    sipexer \
      -method REGISTER \
      -user alice \
      -password secret \
      -proxy voip.test.odoo.com
    ```

!!! example "Options"
    ```bash
    sipexer \
      -method OPTIONS \
      -proxy voip.test.odoo.com
    ```
