# Copyright 2024 - TODAY, Kaynnan Lemes <kaynnan.lemes@escodoo.com.br>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import _
from odoo.exceptions import UserError
from odoo.tools.safe_eval import safe_eval


def _parse_risk_formula(formula, a, b, c, d):
    """Calculate the risk replacing the variables A, B, C, D into the formula."""
    if not formula:
        raise UserError(
            _("You must define the company's risk computing formula. Go to settings")
        )
    f = (
        formula.replace("A", str(a))
        .replace("B", str(b))
        .replace("C", str(c))
        .replace("D", str(d))
    )
    return safe_eval(f)
