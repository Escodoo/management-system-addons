# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import fields, models


class BpmnDiagramVersion(models.Model):
    """Model to store version history of BPMN diagrams."""

    _name = 'bpmn.diagram.version'
    _description = 'BPMN Diagram Version History'
    _order = 'change_date desc'

    diagram_id = fields.Many2one(
        'bpmn.diagram',
        string='Diagram',
        required=True,
        ondelete='cascade'
    )
    version = fields.Char(
        string='Version',
        required=True
    )
    bpmn_xml = fields.Text(
        string='BPMN XML',
        required=True
    )
    user_id = fields.Many2one(
        'res.users',
        string='Changed by',
        required=True,
        default=lambda self: self.env.user
    )
    change_date = fields.Datetime(
        string='Change Date',
        required=True,
        default=fields.Datetime.now
    )
    change_note = fields.Text(
        string='Change Note',
        help='Optional note describing the changes in this version.'
    )

