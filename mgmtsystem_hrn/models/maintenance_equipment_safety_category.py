# Copyright 2024 - TODAY, Kaynnan Lemes <kaynnan.lemes@escodoo.com.br>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).


from odoo import _, api, fields, models
from odoo.exceptions import UserError


class MaintenanceEquipmentSafetyCategory(models.Model):

    _name = "maintenance.equipment.safety.category"
    _description = "Maintenance Equipment Safety Category"

    name = fields.Char(required=True)
    description = fields.Char()

    required_equipment_ids = fields.One2many(
        "maintenance.equipment",
        "required_safety_category_id",
        string="Equipments Safety Required Category",
    )
    installed_equipment_ids = fields.One2many(
        "maintenance.equipment",
        "installed_safety_category_id",
        string="Equipments Safety Installed Category",
    )
    equipment_count = fields.Integer(
        string="Equipment", compute="_compute_equipment_count"
    )

    @api.ondelete(at_uninstall=False)
    def _unlink_except_contains_maintenance_requests(self):
        for safety in self:
            equipments = safety.required_equipment_ids | safety.installed_equipment_ids
            if equipments:
                unique_equipments = set(equipments.mapped("name"))
                equipment_names = "\n".join("- " + name for name in unique_equipments)
                raise UserError(
                    _(
                        "You cannot delete an Safety Category containing the equipment(s):\n%s"
                    )
                    % equipment_names
                )

    def _compute_equipment_count(self):
        mapped_data = {}
        for category in self:
            # Filtrar equipamentos associados aos safety categories desta categoria
            equipments = (
                self.env["maintenance.equipment"]
                .sudo()
                .search(
                    [
                        "|",
                        ("required_safety_category_id", "=", category.id),
                        ("installed_safety_category_id", "=", category.id),
                    ]
                )
            )
            # Contar equipamentos distintos
            mapped_data[category.id] = len(equipments)

        # Atualizar contagem de equipamentos para cada categoria
        for category in self:
            category.equipment_count = mapped_data.get(category.id, 0)
