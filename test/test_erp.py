import os
import sys
import tempfile
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from erp import ERPSystem


def make_erp() -> ERPSystem:
    tmp = tempfile.NamedTemporaryFile(suffix=".json", delete=False)
    tmp.close()
    os.remove(tmp.name)          # storage will create it fresh
    return ERPSystem(data_path=tmp.name)


class TestAuthentication(unittest.TestCase):

    def setUp(self):
        self.erp = make_erp()

    def tearDown(self):
        try:
            os.remove(self.erp.storage.filepath)
        except FileNotFoundError:
            pass

    def test_register_success(self):
        ok, msg = self.erp.register_user("alice", "secret123")
        self.assertTrue(ok)
        self.assertIn("alice", msg)

    def test_register_duplicate_username(self):
        self.erp.register_user("bob", "pass")
        ok, msg = self.erp.register_user("bob", "other")
        self.assertFalse(ok)

    def test_register_empty_fields(self):
        ok, _ = self.erp.register_user("", "pass")
        self.assertFalse(ok)
        ok, _ = self.erp.register_user("user", "")
        self.assertFalse(ok)

    def test_login_success(self):
        self.erp.register_user("carol", "pw99")
        ok, user = self.erp.authenticate("carol", "pw99")
        self.assertTrue(ok)
        self.assertEqual(user.username, "carol")

    def test_login_wrong_password(self):
        self.erp.register_user("dave", "correct")
        ok, user = self.erp.authenticate("dave", "wrong")
        self.assertFalse(ok)
        self.assertIsNone(user)

    def test_login_unknown_user(self):
        ok, user = self.erp.authenticate("nobody", "x")
        self.assertFalse(ok)
        self.assertIsNone(user)


class TestCustomers(unittest.TestCase):

    def setUp(self):
        self.erp = make_erp()

    def tearDown(self):
        try:
            os.remove(self.erp.storage.filepath)
        except FileNotFoundError:
            pass

    def test_add_customer(self):
        ok, _ = self.erp.add_customer("Acme", "123 Main St", "555-0100", "acme@example.com")
        self.assertTrue(ok)
        self.assertEqual(len(self.erp.customers), 1)
        self.assertEqual(self.erp.customers[0].name, "Acme")

    def test_add_customer_empty_name(self):
        ok, _ = self.erp.add_customer("", "addr", "phone", "email")
        self.assertFalse(ok)

    def test_update_customer(self):
        self.erp.add_customer("Old Name", "", "", "")
        cid = self.erp.customers[0].id
        ok, _ = self.erp.update_customer(cid, "New Name", "New Addr", "123", "new@e.com")
        self.assertTrue(ok)
        self.assertEqual(self.erp.customers[0].name, "New Name")

    def test_delete_customer(self):
        self.erp.add_customer("TempCo", "", "", "")
        cid = self.erp.customers[0].id
        ok, _ = self.erp.delete_customer(cid)
        self.assertTrue(ok)
        self.assertEqual(len(self.erp.customers), 0)

    def test_get_customer_by_id(self):
        self.erp.add_customer("FindMe", "", "", "")
        cid = self.erp.customers[0].id
        c = self.erp.get_customer_by_id(cid)
        self.assertIsNotNone(c)
        self.assertEqual(c.name, "FindMe")

    def test_get_nonexistent_customer(self):
        c = self.erp.get_customer_by_id("does-not-exist")
        self.assertIsNone(c)


class TestProducts(unittest.TestCase):

    def setUp(self):
        self.erp = make_erp()

    def tearDown(self):
        try:
            os.remove(self.erp.storage.filepath)
        except FileNotFoundError:
            pass

    def test_add_product(self):
        ok, _ = self.erp.add_product("Lettuce", 3.00, 1.50, 100)
        self.assertTrue(ok)
        self.assertEqual(len(self.erp.products), 1)

    def test_product_margin(self):
        self.erp.add_product("Herb Mix", 10.00, 6.00, 50)
        p = self.erp.products[0]
        self.assertAlmostEqual(p.margin_eur, 4.00)
        self.assertAlmostEqual(p.margin_percent, 40.0)

    def test_add_product_negative_price(self):
        ok, _ = self.erp.add_product("Bad", -1.0, 0.5, 10)
        self.assertFalse(ok)

    def test_update_product(self):
        self.erp.add_product("Spinach", 2.00, 0.80, 200)
        pid = self.erp.products[0].id
        ok, _ = self.erp.update_product(pid, "Baby Spinach", 2.50, 0.90, 250)
        self.assertTrue(ok)
        self.assertEqual(self.erp.products[0].name, "Baby Spinach")
        self.assertAlmostEqual(self.erp.products[0].sales_price, 2.50)

    def test_delete_product(self):
        self.erp.add_product("TempPlant", 1.0, 0.5, 10)
        pid = self.erp.products[0].id
        ok, _ = self.erp.delete_product(pid)
        self.assertTrue(ok)
        self.assertEqual(len(self.erp.products), 0)


class TestOrders(unittest.TestCase):

    def setUp(self):
        self.erp = make_erp()
        self.erp.add_customer("GreenGrocer", "1 Farm Rd", "555-0200", "gg@example.com")
        self.erp.add_product("Kale", 5.00, 2.00, 500)
        self.erp.add_product("Basil", 8.00, 3.00, 200)
        self.cid = self.erp.customers[0].id
        self.pid_kale = self.erp.products[0].id
        self.pid_basil = self.erp.products[1].id

    def tearDown(self):
        try:
            os.remove(self.erp.storage.filepath)
        except FileNotFoundError:
            pass

    def test_create_order(self):
        ok, msg = self.erp.create_order(
            self.cid, "admin",
            [(self.pid_kale, 10), (self.pid_basil, 5)]
        )
        self.assertTrue(ok)
        self.assertEqual(len(self.erp.orders), 1)

    def test_order_totals(self):
        self.erp.create_order(self.cid, "admin", [(self.pid_kale, 4)])
        o = self.erp.orders[0]
        # kale: 5.00 × 4 = 20.00 total; margin = (5-2) × 4 = 12.00
        self.assertAlmostEqual(o.total_price, 20.00)
        self.assertAlmostEqual(o.total_margin, 12.00)
        self.assertAlmostEqual(o.total_cost, 8.00)

    def test_order_line_margin_percent(self):
        self.erp.create_order(self.cid, "admin", [(self.pid_basil, 1)])
        line = self.erp.orders[0].lines[0]
        # basil: (8-3)/8 * 100 = 62.5%
        self.assertAlmostEqual(line.margin_percent, 62.5)

    def test_create_order_no_lines(self):
        ok, _ = self.erp.create_order(self.cid, "admin", [])
        self.assertFalse(ok)

    def test_create_order_invalid_customer(self):
        ok, _ = self.erp.create_order("bad-id", "admin", [(self.pid_kale, 1)])
        self.assertFalse(ok)

    def test_update_order(self):
        self.erp.create_order(self.cid, "admin", [(self.pid_kale, 2)])
        oid = self.erp.orders[0].id
        ok, _ = self.erp.update_order(oid, self.cid, [(self.pid_basil, 3)], status="quotation")
        self.assertTrue(ok)
        o = self.erp.orders[0]
        self.assertEqual(o.status, "quotation")
        self.assertEqual(o.lines[0].product_name, "Basil")
        self.assertAlmostEqual(o.total_price, 24.00)

    def test_delete_order(self):
        self.erp.create_order(self.cid, "admin", [(self.pid_kale, 1)])
        oid = self.erp.orders[0].id
        ok, _ = self.erp.delete_order(oid)
        self.assertTrue(ok)
        self.assertEqual(len(self.erp.orders), 0)

    def test_stock_deducted_on_order_create(self):
        kale = self.erp.get_product_by_id(self.pid_kale)
        initial_qty = kale.quantity
        self.erp.create_order(self.cid, "admin", [(self.pid_kale, 10)])
        self.assertEqual(kale.quantity, initial_qty - 10)

    def test_stock_restored_on_order_delete(self):
        kale = self.erp.get_product_by_id(self.pid_kale)
        initial_qty = kale.quantity
        self.erp.create_order(self.cid, "admin", [(self.pid_kale, 10)])
        oid = self.erp.orders[0].id
        self.erp.delete_order(oid)
        self.assertEqual(kale.quantity, initial_qty)

    def test_create_order_exceeds_stock(self):
        kale = self.erp.get_product_by_id(self.pid_kale)
        ok, msg = self.erp.create_order(self.cid, "admin", [(self.pid_kale, kale.quantity + 1)])
        self.assertFalse(ok)
        self.assertIn("stock", msg.lower())

    def test_order_number_increments(self):
        self.erp.create_order(self.cid, "admin", [(self.pid_kale, 1)])
        self.erp.create_order(self.cid, "admin", [(self.pid_basil, 1)])
        nums = [o.order_number for o in self.erp.orders]
        self.assertEqual(nums[1], nums[0] + 1)


class TestFarmSimulation(unittest.TestCase):

    def setUp(self):
        from models import FarmConfig
        self.farm = FarmConfig(
            length=10.0,
            width=5.0,
            height=3.0,
            floors=3,
            efficiency=0.75,
            electricity_rate=0.25,
            water_rate=0.003,
            kwh_per_sqm_per_day=0.3,
            liters_per_sqm_per_day=3.0,
            seed_cost_per_sqm=1.0,
            yield_kg_per_sqm=3.0,
            price_per_kg=8.0,
            cycle_days=30,
        )

    def test_growing_area(self):
        # 10 × 5 × 3 × 0.75 = 112.5 m²
        self.assertAlmostEqual(self.farm.growing_area, 112.5)

    def test_simulation_keys(self):
        result = self.farm.simulate(30)
        for key in ("electricity_cost", "water_cost", "seed_cost", "revenue", "profit", "yield_kg"):
            self.assertIn(key, result)

    def test_simulation_electricity_math(self):
        result = self.farm.simulate(365)
        expected_kwh = 112.5 * 0.3 * 365
        self.assertAlmostEqual(result["electricity_kwh"], expected_kwh, places=1)
        self.assertAlmostEqual(result["electricity_cost"], expected_kwh * 0.25, places=1)

    def test_simulation_profitability(self):
        # With these params, the farm should be profitable over a year
        result = self.farm.simulate(365)
        self.assertGreater(result["revenue"], 0)
        self.assertGreater(result["profit"], 0)

    def test_export_customers_csv(self):
        erp = make_erp()
        erp.add_customer("TestCo", "Addr", "000", "t@t.com")
        csv_str = erp.export_customers_csv()
        self.assertIn("TestCo", csv_str)
        self.assertIn("Name", csv_str)
        try:
            os.remove(erp.storage.filepath)
        except FileNotFoundError:
            pass

    def test_export_orders_csv(self):
        erp = make_erp()
        erp.add_customer("OrderCo", "", "", "")
        erp.add_product("Leaf", 4.0, 1.5, 100)
        cid = erp.customers[0].id
        pid = erp.products[0].id
        erp.create_order(cid, "admin", [(pid, 2)])
        csv_str = erp.export_orders_csv()
        self.assertIn("OrderCo", csv_str)
        self.assertIn("Order #", csv_str)
        try:
            os.remove(erp.storage.filepath)
        except FileNotFoundError:
            pass


if __name__ == "__main__":
    unittest.main(verbosity=2)