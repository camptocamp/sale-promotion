# Copyright 2024 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo.tests import Form, tagged
from odoo.tests.common import TransactionCase


@tagged("-at_install", "post_install")
class Common(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env = cls.env(context=dict(cls.env.context, tracking_disable=True))

    @classmethod
    def create_order(cls, add_line=True):
        # A simple order with 1 ordered product
        cls.partner = cls.env["res.partner"].create({"name": "Test Customer"})
        cls.product = cls.env["product.product"].create({"name": "service"})
        with Form(cls.env["sale.order"]) as order_form:
            order_form.partner_id = cls.partner
            if add_line:
                with order_form.order_line.new() as order_line:
                    order_line.product_id = cls.product
                    order_line.name = cls.product.name
                    order_line.product_uom_qty = 1
                    order_line.product_uom = cls.product.uom_id
                    order_line.price_unit = 42.0
        return order_form.record

    @classmethod
    def create_program(cls, rule_values=None, **extra_vals):
        default_rule_values = {}
        if rule_values:
            default_rule_values = rule_values
        values = {
            "name": "Test Program",
            "program_type": "promo_code",
            "rule_ids": [(0, 0, default_rule_values)],
        }
        if extra_vals:
            values.update(extra_vals)
        return cls.env["loyalty.program"].create(values)

    @classmethod
    def create_rule(cls, **extra_vals):
        program = cls.create_program(rule_values=extra_vals)
        return program.rule_ids
