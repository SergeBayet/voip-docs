# Wazo

## Setup To Get Started

The distro used at time of writing: **Debian 12**

### Wazo Installation Procedure

Original source: [Wazo Platform Installation Guide](https://wazo-platform.org/uc-doc/installation/)

To install the Unified Communication use case in an all-in-one setup, do the following steps:

- Install a Debian 12 Bookworm system with a default locale with an UTF-8 charset.
- Run the following commands as root on the Debian system to provision sudo, git and Ansible:

```bash
apt update
apt install -yq sudo git ansible curl
```

> Note: Ansible is a suite of software tools that enables infrastructure as code. It is open-source and the suite includes software provisioning, configuration management, and application deployment functionality. https://en.wikipedia.org/wiki/Ansible_(software)

- Extract the Wazo Platform installer

```bash
git clone https://github.com/wazo-platform/wazo-ansible.git
cd wazo-ansible
```

- By default, Wazo Platform will install the development version. To install the latest stable version

```bash
ansible_tag=wazo-$(curl https://mirror.wazo.community/version/stable)
git checkout $ansible_tag
```

- Install the Wazo Platform installer dependency

```bash
ansible-galaxy install -r requirements-postgresql.yml
```

- Edit the file `inventories/uc-engine` to add your preferences and passwords. The various variables that can be customized are described [here](https://github.com/wazo-platform/wazo-ansible/blob/master/README.md#variables). By default, Wazo Platform will install the development version. To install the latest stable version, activate the following settings in `inventories/uc-engine`:

```conf
[uc_engine:vars]
wazo_distribution = pelican-bookworm
wazo_distribution_upgrade = pelican-bookworm
```

> See the available Wazo distributions [here](https://github.com/wazo-platform/debian-repo-main/blob/master/distributions).

- To install the web user interface, activate the following in your `inventories/uc-engine`:

```conf
[uc_ui:children]
uc_engine_host
```

- The following variables allow you to create the `root` account at installation time, to be able to use the web user interface and an API user to be able to use the REST APIs:

```conf
[uc_engine:vars]
engine_api_configure_wizard = true
engine_api_root_password = <YOUR_ROOT_PASSWORD>
api_client_name = <YOUR_API_USERNAME>
api_client_password = <YOUR_API_PASSWORD>
```

- Launch the installation by running the following command:

```bash
ansible-playbook -i inventories/uc-engine uc-engine.yml
```

- Once the installation completed, execute the following command to verify that all the Wazo services (wazo-plugind, wazo-webhookd, ...) are up and running:

```bash
wazo-service status
```

### Post Installation Steps

#### Configuration Files

- Create `/etc/asterisk/extensions_extra.d/odoo-subroutine-queue-no-continue.conf` file with the following content:

```conf
; Hook called by wazo before Queue()
; -> add "c" option in Queue()
; -> inject a subroutine on each channel called before Dial()
[odoo-subroutine-queue-no-continue]
exten = s,1,NoOp(=== ODOO SUBROUTINE - Queue No Continue ===)
 ; Reset flag at the beginning of the call
 ; MASTER_CHANNEL store the information on the master channel
 same = n,Set(MASTER_CHANNEL(__ODOO_CALL_REJECTED)=0)

 ; Debug to see the current options
 same = n,NoOp(Current WAZO_QUEUEOPTIONS=${WAZO_QUEUEOPTIONS})
 same = n,NoOp(Current WAZO_DIAL_OPTIONS=${WAZO_DIAL_OPTIONS})

 ; Add c option
 ; Not sure it's really necessary but...
 same = n,Set(_WAZO_QUEUEOPTIONS=${WAZO_QUEUEOPTIONS}c)

 ; Add a subroutine Dial b()
 ; b() is executed before the DIAL()
 ; used to attach a hangup handler to the callee
 same = n,Set(_WAZO_DIAL_OPTIONS=${WAZO_DIAL_OPTIONS}b(odoo-callee-before-dial^s^1))

 same = n,NoOp(New WAZO_QUEUEOPTIONS=${WAZO_QUEUEOPTIONS})
 same = n,NoOp(New WAZO_DIAL_OPTIONS=${WAZO_DIAL_OPTIONS})
 same = n,Return()

; Subroutine executed on the callee channel before the real call
; Install a handler that will be called when it finished
[odoo-callee-before-dial]
exten = s,1,NoOp(=== ODOO CALLEE BEFORE DIAL ===)
 same = n,NoOp(Channel=${CHANNEL})
 same = n,NoOp(Linkedid=${CHANNEL(linkedid)})

 ; The handler will be executed when the callee hang up / decline / fail
 same = n,Set(CHANNEL(hangup_handler_push)=odoo-callee-hangup-handler,s,1)
 same = n,Return()

; Handler called at the end of the callee canal
; Our case: a decline = SIP 603 rejected with a HANGUPCAUSE=21
[odoo-callee-hangup-handler]
exten = s,1,NoOp(=== ODOO CALLEE HANGUP HANDLER ===)
 same = n,NoOp(Channel=${CHANNEL})
 same = n,NoOp(Linkedid=${CHANNEL(linkedid)})
 same = n,NoOp(HANGUPCAUSE=${HANGUPCAUSE})

 ; 21 = call rejected
 same = n,GotoIf($["${HANGUPCAUSE}" = "21"]?rejected)
 same = n,Return()

 same = n(rejected),NoOp(=== ODOO EXPLICIT REJECT DETECTED ===)

 ; we bubble the information before the forwarding of the queue
 ; to be visible later in the Wazo forward hook
 same = n,Set(MASTER_CHANNEL(__ODOO_CALL_REJECTED)=1)
 same = n,Return()

; Hook Wazo called before the forwarding of a queue
; Wazo calls this context automatically if it exists
[xivo-subrfwd-queue]
exten = s,1,NoOp(=== ODOO FWD SUBROUTINE QUEUE ===)
 same = n,NoOp(ODOO_CALL_REJECTED=${ODOO_CALL_REJECTED})

 ; if the softphone rejects the call, we block the forwarding to the cellphone (for instance)
 same = n,GotoIf($["${ODOO_CALL_REJECTED}" = "1"]?stop)
 same = n,Return()

 same = n(stop),NoOp(=== STOP FORWARD: ODOO CALL WAS REJECTED ===)

 ; End the call with the same logical cause : rejected
 same = n,Hangup(21)
```

- (optional) To enable monit web ui endpoint, create `/etc/nginx/locations/https-available/monit` file with the following content:

```conf
location /monit/ {
    if ($arg_token = "<SECURE_UNIQUE_TOKEN>") {
        add_header Set-Cookie "monit_access=<SECURE_UNIQUE_TOKEN>; Path=/monit; HttpOnly; Secure";
        return 302 $scheme://$host$uri;
    }

    if ($cookie_monit_access != "<SECURE_UNIQUE_TOKEN>") {
        return 403;
    }

    proxy_pass http://localhost:2812/;
    proxy_set_header Host $host;
    proxy_set_header X-Real-IP $remote_addr;
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    proxy_set_header X-Forwarded-Proto $scheme;

    # Monit needs this for redirects to work correctly
    proxy_redirect http://localhost:2812/ /monit/;
}
```

Then enable it with:
```bash
ln -s /etc/nginx/locations/https-available/monit /etc/nginx/locations/https-enabled/monit
nginx -t && nginx -s reload
```
- (optional) To enable nginx to proxy to the wazo sip websocket, create `/etc/nginx/locations/https-available/ws` file with the following content:

```conf
location /ws {
    proxy_pass http://127.0.0.1:5039/ws;
    proxy_http_version 1.1;

    proxy_set_header Upgrade $http_upgrade;
    proxy_set_header Connection "Upgrade";
    proxy_set_header Host $host;
    proxy_set_header X-Real-IP $remote_addr;

    proxy_read_timeout 3600;
}
```

Then enable it with:
```bash
ln -s /etc/nginx/locations/https-available/ws /etc/nginx/locations/https-enabled/ws
nginx -t && nginx -s reload
```

#### HTTPS Certificates
Wazo uses HTTPS mainly for receiving and responding to REST API calls. The REST API calls can occur inside the Wazo Engine, i.e. between Wazo daemons, or outside the Wazo Engine, e.g. for the web interface or any other application based on the REST APIs.

From the outside of the Wazo Engine, every API call is reverse-proxied by nginx, which listens on port 443 (HTTPS) and distribute REST API calls to the right daemon. This means we only have to change one certificate (the one used by nginx) to enable all APIs to be secured by this certificate from the outside of the Wazo Engine.

The default HTTPS certificate used by the Wazo Engine is located in /usr/share/wazo-certs/server.crt with its associated server.key private key.

##### Use your own certificate

Edit the file `/etc/nginx/sites-available/wazo` and replace the following keys:

```conf
ssl_certificate /usr/share/wazo-certs/server.crt;
ssl_certificate_key /usr/share/wazo-certs/server.key;
```

```conf
ssl_certificate /etc/ssl/_.voip.test.odoo.com.crt;
ssl_certificate_key /etc/ssl/_.voip.test.odoo.com.key;
```

Then restart nginx:

```bash
systemctl restart nginx
```