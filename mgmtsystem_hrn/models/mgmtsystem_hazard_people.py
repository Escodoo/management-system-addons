# Copyright 2024 - TODAY, Kaynnan Lemes <kaynnan.lemes@escodoo.com.br>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class Mgmtsystem_hazard_people(models.Model):

    _name = "mgmtsystem.hazard.people"
    _description = "Qty People of hazard"

    company_id = fields.Many2one(
        "res.company", "Company", required=True, default=lambda self: self.env.company
    )
    name = fields.Char("People Involved", required=True, translate=True)
    value = fields.Float(required=True)
    description = fields.Text(required=False, translate=False)
