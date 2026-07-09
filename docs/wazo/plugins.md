# Developing a Wazo plugin

This guide explains how to create, package, install, debug, and evolve a Wazo
plugin. It focuses on the type of plugin that installs:

- Asterisk dialplan fragments;
- a page in the legacy Wazo administration UI;
- local configuration or state used by that page.

The examples are based on Wazo 26.05 on Debian 12. Wazo internals can change
between releases, so always inspect the plugins installed on the target server
before copying an implementation detail.

The complete example behind this guide is the
`wazo-number-condition-plugin`. It adds a **Number Conditions** entry below
**Call Management** and is intended to route incoming calls according to the
calling number.

## Understand what a Wazo plugin is

A Wazo plugin is a source repository that `wazo-plugind` turns into a Debian
package. It is not necessarily a Python package, and it is not automatically a
Wazo UI extension.

A plugin may contain several independent layers:

| Layer | Responsibility | Typical destination |
| --- | --- | --- |
| Plugin metadata | Name, namespace, version, compatibility | `/usr/lib/wazo-plugind/plugins/` |
| Packaging script | Select files and run lifecycle operations | `wazo/rules` |
| Asterisk | Contexts, subroutines, routing | `/etc/asterisk/extensions_extra.d/` |
| Wazo UI | Menu, Flask routes, forms, templates | `/usr/lib/python3/dist-packages/` |
| Wazo UI configuration | Enable the Python entry point | `/etc/wazo-ui/conf.d/` |
| Backend | Persistence and business API | Local storage or a `wazo-confd` plugin |

These layers do not appear merely because the repository contains their source
files. The `package` action in `wazo/rules` must copy every runtime file into
the package staging directory.

!!! warning

    Installing an Asterisk configuration file does not install a Wazo UI
    plugin. If only the dialplan file appears on the server, inspect the
    `package` section of `wazo/rules` and the installed Debian package contents.

## Inspect the target Wazo installation first

Do not assume that every Wazo installation uses the same frontend. Current
installations may expose the Python/Flask Wazo UI, while other products or
future versions may use a different frontend.

On the target server:

```bash
dpkg -s wazo-ui
dpkg -L wazo-ui | head -100
find /usr/lib/python3/dist-packages/wazo_ui/plugins -maxdepth 2 -type f | head -100
```

The Python/Flask UI has plugins such as:

```text
/usr/lib/python3/dist-packages/wazo_ui/plugins/
├── incall/
├── ivr/
├── queue/
├── schedule/
├── user/
└── voicemail/
```

Each plugin generally contains:

```text
plugin.py
view.py
form.py
service.py
templates/
static/
```

Choose a native plugin with behavior close to the desired feature:

- `schedule` for list/create/edit/delete screens;
- `ivr` for a form with a dynamic list of destination rows;
- `queue` for destination registration and Select2 fields;
- `incall` for placement below **Call Management**.

Read the installed version rather than relying on an online example:

```bash
sed -n '1,240p' /usr/lib/python3/dist-packages/wazo_ui/plugins/schedule/view.py
sed -n '1,260p' /usr/lib/python3/dist-packages/wazo_ui/plugins/schedule/templates/schedule/list.html
sed -n '1,300p' /usr/lib/python3/dist-packages/wazo_ui/plugins/ivr/templates/ivr/add.html
sed -n '1,260p' /usr/lib/python3/dist-packages/wazo_ui/helpers/destination.py
```

Also identify the exact Python version and Wazo UI package version:

```bash
python3 --version
dpkg-query -W wazo-ui
```

## Repository layout

A plugin containing dialplan and Wazo UI code can use this layout:

```text
wazo-example-plugin/
├── README.md
├── asterisk/
│   └── extensions_extra.d/
│       └── example.conf
├── wazo/
│   ├── plugin.yml
│   └── rules
├── wazo-ui-example.yml
├── wazo_ui_example/
│   ├── __init__.py
│   ├── form.py
│   ├── plugin.py
│   ├── service.py
│   ├── view.py
│   └── templates/
│       └── example/
│           ├── edit.html
│           └── list.html
└── wazo-ui-example-0.1.0.dist-info/
    ├── METADATA
    ├── entry_points.txt
    └── top_level.txt
```

The manually maintained `.dist-info` directory is used here because
`wazo-plugind` executes `wazo/rules`; it does not automatically run
`pip install`. A project can instead generate Python package metadata during
the build, but the generated metadata must still end up below
`/usr/lib/python3/dist-packages` in the Debian package.

## Create the plugin manifest

Create `wazo/plugin.yml`:

```yaml
name: wazo-example-plugin
namespace: my-company
version: 0.1.0
author: My Company
display_name: Example
min_wazo_version: 26.00
plugin_format_version: 0
tags:
  - call-management
homepage: https://github.com/my-company/wazo-example-plugin

asterisk:
  config_files:
    extensions_extra.d/example.conf:
      source: asterisk/extensions_extra.d/example.conf
```

Important fields:

- `name` and `namespace` identify the installed plugin;
- `version` becomes the Debian package version;
- `min_wazo_version` prevents installation on an older unsupported Wazo;
- `plugin_format_version` selects the format understood by `wazo-plugind`;
- `asterisk.config_files` declares Asterisk configuration files.

### Version every installable change

Increase the version for every change that must reach a server:

```yaml
version: 0.1.1
```

`wazo-plugind` does not necessarily rebuild an installed package merely because
the Git commit changed. A log such as this means that no update occurred:

```text
my-company/wazo-example-plugin is already installed
```

Keep these versions synchronized:

- `wazo/plugin.yml`;
- `Version:` in Python `METADATA`;
- the source `.dist-info` directory name;
- the destination `.dist-info` directory in `wazo/rules`.

## Implement `wazo/rules`

`wazo/rules` is an executable shell script called with one lifecycle action.
A minimal complete implementation is:

```sh
#!/bin/sh

set -e

case "$1" in
    build)
        ;;
    package)
        mkdir -p "${pkgdir}/etc/asterisk/extensions_extra.d"
        cp asterisk/extensions_extra.d/example.conf \
            "${pkgdir}/etc/asterisk/extensions_extra.d/example.conf"

        mkdir -p "${pkgdir}/etc/wazo-ui/conf.d"
        cp wazo-ui-example.yml \
            "${pkgdir}/etc/wazo-ui/conf.d/example.yml"

        mkdir -p "${pkgdir}/usr/lib/python3/dist-packages"
        cp -R wazo_ui_example \
            "${pkgdir}/usr/lib/python3/dist-packages/wazo_ui_example"
        cp -R wazo-ui-example-0.1.0.dist-info \
            "${pkgdir}/usr/lib/python3/dist-packages/wazo_ui_example-0.1.0.dist-info"
        ;;
    install)
        asterisk -x 'dialplan reload'
        systemctl restart wazo-ui
        ;;
    uninstall)
        systemctl restart wazo-ui
        ;;
    *)
        echo "$0 called with unknown argument '$1'" >&2
        exit 1
        ;;
esac
```

Make it executable:

```bash
chmod 0755 wazo/rules
```

Lifecycle actions:

- `build`: compile or generate artifacts before packaging;
- `package`: copy files below `${pkgdir}`, which represents `/` in the future
  Debian package;
- `install`: run after package installation;
- `uninstall`: run during package removal.

Do not write directly to `/etc` or `/usr` in `package`; always write below
`${pkgdir}`.

!!! tip

    Treat `package` as the authoritative inventory of runtime files. A source
    file omitted here will not exist on the Wazo server.

### Test the package staging locally

```bash
pkgdir="$(mktemp -d)"
export pkgdir
sh wazo/rules package
find "$pkgdir" -type f -print | sort
```

Expected output includes the Asterisk file, UI configuration, Python package,
templates, and entry-point metadata.

## Add an Asterisk dialplan fragment

Place a dialplan file below `asterisk/extensions_extra.d/`:

```ini
[example-plugin]
exten = s,1,NoOp(Example plugin loaded)
 same = n,Return()
```

After installation:

```bash
asterisk -rx "dialplan reload"
asterisk -rx "dialplan show example-plugin"
```

Use a unique context prefix to avoid collisions with Wazo-generated contexts.
Never edit Wazo-generated dialplan files directly; upgrades or configuration
regeneration will overwrite them.

For a routing plugin, a stable entry point can be:

```ini
[wazo-number-condition]
exten = _X.,1,NoOp(Number condition router ${EXTEN})
 same = n,GotoIf($["${CALLERID(num)}" =~ "^\+32"]?belgium)
 same = n,Goto(default)
 same = n(belgium),Goto(queue,1,1)
 same = n(default),Hangup()
```

An incoming call can enter it through a native Wazo **Custom** destination:

```text
Goto(wazo-number-condition,<router-uuid>,1)
```

This avoids introducing an unsupported destination type into `wazo-confd`.
A truly native **Number Condition** destination requires a corresponding
`wazo-confd` extension because `confd` validates destination schemas.

## Register an external Wazo UI plugin

Wazo UI discovers plugins through Python entry points in the
`wazo_ui.plugins` group.

Create `wazo-ui-example-0.1.0.dist-info/entry_points.txt`:

```ini
[wazo_ui.plugins]
example = wazo_ui_example.plugin:Plugin
```

Create `wazo-ui-example-0.1.0.dist-info/METADATA`:

```text
Metadata-Version: 2.1
Name: wazo-ui-example
Version: 0.1.0
Summary: Example plugin for Wazo UI
```

Create `wazo-ui-example-0.1.0.dist-info/top_level.txt`:

```text
wazo_ui_example
```

Verify discovery on the server:

```bash
python3 - <<'PY'
from importlib.metadata import entry_points

for entry_point in entry_points(group="wazo_ui.plugins"):
    if entry_point.name == "example":
        print(entry_point)
PY
```

Expected:

```text
EntryPoint(name='example', value='wazo_ui_example.plugin:Plugin', group='wazo_ui.plugins')
```

## Enable the Wazo UI plugin

Wazo UI loads only enabled entry points. Create `wazo-ui-example.yml`:

```yaml
enabled_plugins:
  example: true
```

Package it as:

```text
/etc/wazo-ui/conf.d/example.yml
```

Then restart Wazo UI:

```bash
systemctl restart wazo-ui
systemctl --no-pager --full status wazo-ui
```

The plugin is loaded at process startup; a browser refresh alone is not enough
after installing new Python code.

## Create the Flask blueprint

Create `wazo_ui_example/plugin.py`:

```python
from wazo_ui.helpers.menu import register_flaskview
from wazo_ui.helpers.plugin import create_blueprint

from .service import ExampleService
from .view import ExampleView

example = create_blueprint("example", __name__)


class Plugin:
    def load(self, dependencies):
        core = dependencies["flask"]
        clients = dependencies["clients"]

        ExampleView.service = ExampleService(clients["wazo_confd"])
        ExampleView.register(example, route_base="/examples")
        register_flaskview(example, ExampleView)

        core.register_blueprint(example)
```

The important operations are:

1. create a blueprint with Wazo's helper;
2. inject services or API clients into the view;
3. register Flask-Classful routes;
4. register menu metadata;
5. register the blueprint on the Flask application.

The available dependency names should be confirmed in the installed
`wazo_ui/controller.py`.

## Add a menu entry

Create `wazo_ui_example/view.py`:

```python
from flask_babel import lazy_gettext as l_

from wazo_ui.helpers.menu import menu_item
from wazo_ui.helpers.view import BaseIPBXHelperView

from .form import ExampleForm


class ExampleView(BaseIPBXHelperView):
    form = ExampleForm
    resource = "example"

    @menu_item(
        ".ipbx.call_management.examples",
        l_("Examples"),
        order=2,
        icon="filter",
        multi_tenant=True,
    )
    def index(self):
        return super().index()
```

The path is a hierarchy:

```text
.ipbx.call_management.examples
```

Existing sections such as `.ipbx.call_management` do not need to be declared
again. Inspect a native view to get the exact path:

```bash
sed -n '1,80p' /usr/lib/python3/dist-packages/wazo_ui/plugins/incall/view.py
```

Useful parameters:

- `order`: position inside the section;
- `icon`: Font Awesome icon name used by this Wazo UI;
- `multi_tenant`: whether the menu is visible when working in a tenant.

## Build native CRUD screens

`BaseIPBXHelperView` provides the conventional routes:

| Method | Route | Purpose |
| --- | --- | --- |
| `index` | `/examples/` | List resources |
| `post` | `/examples/` | Create a resource |
| `get` | `/examples/<id>` | Edit a resource |
| `put` | `/examples/put/<id>` | Update a resource |
| `delete` | `/examples/delete/<id>` | Delete a resource |

The service must implement:

```python
class ExampleService:
    def list(self, **kwargs):
        return {"items": [], "total": 0}

    def get(self, resource_id):
        ...

    def create(self, resource):
        ...

    def update(self, resource):
        ...

    def delete(self, resource_id):
        ...
```

Each resource should contain an `id` or `uuid`. Wazo's table macros put this
identifier in the row and use it to build edit/delete URLs.

### List template

Create `templates/example/list.html`:

```jinja
{% extends "layout.html" %}

{% block content_header %}
  {{ build_breadcrumbs([
    { 'name': _('Examples'), 'link': url_for('.ExampleView:index'), 'icon': 'filter' }
  ]) }}
{% endblock %}

{% block content %}
  <section class="content">
    {% call build_list_containers(_('Examples'), 'filter') %}
      {% call build_list_table() %}
        {% call build_list_table_headers(get=url_for('.ExampleView:get', id=''), delete=url_for('.ExampleView:delete', id='')) %}
          <th>{{ _('Name') }}</th>
          <th>{{ _('Enabled') }}</th>
        {% endcall %}
        {% call(item) build_list_table_rows(resource_list['items']) %}
          <td>{{ item.name }}</td>
          <td>{{ _('Yes') if item.enabled else _('No') }}</td>
        {% endcall %}
      {% endcall %}
    {% endcall %}

    {% call build_hidden_add_containers(_('Add Example')) %}
      {% call build_form() %}
        {% call add_default_fields(form=form, submit_value=_('Add')) %}
          {{ render_field(form.name) }}
          {{ render_field(form.enabled) }}
        {% endcall %}
      {% endcall %}
    {% endcall %}
  </section>
{% endblock %}
```

`build_hidden_add_containers` creates the modal opened by the small `+` button.

### Edit template

Create `templates/example/edit.html`:

```jinja
{% extends "layout.html" %}

{% block content_header %}
  {{ build_breadcrumbs(current_breadcrumbs + [
    { 'name': resource.name, 'link': url_for('.ExampleView:get', id=resource.id), 'icon': 'filter' }
  ]) }}
{% endblock %}

{% block content %}
  {% call build_section_row() %}
    {% call build_form(action=url_for('.ExampleView:put', id=resource.id)) %}
      {% call build_form_box(_('Example'), resource.name, 'filter', container_class='col-md-6') %}
        {% call add_default_fields(form=form, submit_value=_('Update')) %}
          {{ render_field(form.name) }}
          {{ render_field(form.enabled) }}
        {% endcall %}
      {% endcall %}
    {% endcall %}
  {% endcall %}
{% endblock %}
```

## Add dynamic rule rows like IVR or Schedule

Use a nested form and a `FieldList`:

```python
import re

from flask_babel import lazy_gettext as l_
from wtforms.fields import BooleanField, FieldList, FormField, StringField, SubmitField
from wtforms.validators import InputRequired, Length, ValidationError

from wazo_ui.helpers.destination import DestinationField
from wazo_ui.helpers.form import BaseForm


def validate_regex(_form, field):
    try:
        re.compile(field.data)
    except re.error as error:
        raise ValidationError(
            l_("Invalid regular expression: %(error)s", error=error)
        ) from error


class RoutingRuleForm(BaseForm):
    regex = StringField(
        l_("Caller number regular expression"),
        validators=[InputRequired(), Length(max=255), validate_regex],
    )
    destination = DestinationField(destination_label=l_("Destination"))


class RouterForm(BaseForm):
    name = StringField(l_("Name"), validators=[InputRequired(), Length(max=128)])
    enabled = BooleanField(l_("Enabled"), default=True)
    rules = FieldList(FormField(RoutingRuleForm), min_entries=1)
    fallback_destination = DestinationField(
        destination_label=l_("Default destination")
    )
    submit = SubmitField(l_("Save"))
```

Render the rows in a right-hand panel, following the IVR layout:

```jinja
{% call build_form(action=url_for('.RouterView:put', id=resource.id)) %}
  {% call build_form_box(_('Router'), resource.name, 'filter', container_class='col-md-6') %}
    {% call add_default_fields(form=form, submit_value=_('Update')) %}
      {{ render_field(form.name) }}
      {{ render_field(form.enabled) }}
      {{ render_field(form.fallback_destination, with_label=False) }}
    {% endcall %}
  {% endcall %}

  {% call build_form_box(_('Routing Rules'), box_class='box-info', container_class='col-md-6') %}
    {{ build_add_row_entry_header() }}
    {% call build_table() %}
      {% call build_table_headers() %}
        <th>{{ _('Regular expression') }}</th>
        <th>{{ _('Destination') }}</th>
        <th></th>
      {% endcall %}
      {% call build_table_body(class_='dynamic-table') %}
        {% do form.rules.append_entry() %}
        {{ build_rule(form.rules.pop_entry(), template=True) }}
        {% for rule in form.rules %}
          {{ build_rule(rule) }}
        {% endfor %}
      {% endcall %}
    {% endcall %}
    {{ build_add_row_entry_header() }}
  {% endcall %}
{% endcall %}

{% macro build_rule(rule, template=False) %}
  {% if template %}
    {% set tr_class = 'row-template hidden' %}
  {% endif %}
  <tr class="{{ tr_class }}">
    <td>{{ render_field(rule.regex, with_label=False) }}</td>
    <td>{{ render_field(rule.destination, with_label=False) }}</td>
    <td class="text-center">{{ add_delete_entry_button() }}</td>
  </tr>
{% endmacro %}
```

The hidden template row is cloned by Wazo's JavaScript when the user presses
`+`. The order of submitted `FieldList` entries is the visual order and should
be preserved by the service when the first matching rule wins.

## Use Wazo destination fields correctly

`DestinationField` exposes the destination types registered by native plugins:

- application;
- conference;
- custom;
- extension;
- group;
- hangup;
- IVR;
- queue;
- sound;
- switchboard;
- user;
- voicemail.

The serialized value is a dictionary:

```json
{
  "type": "queue",
  "queue_id": "1",
  "ring_time": null,
  "queue_label": "Sales"
}
```

Do not reduce this object to the visible label. The stable identifier is needed
for routing, while the label is needed to restore the Select2 widget.

### Dynamic Select2 validation trap

Destination selects are populated through AJAX. Their server-side WTForms
`choices` list is empty. Calling `form.validate_on_submit()` recursively on the
whole `DestinationField` can therefore produce:

```text
User - Not a valid choice.
```

It may also validate every inactive destination subform and produce dozens of
errors:

```text
Destination - conference
Destination - extension
Destination - queue
Destination - csrf_token
...
```

Native Wazo views often validate only the top-level CSRF token and let
`wazo-confd` validate the destination payload. If the plugin uses a local
backend:

- validate the top-level CSRF token;
- validate local scalar fields such as name and regex;
- require a destination `type`;
- do not compare AJAX-loaded identifiers to an empty WTForms choices list;
- validate identifiers again before using them to generate dialplan.

Never disable CSRF on the HTTP form.

### Restore destination labels

When a native resource is read from `wazo-confd`, its response contains helper
labels such as:

- `queue_label`;
- `user_firstname` and `user_lastname`;
- `ivr_name`;
- `voicemail_name`;
- `group_name`;
- `conference_name`;
- `switchboard_name`.

A local service does not get these fields automatically. If it stores only:

```json
{"type": "queue", "queue_id": "1", "queue_label": null}
```

the identifier remains saved, but the queue appears empty after reloading the
form. Resolve the label from `wazo-confd` before returning the form data.

Conceptually:

```python
queue_id = destination["queue_id"]
queues = confd_client.queues.list(limit=None)["items"]
queue = next(queue for queue in queues if str(queue["id"]) == str(queue_id))
destination["queue_label"] = queue["name"]
```

Apply the same principle to every destination type supported by the plugin.
Persist the enriched values so an existing record with a missing label is
repaired once rather than on every request.

The identifier remains authoritative. A label is presentation data and may
change.

## Choose a persistence strategy

There are two reasonable levels.

### Local file persistence

Suitable for a prototype or a feature local to one Wazo engine:

```text
/var/lib/wazo-ui/example/resources.json
```

Requirements:

- use a fixed path, never a user-controlled filesystem path;
- create the directory with restrictive permissions;
- write to a temporary file in the same directory;
- flush and atomically replace the destination;
- serialize only JSON-compatible values;
- use stable UUIDs;
- account for concurrent requests;
- implement schema migration when the model changes.

Atomic replacement prevents a crash from leaving a partially written JSON
document.

Limitations:

- no multi-node synchronization;
- no tenant-aware API semantics unless implemented explicitly;
- no standard Wazo backup/API integration;
- API clients outside Wazo UI cannot manage the resources.

### `wazo-confd` plugin

Use a real `wazo-confd` resource when the feature must be:

- exposed through the Wazo API;
- tenant-aware;
- validated centrally;
- consumed by multiple services;
- persisted in PostgreSQL;
- integrated as a native destination type.

This is more work: schema, REST resource, DAO/model, permissions, client
support, and migrations are required. Do not create a `confd` plugin merely to
display the first UI prototype, but plan for it before the local JSON format
becomes a long-term public interface.

## Generate dialplan safely

Do not place raw user-provided strings directly into Asterisk configuration.
For a number-condition router:

1. validate regex length and syntax;
2. keep destination types on an explicit allowlist;
3. resolve destination identifiers against `wazo-confd`;
4. map each allowed type to a literal dialplan template;
5. reject control characters, commas, parentheses, and newlines where they are
   not explicitly supported;
6. generate into a temporary file;
7. run an Asterisk syntax or dialplan check where possible;
8. atomically replace the active file;
9. reload the dialplan only after successful generation.

Example architecture:

```text
Incall
  └── Custom destination: Goto(wazo-number-condition,<router UUID>,1)
        ├── ^\+32 → queue Belgium
        ├── ^\+33 → queue France
        ├── ^\+34 → queue Spain
        └── default → international queue
```

The first matching rule wins. Always provide a default destination, otherwise
unmatched calls have undefined behavior.

Keep generated dialplan separate from the static bootstrap file:

```text
/etc/asterisk/extensions_extra.d/number-condition.conf
/var/lib/wazo-ui/number-condition/generated.conf
```

The static file can include or call the generated implementation. This keeps
package ownership and mutable runtime data conceptually separate.

## Install the plugin

### Through Wazo UI

Install from the Git repository and select the correct branch or tag. If the
plugin is already installed, use a newer version or explicitly reinstall it.

Watch the task:

```bash
journalctl -u wazo-plugind -f
```

### Through the CLI

Check the available commands on the installed version:

```bash
wazo-plugind-cli -c help
wazo-plugind-cli -c "help install"
wazo-plugind-cli -c list
```

A typical command syntax is:

```bash
wazo-plugind-cli -c "install git https://github.com/my-company/wazo-example-plugin --ref master"
```

CLI options vary by release. Use the local `help install` output rather than
assuming a `--reinstall` option exists.

## Verify what was actually installed

Find the generated Debian package:

```bash
dpkg -l | grep wazo-plugind
dpkg -L wazo-plugind-wazo-example-plugin-my-company
dpkg-query -W -f='${Version}\n' wazo-plugind-wazo-example-plugin-my-company
```

Verify each layer independently:

```bash
test -f /etc/asterisk/extensions_extra.d/example.conf
test -f /etc/wazo-ui/conf.d/example.yml
test -d /usr/lib/python3/dist-packages/wazo_ui_example
test -f /usr/lib/python3/dist-packages/wazo_ui_example-0.1.0.dist-info/entry_points.txt
```

Verify entry-point discovery:

```bash
python3 - <<'PY'
from importlib.metadata import entry_points

print(
    [
        entry_point
        for entry_point in entry_points(group="wazo_ui.plugins")
        if entry_point.name == "example"
    ]
)
PY
```

Verify services:

```bash
systemctl restart wazo-ui
systemctl --no-pager --full status wazo-ui
asterisk -rx "dialplan reload"
asterisk -rx "dialplan show example-plugin"
```

Finally force-refresh the browser with `Ctrl+F5`.

## Debug failures systematically

### Plugin installation

```bash
journalctl -u wazo-plugind --since "30 minutes ago" --no-pager
```

Common messages:

`git clone ... returned 128`
: The server could not clone the repository, branch, or tag. Check network,
  repository visibility, and the requested ref.

`is already installed`
: No package update occurred. Increase the plugin version or force a real
  reinstall.

`Unexpected error while building`
: Run `wazo/rules package` locally with a temporary `${pkgdir}`, then inspect
  shell errors and missing source paths.

### Wazo UI startup

```bash
journalctl -u wazo-ui --since "30 minutes ago" --no-pager
systemctl --no-pager --full status wazo-ui
```

Typical causes:

- entry point missing or misspelled;
- plugin absent from `enabled_plugins`;
- import error in `plugin.py`, `view.py`, or `form.py`;
- template not copied;
- wrong `.dist-info` version/path;
- Wazo UI was not restarted.

### HTTP requests

Wazo UI logs each request:

```text
GET https://wazo.example/number_conditions/ 200
POST https://wazo.example/number_conditions/ 200
```

Interpretation:

- `POST 200`: the form was usually rejected and rendered again;
- `POST 302`: creation/update usually succeeded and redirected;
- `500`: inspect the traceback in `journalctl -u wazo-ui`;
- `404`: verify route registration and `route_base`.

### Menu missing

Check, in order:

1. installed Python files;
2. installed `.dist-info/entry_points.txt`;
3. `importlib.metadata.entry_points`;
4. `/etc/wazo-ui/conf.d/*.yml`;
5. Wazo UI restart;
6. `journalctl -u wazo-ui`;
7. browser hard refresh.

### Dialplan missing

```bash
dpkg -L <plugin-package> | grep asterisk
asterisk -rx "dialplan reload"
asterisk -rx "dialplan show <context>"
journalctl -u asterisk --since "10 minutes ago" --no-pager
```

## Validate before publishing

Run at least:

```bash
ruff check wazo_ui_example
python3 -m compileall -q wazo_ui_example
git diff --check
```

Parse Jinja syntax:

```bash
python3 - <<'PY'
from pathlib import Path

from jinja2 import Environment

environment = Environment(extensions=["jinja2.ext.do"])
for path in Path("wazo_ui_example/templates").rglob("*.html"):
    environment.parse(path.read_text(encoding="utf-8"))
    print(f"valid: {path}")
PY
```

Test package contents:

```bash
pkgdir="$(mktemp -d)"
export pkgdir
sh wazo/rules package
find "$pkgdir" -type f -print | sort
```

For a CRUD service, test:

- create;
- list;
- get;
- update;
- delete;
- ordering;
- migration from the previous schema;
- atomic persistence;
- missing/renamed Wazo destinations.

## Security checklist

- Keep CSRF enabled on non-JSON routes.
- Require authentication by inheriting from Wazo's login-required views.
- Never use `eval`.
- Never interpolate untrusted values into shell commands.
- Do not accept arbitrary filesystem paths.
- Do not generate arbitrary Asterisk applications from destination data.
- Resolve destination IDs through `wazo-confd`.
- Allowlist destination types and dialplan templates.
- Limit regex length and reject multiline/control characters.
- Treat catastrophic-backtracking regexes as a denial-of-service risk.
- Use tenant information when resources can belong to different tenants.
- Do not expose secrets, tokens, or full API objects in stored JSON or logs.
- Do not log raw form payloads in production.
- Use restrictive ownership and permissions for mutable state.

## Release checklist

Before each release:

1. update the plugin version everywhere;
2. run Ruff and Python compilation;
3. parse all Jinja templates;
4. test CRUD and schema migration;
5. stage the package and inspect every file;
6. commit and push the expected branch/tag;
7. install the new version;
8. confirm the installed Debian version;
9. inspect `wazo-plugind` and `wazo-ui` logs;
10. confirm entry-point discovery;
11. test create/edit/delete from the browser;
12. verify restored Select2 labels;
13. reload and inspect Asterisk dialplan;
14. place a real inbound test call, including the default branch;
15. verify uninstall/reinstall behavior.

## Quick reference

```bash
# Plugin source/build
sh wazo/rules package
ruff check wazo_ui_example
python3 -m compileall -q wazo_ui_example

# Installed package
dpkg -L wazo-plugind-wazo-example-plugin-my-company
dpkg-query -W -f='${Version}\n' wazo-plugind-wazo-example-plugin-my-company

# Plugin manager
wazo-plugind-cli -c list
journalctl -u wazo-plugind -f

# Wazo UI
systemctl restart wazo-ui
systemctl status wazo-ui
journalctl -u wazo-ui -f

# Asterisk
asterisk -rx "dialplan reload"
asterisk -rx "dialplan show example-plugin"
```

The key mental model is:

```text
Git repository
  → wazo-plugind
  → wazo/rules package
  → Debian package
  → files under /etc and /usr
  → service restart
  → Python entry-point discovery
  → Flask blueprint and menu
  → service/persistence
  → generated Asterisk routing
```

When a feature is missing, identify which arrow in this chain failed instead
of debugging the browser, Python, and Asterisk simultaneously.
