# Copyright 2025 - TODAY, Marcel Savegnago <https://escodoo.com.br>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class DmnTemplateCategory(models.Model):
    """Model to categorize DMN templates."""

    _name = "dmn.template.category"
    _description = "DMN Template Category"
    _order = "sequence, name, id"

    name = fields.Char(required=True)
    description = fields.Html()
    sequence = fields.Integer(default=10)
    template_ids = fields.One2many("dmn.template", "category_id", string="Templates")
    template_count = fields.Integer(compute="_compute_template_count")

    def _compute_template_count(self):
        for category in self:
            category.template_count = len(category.template_ids.filtered("active"))
