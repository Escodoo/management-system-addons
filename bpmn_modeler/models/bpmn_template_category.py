# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import fields, models


class BpmnTemplateCategory(models.Model):
    """Model to categorize BPMN templates."""

    _name = "bpmn.template.category"
    _description = "BPMN Template Category"
    _order = "sequence, name, id"

    name = fields.Char(required=True)
    description = fields.Html()
    sequence = fields.Integer(default=10)
    template_ids = fields.One2many("bpmn.template", "category_id", string="Templates")
    template_count = fields.Integer(compute="_compute_template_count")

    def _compute_template_count(self):
        for category in self:
            category.template_count = len(category.template_ids.filtered("active"))
