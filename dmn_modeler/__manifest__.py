{
    "name": "DMN Modeler",
    "summary": "Module to model DMN decision tables using dmn-js and Odoo's OWL framework.",
    "version": "16.0.1.0.0",
    "category": "Industries",
    "website": "https://github.com/Escodoo/management-system-addons",
    "author": "Escodoo",
    "license": "AGPL-3",
    "installable": True,
    "application": True,
    "depends": [
        "web",
        "mail",
    ],
    "data": [
        "security/ir.model.access.csv",
        "views/dmn_diagram_category_views.xml",
        "views/dmn_diagram_views.xml",
        "views/dmn_template_views.xml",
        "views/dmn_template_wizard_views.xml",
    ],
    "demo": [
        "demo/dmn_template_categories.xml",
        "demo/dmn_templates.xml",
    ],
    "assets": {
        "web.assets_backend": [
            # DMN.js library - must be loaded first
            "dmn_modeler/static/src/lib/dmn-modeler.development.js",
            # Module files
            "dmn_modeler/static/src/scss/dmn_modeler.scss",
            "dmn_modeler/static/src/js/dmn_modeler.esm.js",
            "dmn_modeler/static/src/js/dmn_modeler_widget.esm.js",
            "dmn_modeler/static/src/xml/dmn_modeler.xml",
        ],
    },
    "images": ["static/description/icon.png"],
}
