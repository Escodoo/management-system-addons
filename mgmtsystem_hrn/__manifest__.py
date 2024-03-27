# Copyright 2024 - TODAY, Escodoo
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

{
    "name": "Management System - HRN",
    "version": "16.0.1.0.0",
    "author": "Escodoo, Odoo Community Association (OCA)",
    "website": "https://github.com/Escodoo/management-system-addons",
    "license": "AGPL-3",
    "category": "Management System",
    "depends": ["mgmtsystem_hazard_risk", "maintenance"],
    "data": [
        "security/ir.model.access.csv",
        "security/mgmtsystem_hazard_security.xml",
        "views/maintenance_equipment.xml",
        "views/maintenance_equipment_safety_category.xml",
        "views/mgmtsystem_hazard_people.xml",
        "views/mgmtsystem_hazard_residual_risk.xml",
        "views/mgmtsystem_hazard_evidence.xml",
        "views/mgmtsystem_hazard.xml",
    ],
}
