# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import fields, models, api


class BpmnTemplateWizard(models.TransientModel):
    """Wizard to select a template when creating a new diagram."""

    _name = 'bpmn.template.wizard'
    _description = 'BPMN Template Selection Wizard'

    template_id = fields.Many2one(
        'bpmn.template',
        string='Template',
        required=True,
        domain=[('active', '=', True)]
    )
    name = fields.Char(
        string='Diagram Name',
        required=True
    )
    description = fields.Text(
        string='Description'
    )

    @api.model
    def default_get(self, fields_list):
        """Set default name from template if available."""
        res = super().default_get(fields_list)
        if 'template_id' in res and res.get('template_id'):
            template = self.env['bpmn.template'].browse(res['template_id'])
            if 'name' in fields_list and not res.get('name'):
                res['name'] = template.name
        return res

    @api.onchange('template_id')
    def _onchange_template_id(self):
        """Update name and description when template changes."""
        if self.template_id:
            self.name = self.template_id.name
            self.description = self.template_id.description

    def action_create_diagram(self):
        """Create a new diagram from the selected template."""
        self.ensure_one()
        diagram = self.env['bpmn.diagram'].create({
            'name': self.name,
            'description': self.description,
            'bpmn_xml': self.template_id.xml_content,
            'template_id': self.template_id.id,
            'version': '1.0.0',
            'state': 'draft',
        })
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'bpmn.diagram',
            'view_mode': 'form',
            'res_id': diagram.id,
            'target': 'current',
        }

