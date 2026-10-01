# Copyright 2024 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import _, models
from odoo.osv.expression import AND


class SaleOrder(models.Model):
    _inherit = "sale.order"

    def _try_apply_code(self, code):
        self.ensure_one()
        base_domain = self._get_trigger_domain()
        domain = AND([base_domain, [("mode", "=", "with_code"), ("code", "=", code)]])
        rule = self.env["loyalty.rule"].search(domain)
        if rule and rule._is_valid_order(self):
            return super()._try_apply_code(code)
        return {
            "error": _(
                "This code (%(code)s) is not available for this order.", code=code
            )
        }

    def _try_apply_program(self, program, coupon):
        self.ensure_one()
        if program and program._is_valid_order(self):
            return super()._try_apply_program(program, coupon)
        return {"error": _("The program is not available for this order.")}
