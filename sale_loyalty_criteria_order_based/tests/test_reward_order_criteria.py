# Copyright 2024 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from .common import Common


class TestRewardOrderCriteria(Common):
    def test_apply_code_no_domain(self):
        self.create_rule(code="TEST", minimum_qty=1)
        # Rule is valid when 1 product is sold, with code TEST
        # There's no line in the order, it should return an error
        order_no_line = self.create_order(add_line=False)
        result = order_no_line._try_apply_code("TEST")
        self.assertEqual(
            result.get("error"),
            "You don't have the required product quantities on your sales order.",
        )
        # If we apply it on an order with a line, no error should be returned
        order_with_line = self.create_order()
        result = order_with_line._try_apply_code("TEST")
        self.assertNotIn("error", result)

    def test_apply_rule_with_domain(self):
        # A rule only valid for draft orders with 1 qty sold at least
        self.create_rule(
            code="TEST_WITH_DOMAIN", rule_order_domain="[('state', '=', 'draft')]"
        )
        # Order is draft but doesn't have a line
        order = self.create_order(add_line=False)
        result = order._try_apply_code("TEST_WITH_DOMAIN")
        self.assertEqual(
            result.get("error"),
            "You don't have the required product quantities on your sales order.",
        )
        # Order is draft and have a line -> no error
        order = self.create_order()
        result = order._try_apply_code("TEST_WITH_DOMAIN")
        self.assertNotIn("error", result)
        # Order is not draft -> Should return an error
        order = self.create_order()
        order.action_confirm()
        result = order._try_apply_code("TEST_WITH_DOMAIN")
        self.assertEqual(
            result.get("error"),
            "This code (TEST_WITH_DOMAIN) is not available for this order.",
        )

    def test_apply_program_with_domain(self):
        # Very similar test then `test_apply_code_no_domain`, except domain is on
        # the program.
        # A program only valid for draft orders, with a rule allowing
        # this code to be used only when there's a product sold at least
        self.create_program(
            rule_values={
                "code": "TEST_WITH_DOMAIN",
            },
            rule_order_domain="[('state', '=', 'draft')]",
        )
        # Order is draft but doesn't have a line
        order = self.create_order(add_line=False)
        result = order._try_apply_code("TEST_WITH_DOMAIN")
        self.assertEqual(
            result.get("error"),
            "You don't have the required product quantities on your sales order.",
        )
        # Order is draft and have a line -> no error
        order = self.create_order()
        result = order._try_apply_code("TEST_WITH_DOMAIN")
        self.assertNotIn("error", result)
        # Order is not draft -> Should return an error
        order = self.create_order()
        order.action_confirm()
        result = order._try_apply_code("TEST_WITH_DOMAIN")
        self.assertEqual(
            result.get("error"), "The program is not available for this order."
        )
