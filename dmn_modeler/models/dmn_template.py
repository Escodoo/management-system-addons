# Copyright 2025 - TODAY, Marcel Savegnago <https://escodoo.com.br>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class DmnTemplate(models.Model):
    """Model to store DMN decision table templates."""

    _name = "dmn.template"
    _description = "DMN Template"
    _order = "sequence, name, id"

    name = fields.Char(required=True, help="Name of the DMN template.")
    description = fields.Text(help="Description of what this template is used for.")
    category_id = fields.Many2one(
        "dmn.template.category", help="Category of this template."
    )
    xml_content = fields.Text(
        required=True,
        help="DMN XML content of the template.",
    )
    icon = fields.Char(
        default="fa-file-o",
        help="Font Awesome icon class (e.g., fa-file-o, fa-table).",
    )
    sequence = fields.Integer(
        default=10, help="Order in which templates are displayed."
    )
    is_public = fields.Boolean(
        default=True,
        help="If checked, this template is available to all users.",
    )
    active = fields.Boolean(
        default=True,
        help="If unchecked, this template will be hidden.",
    )
    usage_count = fields.Integer(
        compute="_compute_usage_count",
        help="Number of times this template has been used.",
    )

    def _compute_usage_count(self):
        for template in self:
            template.usage_count = self.env["dmn.diagram"].search_count(
                [("template_id", "=", template.id)]
            )

    def action_use_template(self):
        """Action to create a new diagram from this template."""
        self.ensure_one()
        return {
            "name": f"Create Diagram from {self.name!r}",
            "type": "ir.actions.act_window",
            "res_model": "dmn.diagram",
            "view_mode": "form",
            "target": "current",
            "context": {
                "default_name": self.name,
                "default_dmn_xml": self.xml_content,
                "default_template_id": self.id,
            },
        }
