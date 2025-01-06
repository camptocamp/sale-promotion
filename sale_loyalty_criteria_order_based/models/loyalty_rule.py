# Copyright 2022 Ooops404
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
# Copyright 2024 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)
import ast

from odoo import _, api, fields, models
from odoo.exceptions import UserError
from odoo.osv.expression import expression


class LoyaltyRule(models.Model):
    _inherit = "loyalty.rule"

    rule_order_domain = fields.Char(string="Based on Order", default="[]")

    @api.constrains("rule_order_domain")
    def _constrain_rule_order_domain(self):
        model = self.env["sale.order"]
        for rule in self:
            if not rule.rule_order_domain:
                continue
            try:
                domain = ast.literal_eval(rule.rule_order_domain)
                # Ensuring that domain is valid for sale.order
                expression(domain, model)
            except Exception as e:
                raise UserError(_("Invalid domain on rule")) from e

    def _is_valid_order(self, order):
        """Check that we can apply the rule on current order"""
        self.ensure_one()
        order.ensure_one()
        domain = ast.literal_eval(self.rule_order_domain)
        if domain:
            return bool(order.filtered_domain(domain))
        return True
