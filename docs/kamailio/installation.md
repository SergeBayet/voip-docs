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
apt install kamailio kamailio-websocket-modules
```

There are many Kamailio packages specific for various modules. You can see all available with:
```bash
apt search kamailio
```
