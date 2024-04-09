# Copyright 2024 - TODAY, Kaynnan Lemes <kaynnan.lemes@escodoo.com.br>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, fields, models

from .common import _parse_risk_formula


class MgmtsystemHazardResidual_risk(models.Model):

    _inherit = "mgmtsystem.hazard.residual_risk"

    people_id = fields.Many2one(
        "mgmtsystem.hazard.people", "People Involved", required=True
    )

    @api.depends("probability_id", "severity_id", "usage_id", "people_id")
    def _compute_risk(self):
        for record in self:
            if (
                record.probability_id
                and record.severity_id
                and record.usage_id
                and record.people_id
            ):
                record.risk = _parse_risk_formula(
                    record.env.company.risk_computation_id.name,
                    record.probability_id.value,
                    record.severity_id.value,
                    record.usage_id.value,
                    record.people_id.value,
                )
            else:
                record.risk = False

    # Refactor Int to Float
    risk = fields.Float(compute=_compute_risk)
