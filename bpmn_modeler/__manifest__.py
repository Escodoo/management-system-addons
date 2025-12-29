{
    'name': 'BPMN Modeler',
    'summary': 'Module to model BPMN flows using bpmn.js and Odoo\'s OWL framework.',
    'version': '17.0.1.0.0',
    'category': 'Industries',
    'website': 'https://github.com/OCA/bpmn_modeler',
    'author': 'OCA',
    'license': 'AGPL-3',
    'installable': True,
    'application': True,
    'depends': [
        'web',
        'mail',
    ],
    'data': [
        'security/ir.model.access.csv',
        'views/bpmn_diagram_category_views.xml',
        'views/bpmn_template_views.xml',
        'views/bpmn_template_wizard_views.xml',
        'views/bpmn_diagram_views.xml',
    ],
    'demo': [
        'demo/bpmn_template_categories.xml',
        'demo/bpmn_templates.xml',
    ],
    'assets': {
        'web.assets_backend': [
            # BPMN.js library - must be loaded first
            'bpmn_modeler/static/src/lib/bpmn-modeler.development.js',
            # Module files
            'bpmn_modeler/static/src/scss/bpmn_modeler.scss',
            'bpmn_modeler/static/src/js/bpmn_modeler.js',
            'bpmn_modeler/static/src/js/bpmn_modeler_widget.js',
            'bpmn_modeler/static/src/xml/bpmn_modeler.xml',
        ],
    },
    'images': ['static/description/icon.png'],
}
