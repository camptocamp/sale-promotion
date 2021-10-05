# Copyright 2021 Tecnativa - David Vidal
# Copyright 2021 Camptocamp - Silvio Gregorini
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


def _get_data_from_triggers(recs, triggers) -> dict:
    """Retrieves data from records `recs` on fields passed within `triggers`

    :param models.Model recs: records to be read
    :param set[str] triggers: set of field names
    :returns: dict mapping each record ID to a list of fields values
    """
    return {r.id: [r[t] for t in triggers] for r in recs}


class SaleOrder(models.Model):
    _inherit = "sale.order"

    # Used in UI to hide the manual button
    auto_refresh_coupon = fields.Boolean(
        related="company_id.auto_refresh_coupon",
    )

    @api.model
    def _get_auto_refresh_coupons_triggers(self) -> set:
        """Returns set of fields which trigger :meth:`_auto_refresh_coupons`

        Hook method to be overridden if necessary
        """
        return {
            "order_line",
            "partner_id",
        }

    @api.model_create_multi
    def create(self, vals_list):
        if self.env.context.get("skip_auto_refresh_coupons"):
            return super().create(vals_list)

        self_ctx = self.with_context(skip_auto_refresh_coupons=True)
        orders = super(SaleOrder, self_ctx).create(vals_list)
        orders._auto_refresh_coupons()
        return orders

    def write(self, vals):
        if self.env.context.get("skip_auto_refresh_coupons", False):
            return super().write(vals)

        triggers = self._get_auto_refresh_coupons_triggers()
        old_data = _get_data_from_triggers(self, triggers)
        self_ctx = self.with_context(skip_auto_refresh_coupons=True)
        res = super(SaleOrder, self_ctx).write(vals)
        new_data = _get_data_from_triggers(self, triggers)
        if old_data != new_data:
            self._auto_refresh_coupons()
        return res

    def _auto_refresh_coupons(self):
        orders = self.filtered(type(self)._allow_recompute_coupon_lines)
        if orders:
            orders = orders.with_context(skip_auto_refresh_coupons=True)
            orders.recompute_coupon_lines()

    def _allow_recompute_coupon_lines(self):
        """Returns whether reward lines in order ``self`` can be recomputed
        automatically.

        Hook method, to be overridden for custom behaviours.

        :return: True if the current SO allows automatic recomputation for
        reward lines, False otherwise.
        """
        self.ensure_one()
        return self.auto_refresh_coupon and self.state in ("draft", "sent")


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    @api.model
    def _get_auto_refresh_coupons_triggers(self) -> set:
        """Returns set of fields which trigger :meth:`_auto_refresh_coupons`

        Hook method to be overridden if necessary
        """
        return {
            "discount",
            "product_id",
            "price_unit",
            "product_uom",
            "product_uom_qty",
            "tax_id",
        }

    @api.model_create_multi
    def create(self, vals_list):
        if self.env.context.get("skip_auto_refresh_coupons", False):
            return super().create(vals_list)

        self_ctx = self.with_context(skip_auto_refresh_coupons=True)
        lines = super(SaleOrderLine, self_ctx).create(vals_list)
        lines.mapped("order_id")._auto_refresh_coupons()
        return lines

    def write(self, vals):
        if self.env.context.get("skip_auto_refresh_coupons", False):
            return super().write(vals)

        triggers = self._get_auto_refresh_coupons_triggers()
        orders = self.mapped("order_id")
        old_data = _get_data_from_triggers(self, triggers)
        self_ctx = self.with_context(skip_auto_refresh_coupons=True)
        res = super(SaleOrderLine, self_ctx).write(vals)
        orders |= self.mapped("order_id")
        new_data = _get_data_from_triggers(self, triggers)
        if old_data != new_data:
            orders._auto_refresh_coupons()
        return res

    def unlink(self):
        if self.env.context.get("skip_auto_refresh_coupons", False):
            return super().unlink()

        orders = self.mapped("order_id")
        self_ctx = self.with_context(skip_auto_refresh_coupons=True)
        res = super(SaleOrderLine, self_ctx).unlink()
        orders._auto_refresh_coupons()
        return res
