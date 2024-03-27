# Copyright 2024 - TODAY, Kaynnan Lemes <kaynnan.lemes@escodoo.com.br>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class MaintenanceEquipment(models.Model):

    _inherit = "maintenance.equipment"

    required_safety_category_id = fields.Many2one(
        "maintenance.equipment.safety.category", string="Required Category"
    )
    installed_safety_category_id = fields.Many2one(
        "maintenance.equipment.safety.category", string="Installed Category"
    )
