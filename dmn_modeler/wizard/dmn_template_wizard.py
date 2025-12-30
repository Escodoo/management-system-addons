# Copyright 2025 - TODAY, Marcel Savegnago <https://escodoo.com.br>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class DmnTemplateWizard(models.TransientModel):
    """Wizard to select a template when creating a new diagram."""

    _name = "dmn.template.wizard"
    _description = "DMN Template Selection Wizard"

    template_id = fields.Many2one(
        "dmn.template",
        string="Template",
        required=True,
        domain=[("active", "=", True)],
    )
    name = fields.Char(required=True)
    description = fields.Text()

    @api.model
    def default_get(self, fields_list):
        """Set default name from template if available."""
        res = super().default_get(fields_list)
        if "template_id" in res and res.get("template_id"):
            template = self.env["dmn.template"].browse(res["template_id"])
            if "name" in fields_list and not res.get("name"):
                res["name"] = template.name
        return res

    @api.onchange("template_id")
    def _onchange_template_id(self):
        """Update name and description when template changes."""
        if self.template_id:
            self.name = self.template_id.name
            self.description = self.template_id.description

    def action_create_diagram(self):
        """Create a new diagram from the selected template."""
        self.ensure_one()
        diagram = self.env["dmn.diagram"].create(
            {
                "name": self.name,
                "description": self.description,
                "dmn_xml": self.template_id.xml_content,
                "template_id": self.template_id.id,
                "version": "1.0.0",
                "state": "draft",
            }
        )
        return {
            "type": "ir.actions.act_window",
            "res_model": "dmn.diagram",
            "view_mode": "form",
            "res_id": diagram.id,
            "target": "current",
        }
