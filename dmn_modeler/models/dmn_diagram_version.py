# Copyright 2025 - TODAY, Marcel Savegnago <https://escodoo.com.br>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class DmnDiagramVersion(models.Model):
    """Model to store version history of DMN decision tables."""

    _name = "dmn.diagram.version"
    _description = "DMN Diagram Version History"
    _order = "change_date desc, id desc"

    diagram_id = fields.Many2one("dmn.diagram", required=True, ondelete="cascade")
    version = fields.Char(required=True)
    dmn_xml = fields.Text(required=True)
    user_id = fields.Many2one(
        "res.users",
        string="Changed by",
        required=True,
        default=lambda self: self.env.user,
    )
    change_date = fields.Datetime(required=True, default=fields.Datetime.now)
    change_note = fields.Text(
        help="Optional note describing the changes in this version.",
    )
