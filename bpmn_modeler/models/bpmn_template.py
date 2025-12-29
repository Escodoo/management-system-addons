# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import fields, models


class BpmnTemplate(models.Model):
    """Model to store BPMN diagram templates."""

    _name = 'bpmn.template'
    _description = 'BPMN Template'
    _order = 'sequence, name'

    name = fields.Char(
        string='Template Name',
        required=True,
        help='Name of the BPMN template.'
    )
    description = fields.Text(
        string='Description',
        help='Description of what this template is used for.'
    )
    category_id = fields.Many2one(
        'bpmn.template.category',
        string='Category',
        help='Category of this template.'
    )
    xml_content = fields.Text(
        string='BPMN XML Content',
        required=True,
        help='BPMN XML content of the template.'
    )
    icon = fields.Char(
        string='Icon',
        default='fa-file-o',
        help='Font Awesome icon class (e.g., fa-file-o, fa-sitemap).'
    )
    sequence = fields.Integer(
        string='Sequence',
        default=10,
        help='Order in which templates are displayed.'
    )
    is_public = fields.Boolean(
        string='Public Template',
        default=True,
        help='If checked, this template is available to all users.'
    )
    active = fields.Boolean(
        string='Active',
        default=True,
        help='If unchecked, this template will be hidden.'
    )
    usage_count = fields.Integer(
        string='Usage Count',
        compute='_compute_usage_count',
        help='Number of times this template has been used.'
    )

    def _compute_usage_count(self):
        for template in self:
            template.usage_count = self.env['bpmn.diagram'].search_count([
                ('template_id', '=', template.id)
            ])

    def action_use_template(self):
        """Action to create a new diagram from this template."""
        self.ensure_one()
        return {
            'name': f'Create Diagram from "{self.name}"',
            'type': 'ir.actions.act_window',
            'res_model': 'bpmn.diagram',
            'view_mode': 'form',
            'target': 'current',
            'context': {
                'default_name': self.name,
                'default_bpmn_xml': self.xml_content,
                'default_template_id': self.id,
            }
        }

