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

## Configuration Files

!!! tip
    To copy all these configuration files, you can use:
    ```bash
    scp -r ./_etc_kamailio/* root@voip.test.odoo.com:/etc/kamailio/
    ```
    Or, to keep the folder in sync (transfers only what changed and removes files deleted locally), use `rsync` over SSH:
    ```bash
    rsync -avz --delete ./_etc_kamailio/ root@voip.test.odoo.com:/etc/kamailio/
    ```
    After copying the configuration files, the Kamailio service needs to be restarted for the changes to take effect. You can do this remotely over SSH:
    ```bash
    ssh root@voip.test.odoo.com systemctl restart kamailio
    ```
    To sync from local to the server and restart in a single command:
    ```bash
    rsync -avz --delete ./_etc_kamailio/ root@voip.test.odoo.com:/etc/kamailio/ && ssh root@voip.test.odoo.com systemctl restart kamailio
    ```

### `/etc/kamailio/kamctlrc`
```rc
{% include "./_etc_kamailio/kamctlrc" %}
```

### `/etc/kamailio/kamailio.cfg`
```c
{% include "./_etc_kamailio/kamailio.cfg" %}
```

### `/etc/kamailio/globals.cfg`
```c
{% include "./_etc_kamailio/globals.cfg" %}
```

### `/etc/kamailio/custom_params.cfg`
```c
{% include "./_etc_kamailio/custom_params.cfg" %}
```

### `/etc/kamailio/modules.cfg`
```c
{% include "./_etc_kamailio/modules.cfg" %}
```

### `/etc/kamailio/routes.cfg`
```c
{% include "./_etc_kamailio/routes.cfg" %}
```

### `/etc/kamailio/routes/request_main.cfg`
```c
{% include "./_etc_kamailio/routes/request_main.cfg" %}
```

### `/etc/kamailio/routes/relay.cfg`
```c
{% include "./_etc_kamailio/routes/relay.cfg" %}
```

### `/etc/kamailio/routes/reqinit.cfg`
```c
{% include "./_etc_kamailio/routes/reqinit.cfg" %}
```

### `/etc/kamailio/routes/withindialog.cfg`
```c
{% include "./_etc_kamailio/routes/withindialog.cfg" %}
```

### `/etc/kamailio/routes/registrar.cfg`
```c
{% include "./_etc_kamailio/routes/registrar.cfg" %}
```

### `/etc/kamailio/routes/location.cfg`
```c
{% include "./_etc_kamailio/routes/location.cfg" %}
```

### `/etc/kamailio/routes/presence.cfg`
```c
{% include "./_etc_kamailio/routes/presence.cfg" %}
```

### `/etc/kamailio/routes/auth.cfg`
```c
{% include "./_etc_kamailio/routes/auth.cfg" %}
```

### `/etc/kamailio/routes/natdetect.cfg`
```c
{% include "./_etc_kamailio/routes/natdetect.cfg" %}
```

### `/etc/kamailio/routes/natmanage.cfg`
```c
{% include "./_etc_kamailio/routes/natmanage.cfg" %}
```

### `/etc/kamailio/routes/dialoguri.cfg`
```c
{% include "./_etc_kamailio/routes/dialoguri.cfg" %}
```

### `/etc/kamailio/routes/sipout.cfg`
```c
{% include "./_etc_kamailio/routes/sipout.cfg" %}
```

### `/etc/kamailio/routes/pstn.cfg`
```c
{% include "./_etc_kamailio/routes/pstn.cfg" %}
```

### `/etc/kamailio/routes/jsonrpc.cfg`
```c
{% include "./_etc_kamailio/routes/jsonrpc.cfg" %}
```

### `/etc/kamailio/routes/voicemail.cfg`
```c
{% include "./_etc_kamailio/routes/voicemail.cfg" %}
```

### `/etc/kamailio/routes/manage_branch.cfg`
```c
{% include "./_etc_kamailio/routes/manage_branch.cfg" %}
```

### `/etc/kamailio/routes/manage_reply.cfg`
```c
{% include "./_etc_kamailio/routes/manage_reply.cfg" %}
```

### `/etc/kamailio/routes/manage_failure.cfg`
```c
{% include "./_etc_kamailio/routes/manage_failure.cfg" %}
```
