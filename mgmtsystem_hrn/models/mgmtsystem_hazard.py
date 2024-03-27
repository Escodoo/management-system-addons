# Copyright 2024 - TODAY, Kaynnan Lemes <kaynnan.lemes@escodoo.com.br>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, fields, models

from .common import _parse_risk_formula


class MgmtsystemHazard(models.Model):

    _inherit = "mgmtsystem.hazard"

    people_id = fields.Many2one("mgmtsystem.hazard.people", "People Involved")
    evidence_ids = fields.One2many(
        "mgmtsystem.hazard.evidence", "hazard_id", "Evidence"
    )

    @api.depends("probability_id", "severity_id", "usage_id", "people_id")
    def _compute_risk(self):
        for hazard in self:
            if (
                hazard.probability_id
                and hazard.severity_id
                and hazard.usage_id
                and hazard.people_id
            ):
                hazard.risk = _parse_risk_formula(
                    self.env.company.risk_computation_id.name,
                    hazard.probability_id.value,
                    hazard.severity_id.value,
                    hazard.usage_id.value,
                    hazard.people_id.value,
                )
            else:
                hazard.risk = False

    # Refactor Int to Float
    risk = fields.Float(compute=_compute_risk)
