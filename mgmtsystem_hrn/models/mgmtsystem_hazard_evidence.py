# Copyright 2024 - TODAY, Kaynnan Lemes <kaynnan.lemes@escodoo.com.br>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, fields, models, tools


class MgmtsystemHazardEvidence(models.Model):

    _name = "mgmtsystem.hazard.evidence"
    _description = "Evidence of hazard"
    _inherit = ["image.mixin"]
    _order = "sequence, id"

    company_id = fields.Many2one(
        "res.company", "Company", required=True, default=lambda self: self.env.company
    )
    hazard_id = fields.Many2one(
        "mgmtsystem.hazard", "Hazard", ondelete="cascade", required=False, index=True
    )
    name = fields.Char("Evidence", required=True)
    sequence = fields.Integer(default=10, index=True)
    image_1920 = fields.Image(required=True)
    description = fields.Text()
    can_image_1024_be_zoomed = fields.Boolean(
        "Can Image 1024 be zoomed",
        compute="_compute_can_image_1024_be_zoomed",
        store=True,
    )

    @api.depends("image_1920", "image_1024")
    def _compute_can_image_1024_be_zoomed(self):
        for image in self:
            image.can_image_1024_be_zoomed = (
                image.image_1920
                and tools.is_image_size_above(image.image_1920, image.image_1024)
            )
