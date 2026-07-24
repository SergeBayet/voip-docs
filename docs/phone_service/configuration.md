# Configure Odoo IAP Phone Service

After having installed the Phone Service, you must go to `Settings > Phone Service`
and configure the following:
- Telnyx API Keys
- IAP Service Key
- Edge Token: must be the same as the edge token defined in the edge environment
- Edge Permit CIDRs: all public IP of the known edges, CIDR formatted, comma-separated.

## Development tips

We strongly recommend you create your own data module with:

`data/voip.xml`
```xml
<?xml version="1.0" encoding="utf-8"?>
<odoo>
    <!-- Allows to purchase dummy credits -->
    <record id="config_iap_endpoint" model="ir.config_parameter">
        <field name="key">iap.endpoint</field>
        <field name="value">https://iap-test.odoo.com/</field>
    </record>
    <record id="config_service_key" model="ir.config_parameter">
        <field name="key">phone_service.service_key</field>
        <field name="value">ask-for-the-proper-iap-service-key</field>
    </record>

    <!-- Mandatory in order to receive webhooks -->
    <function model="ir.config_parameter" name="set_param">
        <value>web.base.url</value>
        <value>https://your-tunneling-address.ngrok.free</value>
    </function>
    <function model="ir.config_parameter" name="set_param">
        <value>web.base.url.freeze</value>
        <value>True</value>
    </function>

    <!-- must be the same as the edge token defined in the edge environment -->
    <record id="ir_config_parameter_phone_service_edge_token" model="ir.config_parameter">
        <field name="key">phone_service.edge_token</field>
        <field name="value">the-magnificent-edge-token</field>
    </record>

    <!-- Your Telnyx API Keys -->
    <record id="config_telnyx_public_api_key" model="ir.config_parameter">
        <field name="key">phone_service.telnyx_public_api_key</field>
        <field name="value">find-it-in-telnyx-portal</field>
    </record>
    <record id="config_telnyx_private_api_key" model="ir.config_parameter">
        <field name="key">phone_service.telnyx_private_api_key</field>
        <field name="value">create-it-in-telnyx-portal</field>
    </record>

    <!-- PBX -->
    <record id="pbx_all_countries" model="phone_service.pbx">
        <field name="name">Development Wazo</field>
        <field name="url">https://wazo-2.voip.test.odoo.com</field>
        <field name="telnyx_connection_id">use-your-own-telnyx-sip-fqdn-connection</field>
        <field name="edge_proxy_fqdn">edge-XXX.voip.test.odoo.com</field>
        <field name="public_ip">34.79.218.67</field> <!-- Public IP of wazo-2.voip.test.odoo.com -->
        <field name="private_ip">10.132.15.236</field> <!-- Private IP of wazo-2.voip.test.odoo.com (find it with `ip addr` CLI command) -->
        <field name="master_username">master-wazo-user</field>
        <field name="master_password">master-wazo-password</field>
    </record>

    <!-- Extra security -->
    <record id="base.user_admin" model="res.users">
        <field name="password">A Better Password</field>
    </record>
</odoo>
```
