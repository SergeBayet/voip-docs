# HAProxy

The distro used at time of writing: **Ubuntu 26.04 LTS**

## Setup

```bash
# Create a directory for the key if it doesn't exist
sudo install -d -m 0755 /usr/share/keyrings
# Download the GPG key
sudo wget -qO /usr/share/keyrings/HAPROXY-key-community.asc https://pks.haproxy.com/linux/community/RPM-GPG-KEY-HAProxy

# Add the HAProxy repository for resolute and HAProxy 3.4
echo "deb [signed-by=/usr/share/keyrings/HAPROXY-key-community.asc] https://www.haproxy.com/download/haproxy/performance/ubuntu/ha34 resolute main" | sudo tee /etc/apt/sources.list.d/haproxy.list

sudo apt-get update
sudo apt-get install haproxy-awslc
```

## Configuration

### X.509 Certificates

HAProxy wants key+cert concatenated in one PEM.

```bash
mkdir /etc/haproxy/certs
cat "/etc/ssl/_.voip.test.odoo.com.crt" "/etc/ssl/_.voip.test.odoo.com.key" > "/etc/haproxy/certs/_.voip.test.odoo.com.pem"
```

### Sip-Over-WSS [WIP]

`/etc/haproxy/conf.d/sip-over-wss.cfg`

```conf
frontend wss_in
    bind :443 ssl crt /etc/haproxy/certs/_.voip.test.odoo.com.pem
    default_backend kamailio_ws
    mode tcp
    log global
    option tcplog
    timeout connect 5s
    timeout client  1h
    timeout server  1h

backend kamailio_ws
    mode tcp
    balance roundrobin

    option httpchk
    http-check send meth GET uri /healthz ver HTTP/1.1 hdr Host healthcheck hdr Connection close
    http-check expect status 200

    # send-proxy-v2 prepends PROXY protocol so Kamailio learns the real client IP.
    # check-send-proxy: the health check must also prepend it, else the edge
    # (tcp_accept_haproxy=yes) refuses the header-less check connection.
    # init-addr last,libc,none: resolve via libc at startup so the servers get an
    # address and come UP at runtime; fall back to "none" so `haproxy -c` (lint,
    # run standalone with the edges down) still validates. NB the original bare
    # `init-addr none` passed lint but, with no resolvers section, never resolved
    # -> permanent <NOSRV>: that was the WS-edge "unexpected EOF" bug.
    server edge-a 127.0.0.1:8080 send-proxy-v2 check check-send-proxy init-addr last,libc,none
    # server edge-b edge-b:8080 send-proxy-v2 check check-send-proxy init-addr last,libc,none
```