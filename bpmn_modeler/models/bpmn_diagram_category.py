# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import fields, models


class BpmnDiagramCategory(models.Model):
    """Model to categorize BPMN diagrams."""

    _name = "bpmn.diagram.category"
    _description = "BPMN Diagram Category"
    _order = "sequence, name"

    name = fields.Char(required=True)
    description = fields.Text()
    sequence = fields.Integer(default=10)
    diagram_ids = fields.One2many("bpmn.diagram", "category_id", string="Diagrams")
    diagram_count = fields.Integer(compute="_compute_diagram_count")

    def _compute_diagram_count(self):
        for category in self:
            category.diagram_count = len(category.diagram_ids)
