# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import fields, models, api
from odoo.exceptions import UserError


class BpmnDiagram(models.Model):
    """Model to store BPMN diagrams."""

    _name = 'bpmn.diagram'
    _description = 'BPMN Diagram'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'create_date desc'

    name = fields.Char(
        string='Name',
        required=True,
        tracking=True,
        help='The name of the BPMN diagram.'
    )
    description = fields.Text(
        string='Description',
        tracking=True,
        help='A detailed description of the BPMN diagram.'
    )
    version = fields.Char(
        string='Version',
        default='1.0.0',
        required=True,
        tracking=True,
        help='Version number of the diagram (e.g., 1.0.0, 2.1.3).'
    )
    state = fields.Selection([
        ('draft', 'Draft'),
        ('review', 'Under Review'),
        ('approved', 'Approved'),
        ('active', 'Active'),
        ('archived', 'Archived'),
    ], string='Status', default='draft', required=True, tracking=True,
       help='Current status of the BPMN diagram.')
    
    # Version management (automatic history tracking)
    version_history_ids = fields.One2many(
        'bpmn.diagram.version',
        'diagram_id',
        string='Version History',
        readonly=True
    )
    
    # Approval
    approval_user_id = fields.Many2one(
        'res.users',
        string='Approved by',
        readonly=True,
        tracking=True
    )
    approval_date = fields.Datetime(
        string='Approval Date',
        readonly=True,
        tracking=True
    )
    
    # Template
    template_id = fields.Many2one(
        'bpmn.template',
        string='Created from Template',
        readonly=True
    )
    
    # Category
    category_id = fields.Many2one(
        'bpmn.diagram.category',
        string='Category',
        tracking=True
    )
    
    # Diagram content
    bpmn_xml = fields.Text(
        string='BPMN XML',
        help='The XML definition of the BPMN diagram.',
        default='''<?xml version="1.0" encoding="UTF-8"?>
<bpmn:definitions xmlns:bpmn="http://www.omg.org/spec/BPMN/20100524/MODEL" xmlns:bpmndi="http://www.omg.org/spec/BPMN/20100524/DI" xmlns:dc="http://www.omg.org/spec/DD/20100524/DC" xmlns:di="http://www.omg.org/spec/DD/20100524/DI" id="Definitions_1" targetNamespace="http://bpmn.io/schema/bpmn" exporter="bpmn-js (https://demo.bpmn.io)" exporterVersion="11.0.1">
  <bpmn:process id="Process_1" isExecutable="false" />
  <bpmndi:BPMNDiagram id="BPMNDiagram_1">
    <bpmndi:BPMNPlane id="BPMNPlane_1" bpmnElement="Process_1" />
  </bpmndi:BPMNDiagram>
</bpmn:definitions>'''
    )
    svg_content = fields.Text(
        string='SVG Preview',
        help='SVG preview of the BPMN diagram for quick visualization.',
    )
    
    # Statistics
    element_count = fields.Integer(
        string='Element Count',
        compute='_compute_statistics',
        store=False
    )
    last_modified = fields.Datetime(
        string='Last Modified',
        compute='_compute_last_modified',
        store=True
    )
    
    def _compute_statistics(self):
        for record in self:
            # This will be populated by the JavaScript validation
            record.element_count = 0
    
    @api.depends('write_date')
    def _compute_last_modified(self):
        for record in self:
            record.last_modified = record.write_date or record.create_date
    
    def action_submit_for_review(self):
        """Submit diagram for review."""
        self.ensure_one()
        if self.state != 'draft':
            raise UserError('Only draft diagrams can be submitted for review.')
        self.write({'state': 'review'})
        return True
    
    def action_approve(self):
        """Approve the diagram."""
        self.ensure_one()
        if self.state not in ('review', 'draft'):
            raise UserError('Only draft or review diagrams can be approved.')
        self.write({
            'state': 'approved',
            'approval_user_id': self.env.user.id,
            'approval_date': fields.Datetime.now(),
        })
        return True
    
    def action_activate(self):
        """Activate the diagram."""
        self.ensure_one()
        if self.state != 'approved':
            raise UserError('Only approved diagrams can be activated.')
        self.write({'state': 'active'})
        return True
    
    def action_archive(self):
        """Archive the diagram."""
        self.ensure_one()
        self.write({'state': 'archived'})
        return True
    
    def action_unarchive(self):
        """Unarchive the diagram."""
        self.ensure_one()
        self.write({'state': 'draft'})
        return True
    
    def write(self, vals):
        """Override write to validate state and create version history."""
        # Fields that can only be edited when in draft state
        protected_fields = {'name', 'description', 'category_id', 'bpmn_xml'}
        fields_to_check = protected_fields.intersection(set(vals.keys()))
        
        if fields_to_check:
            for record in self:
                if record.state != 'draft':
                    raise UserError(
                        f'You can only edit the diagram (name, description, category, and BPMN content) '
                        f'when it is in "Draft" state. Current state: {dict(record._fields["state"].selection)[record.state]}.'
                    )
        
        # Create version history when BPMN XML changes
        if 'bpmn_xml' in vals and vals['bpmn_xml']:
            for record in self:
                if record.bpmn_xml and record.bpmn_xml != vals['bpmn_xml']:
                    # Create version history entry
                    self.env['bpmn.diagram.version'].create({
                        'diagram_id': record.id,
                        'version': record.version,
                        'bpmn_xml': record.bpmn_xml,
                        'user_id': self.env.user.id,
                        'change_date': fields.Datetime.now(),
                    })
        return super().write(vals)
