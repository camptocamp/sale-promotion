# Copyright 2024 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo.exceptions import UserError

from .common import Common


class TestMethods(Common):
    def test_constrain_rule(self):
        # Trying to set rule_order_domain as an invalid domain should
        # raise a UserError
        regex = r"Invalid domain on rule"
        # invalid expression
        domain = '{"wrong": "wrong"}'
        with self.assertRaisesRegex(UserError, regex):
            self.create_rule(rule_order_domain=domain)
        # invalid expression
        domain = "wrong"
        with self.assertRaisesRegex(UserError, regex):
            self.create_rule(rule_order_domain=domain)
        # valid expression, wrong field
        domain = '[("wrong_field", "=", False)]'
        with self.assertRaisesRegex(UserError, regex):
            self.create_rule(rule_order_domain=domain)
        # Valid domains shouldn't raise an exception
        self.create_rule(rule_order_domain='[("partner_id", "=", 42)]')
        self.create_rule(rule_order_domain="[]")

    def test_constrain_program(self):
        # Trying to set rule_order_domain as an invalid domain should
        # raise a UserError
        regex = r"Invalid domain on program"
        # invalid expression
        domain = '{"wrong": "wrong"}'
        with self.assertRaisesRegex(UserError, regex):
            self.create_program(rule_order_domain=domain)
        # invalid expression
        domain = "wrong"
        with self.assertRaisesRegex(UserError, regex):
            self.create_program(rule_order_domain=domain)
        # valid expression, wrong field
        domain = '[("wrong_field", "=", False)]'
        with self.assertRaisesRegex(UserError, regex):
            self.create_program(rule_order_domain=domain)
        # Valid domains shouldn't raise an exception
        self.create_program(rule_order_domain='[("partner_id", "=", 42)]')
        self.create_program(rule_order_domain="[]")

    def test_rule_domain(self):
        order = self.create_order()
        all_orders_rule = self.create_rule()
        self.assertTrue(all_orders_rule._is_valid_order(order))
        other_order_rule = self.create_rule(
            rule_order_domain=f"[('id', '!=', {order.id})]"
        )
        self.assertFalse(other_order_rule._is_valid_order(order))
        this_order_rule = self.create_rule(
            rule_order_domain=f"[('id', '=', {order.id})]"
        )
        self.assertTrue(this_order_rule._is_valid_order(order))

    def test_program_domain(self):
        order = self.create_order()
        all_orders_program = self.create_program()
        self.assertTrue(all_orders_program._is_valid_order(order))
        other_order_program = self.create_program(
            rule_order_domain=f"[('id', '!=', {order.id})]"
        )
        self.assertFalse(other_order_program._is_valid_order(order))
        this_order_program = self.create_program(
            rule_order_domain=f"[('id', '=', {order.id})]"
        )
        self.assertTrue(this_order_program._is_valid_order(order))
