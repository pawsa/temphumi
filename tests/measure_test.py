#! /usr/bin/env python3
"""Tests measurement process. Small part of it is the actual
measurement. The large part is logging."""

import unittest

from temphumi import measure

class TestLogSubscriber(unittest.TestCase):
    """Tests if subscribing to the measurement process works as
    expected, and that the log files are divided appropriately."""
    def setUp(self):
        self.name = ':memory:'

    def test_insertion(self):
        """Test insertion."""
        with measure.LogSubscriber(self.name) as subscriber:
            subscriber.accept(1.0, {'t': 20, 'h': 20})
            subscriber.accept(2.0, {'t': 21, 'h': 20})
            subscriber.accept(3.0, {'t': 22, 'h': 20})

class TestPower(unittest.TestCase):
    """Test the power sensor."""
    def setUp(self):
        self.sensor = measure.PowerSensor('')

    def test_extraction(self):
        """Test if the data can be extracted from the status page."""
        body = """
        var webdata_now_p = "12.34";
        var webdata_today_e = "56.78";
        """
        p_now, e_today = self.sensor.extract(body)
        self.assertEqual(p_now, 12.34)
        self.assertEqual(e_today, 56.78)


if __name__ == "__main__":
    unittest.main()
