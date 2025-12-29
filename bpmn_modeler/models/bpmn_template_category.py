# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import fields, models


class BpmnTemplateCategory(models.Model):
    """Model to categorize BPMN templates."""

    _name = 'bpmn.template.category'
    _description = 'BPMN Template Category'
    _order = 'sequence, name'

    name = fields.Char(
        string='Category Name',
        required=True
    )
    description = fields.Html(
        string='Description'
    )
    sequence = fields.Integer(
        string='Sequence',
        default=10
    )
    template_ids = fields.One2many(
        'bpmn.template',
        'category_id',
        string='Templates'
    )
    template_count = fields.Integer(
        string='Template Count',
        compute='_compute_template_count'
    )

    def _compute_template_count(self):
        for category in self:
            category.template_count = len(category.template_ids.filtered('active'))

