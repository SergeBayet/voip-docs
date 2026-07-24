# Odoo VoIP Module Configuration

## Development tips
We strongly recommend you use your own data module with:

`data/voip.xml`
```xml
<?xml version="1.0" encoding="utf-8"?>
<odoo>
    <!-- Allows to purchase dummy credits -->
    <record id="iap_endpoint" model="ir.config_parameter">
        <field name="key">iap.endpoint</field>
        <field name="value">https://iap-test.odoo.com/</field>
    </record>

    <!-- Allows to contact your own Phone Service instance -->
    <record id="phone_service_endpoint" model="ir.config_parameter">
        <field name="key">phone_service.endpoint</field>
        <field name="value">https://your-tunneling-address.ngrok.free</field>
    </record>

    <!-- Allows to redirect your softphone to your own Kamailio Edge node -->
    <record id="voip.odoo_provider" model="voip.provider">
        <field name="ws_server">wss://edge-XXX.voip.test.odoo.com</field>
        <field name="pbx_ip">edge-XXX.voip.test.odoo.com</field>
    </record>
</odoo>
```