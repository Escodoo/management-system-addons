# Copyright 2025 - TODAY, Marcel Savegnago <https://escodoo.com.br>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class DmnDiagramCategory(models.Model):
    """Model to categorize DMN decision tables."""

    _name = "dmn.diagram.category"
    _description = "DMN Diagram Category"
    _order = "sequence, name, id"

    name = fields.Char(required=True)
    description = fields.Text()
    sequence = fields.Integer(default=10)
    diagram_ids = fields.One2many("dmn.diagram", "category_id", string="Diagrams")
    diagram_count = fields.Integer(compute="_compute_diagram_count")

    def _compute_diagram_count(self):
        for category in self:
            category.diagram_count = len(category.diagram_ids)
