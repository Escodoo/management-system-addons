# Copyright 2024 - TODAY, Kaynnan Lemes <kaynnan.lemes@escodoo.com.br>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from datetime import datetime

from odoo import tools
from odoo.tests import common

DATE_FORMAT = tools.DEFAULT_SERVER_DATE_FORMAT


class TestMgmtsystemHRN(common.TransactionCase):
    def test_hazard_risk_computation_a_time_b_time_c_time_d(self):
        # (A * B ) + (C * D)
        computation_risk = self.env["mgmtsystem.hazard.risk.computation"].create(
            {
                "name": "(A * B ) + (C * D)",
                "description": "Risk = (Probability A x Severity B) + (Usage C x People D)",
            }
        )
        self.env.user.company_id.risk_computation_id = computation_risk

        type_rec = self.env.ref("mgmtsystem_hazard.type_ohsas_position")
        hazard_rec = self.env.ref("mgmtsystem_hazard.hazard_spilling")
        origin_rec = self.env.ref("mgmtsystem_hazard.origin_ignition_gas")

        department_rec = self.env["hr.department"].create({"name": "Department 01"})

        # People = 5
        people_rec = self.env["mgmtsystem.hazard.people"].create(
            {
                "name": "1 - 10",
                "value": "5",
            }
        )

        # Probability = 2
        probability_rec = self.env.ref("mgmtsystem_hazard.probability_maybe")

        # Severity = 3
        severity_rec = self.env.ref("mgmtsystem_hazard.severity_heavy")

        # Usage = 5
        usage_rec = self.env.ref("mgmtsystem_hazard.usage_very_high")
        r_type_rec = self.env.ref("mgmtsystem_hazard_risk.risk_type_physical")

        record = self.env["mgmtsystem.hazard"].create(
            {
                "name": "Hazard Test 02",
                "type_id": type_rec.id,
                "hazard_id": hazard_rec.id,
                "origin_id": origin_rec.id,
                "department_id": department_rec.id,
                "responsible_user_id": self.env.user.id,
                "analysis_date": datetime.now().strftime(DATE_FORMAT),
                "probability_id": probability_rec.id,
                "severity_id": severity_rec.id,
                "people_id": people_rec.id,
                "usage_id": usage_rec.id,
                "risk_type_id": r_type_rec.id,
            }
        )
        self.assertEqual(record.risk, 31)  # (2 * 3) + (5 * 5)
