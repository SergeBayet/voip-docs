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
apt upgrade # while you're at it, also upgrade
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

## Certs

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
```
