# Copyright 2024 - TODAY, Kaynnan Lemes <kaynnan.lemes@escodoo.com.br>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class MgmtsystemHazardSeverity(models.Model):

    _inherit = "mgmtsystem.hazard.severity"
    # Refactor Int to Float
    value = fields.Float(required=True)
