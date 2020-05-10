"""Tests tseries"""

import unittest

import temphumi
from temphumi.tseries import tseries


class TestTseries(unittest.TestCase):
    """Test reading series"""

    def setUp(self):
        self.app = temphumi.create_app({'DATABASE': ':memory:'})
        self.client = self.app.test_client()

    def test_main_page(self):
        """Tests that main page can be served"""
        with self.app.app_context():
            with self.client.get('/') as read_page:
                self.assertEqual(read_page.status_code, 200)
                self.assertEqual(read_page.status, '200 OK')

    def test_measurements(self):
        """Test if the data can be read as expected from the mock."""
        with self.app.app_context():
            tseries.get_storage().store(1, {'t': 1, 'h': 2})
            tseries.get_storage().store(2, {'t': 2, 'h': 2})
            with self.client.get('/measurements/1,200') as read_json:
                self.assertEqual(read_json.status_code, 200)
                read_data = read_json.json
                self.assertFalse(read_data.get('has_after'))
                self.assertFalse(read_data.get('has_before'))
                self.assertEqual(len(read_data.get('data')), 2)
                self.assertIn('dt', read_data.get('data')[0])


if __name__ == "__main__":
    unittest.main()
