# Copyright 2025 - TODAY, Marcel Savegnago <https://escodoo.com.br>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import _, api, fields, models
from odoo.exceptions import UserError


class DmnDiagram(models.Model):
    """Model to store DMN decision tables."""

    _name = "dmn.diagram"
    _description = "DMN Diagram"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "create_date desc, id desc"

    name = fields.Char(
        required=True,
        tracking=True,
        help="The name of the DMN decision table.",
    )
    description = fields.Text(
        tracking=True,
        help="A detailed description of the DMN decision table.",
    )
    version = fields.Char(
        default="1.0.0",
        required=True,
        tracking=True,
        help="Version number of the diagram (e.g., 1.0.0, 2.1.3).",
    )
    state = fields.Selection(
        [
            ("draft", "Draft"),
            ("review", "Under Review"),
            ("approved", "Approved"),
            ("active", "Active"),
            ("archived", "Archived"),
        ],
        string="Status",
        default="draft",
        required=True,
        tracking=True,
        help="Current status of the DMN decision table.",
    )

    # Version management (automatic history tracking)
    version_history_ids = fields.One2many(
        "dmn.diagram.version", "diagram_id", string="Version History", readonly=True
    )

    # Approval
    approval_user_id = fields.Many2one(
        "res.users", string="Approved by", readonly=True, tracking=True
    )
    approval_date = fields.Datetime(readonly=True, tracking=True)

    # Template
    template_id = fields.Many2one(
        "dmn.template", string="Created from Template", readonly=True
    )

    # Category
    category_id = fields.Many2one(
        "dmn.diagram.category", string="Category", tracking=True
    )

    # Diagram content
    dmn_xml = fields.Text(
        string="DMN XML",
        help="The XML definition of the DMN decision table.",
        default="""<?xml version="1.0" encoding="UTF-8"?>
<dmn:definitions xmlns:dmn="https://www.omg.org/spec/DMN/20191111/MODEL/"
                xmlns:dmndi="https://www.omg.org/spec/DMN/20191111/DMNDI/"
                xmlns:dc="http://www.omg.org/spec/DMN/20180521/DC/"
                xmlns:di="http://www.omg.org/spec/DMN/20180521/DI/"
                id="Definitions_1"
                namespace="http://camunda.org/schema/1.0/dmn"
                exporter="dmn-js"
                exporterVersion="17.5.0">
  <dmn:decision id="Decision_1" name="Decision 1">
    <dmn:decisionTable id="DecisionTable_1"/>
  </dmn:decision>
  <dmndi:DMNDI>
    <dmndi:DMNDiagram id="DMNDiagram_1">
      <dmndi:DMNShape id="DMNShape_Decision_1" dmnElementRef="Decision_1">
        <dc:Bounds height="80" width="180" x="100" y="100"/>
      </dmndi:DMNShape>
    </dmndi:DMNDiagram>
  </dmndi:DMNDI>
</dmn:definitions>""",
    )
    svg_content = fields.Text(
        string="SVG Preview",
        help="SVG preview of the DMN decision table for quick visualization.",
    )

    # Statistics
    element_count = fields.Integer(compute="_compute_statistics", store=False)
    last_modified = fields.Datetime(compute="_compute_last_modified", store=True)

    def _compute_statistics(self):
        for record in self:
            # This will be populated by the JavaScript validation
            record.element_count = 0

    @api.depends("write_date")
    def _compute_last_modified(self):
        for record in self:
            record.last_modified = record.write_date or record.create_date

    def action_submit_for_review(self):
        """Submit diagram for review."""
        self.ensure_one()
        if self.state != "draft":
            raise UserError(_("Only draft diagrams can be submitted for review."))
        self.write({"state": "review"})
        return True

    def action_approve(self):
        """Approve the diagram."""
        self.ensure_one()
        if self.state not in ("review", "draft"):
            raise UserError(_("Only draft or review diagrams can be approved."))
        self.write(
            {
                "state": "approved",
                "approval_user_id": self.env.user.id,
                "approval_date": fields.Datetime.now(),
            }
        )
        return True

    def action_activate(self):
        """Activate the diagram."""
        self.ensure_one()
        if self.state != "approved":
            raise UserError(_("Only approved diagrams can be activated."))
        self.write({"state": "active"})
        return True

    def action_archive(self):
        """Archive the diagram."""
        self.ensure_one()
        self.write({"state": "archived"})
        return True

    def action_unarchive(self):
        """Unarchive the diagram."""
        self.ensure_one()
        self.write({"state": "draft"})
        return True

    def write(self, vals):
        """Override write to validate state and create version history."""
        # Fields that can only be edited when in draft state
        protected_fields = {"name", "description", "category_id", "dmn_xml"}
        fields_to_check = protected_fields.intersection(set(vals.keys()))

        if fields_to_check:
            for record in self:
                if record.state != "draft":
                    state_selection = dict(record._fields["state"].selection)
                    raise UserError(
                        _(
                            "You can only edit the diagram (name, description, "
                            "category, and DMN content) when it is in 'Draft' "
                            "state. Current state: %s."
                        )
                        % state_selection[record.state]
                    )

        # Create version history when DMN XML changes
        if "dmn_xml" in vals and vals["dmn_xml"]:
            # Get default value for dmn_xml field
            field = self._fields["dmn_xml"]
            if callable(field.default):
                default_xml = field.default(self)
            else:
                default_xml = field.default
            for record in self:
                # Only create version if there was a previous XML value
                # and it's different from the new value
                # Skip if this is the first time setting XML (value was default)
                if (
                    record.dmn_xml
                    and record.dmn_xml != vals["dmn_xml"]
                    and record.dmn_xml != default_xml
                ):
                    # Create version history entry
                    self.env["dmn.diagram.version"].create(
                        {
                            "diagram_id": record.id,
                            "version": record.version,
                            "dmn_xml": record.dmn_xml,
                            "user_id": self.env.user.id,
                            "change_date": fields.Datetime.now(),
                        }
                    )
        return super().write(vals)
