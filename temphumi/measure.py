#!/usr/bin/env python3

"""
This script handles two tasks:
- periodic reading from the temperature and humidity sensor
- writing it to configured subscribers.

One main subscriber is LogWriter. It shares the code with the serving
path.
"""

import argparse
import random
import re
import time
import requests

from temphumi.tseries import seriesstorage


class PrintSubscriber:  # pylint: disable=too-few-public-methods
    """Prints accepted data to console."""

    @staticmethod
    def accept(time_stamp, data):
        """Accepts data by printing it to console."""
        print("{} {}".format(
            time.strftime("%Y-%m-%dT%H:%M:%S",
                          time.localtime(time_stamp)), str(data)))

class LogSubscriber:
    """Writes accepted data to log storage."""
    def __init__(self, logbasename):
        self.name = logbasename
        self.storage = None

    def __enter__(self):
        self.storage = seriesstorage.Storage(self.name)
        return self

    def __exit__(self, rtype, value, traceback):
        self.storage.close()
        self.storage = None
        return False

    def accept(self, time_stamp, data):
        """Accepts given measurement data by storing in in the log
        storage."""
        self.storage.store(time_stamp, data)


class Sleeper:  # pylint: disable=too-few-public-methods
    """Accepts measurements by sleeping as configured."""

    def __init__(self, interval_s):
        self.interval_s = interval_s

    def accept(self, time_stamp, data): # pylint: disable=unused-argument
        """Accepts the measurement; ignores passed data and just sleeps
        as configured during object creation."""
        time.sleep(self.interval_s)


class RandomSensor:  # pylint: disable=too-few-public-methods
    """@returns: (humidity, temperature)"""

    @staticmethod
    def read():
        """@returns random humidity and temperature data."""
        return {'h': random.randrange(0, 100),
                't': random.randrange(-20, 40)}

class PowerSensor:
    """returns (p: current power, e: energy today)"""

    def __init__(self, url, timeout=10):
        self.url = url
        self.timeout = timeout

    @staticmethod
    def extract(body):
        """Extracts current power and energy data from HTML string."""
        try:
            current_p = re.search('webdata_now_p = "([.0-9]+)"',
                                  body).group(1)
        except AttributeError:
            current_p = 0
        try:
            e_today = re.search('webdata_today_e = "([.0-9]+)"',
                                body).group(1)
        except AttributeError:
            e_today = 0
        return float(current_p), float(e_today)

    def read(self):
        """@returns power and total power data"""
        try:
            with requests.get(self.url, timeout=self.timeout) as page:
                current_p, e_today = self.extract(page.text)
                return {'p': current_p, 'e': e_today}
        except requests.exceptions.ConnectionError:
            return {}


class DHTSensor:  # pylint: disable=too-few-public-methods
    """Reads data from Grove digital Humidity & Temperature sensor."""
    def __init__(self, dht_port):
        from seeed_dht import DHT  # pylint: disable=import-outside-toplevel
        self.sensor = DHT('11', dht_port)

    def read(self):
        """@returns temperature and humidity data"""
        humi, temp = self.sensor.read()
        return {'t': temp, 'h': humi}


def loop(sensors, subscribers):
    """The main loop of the measurement program. It reads data from
    the sensor objects, and provides it to subscribers in sequence."""
    while True:
        data = {}
        now = time.time()
        for sensor in sensors:
            data.update(sensor.read())
        for subscriber in subscribers:
            subscriber.accept(now, data)


def measure(interval_s, logfname, dht_port, power_url, debug_log):
    """The main method of the measurement program.  It initializes
     sensor and various methods receiving the data.
    """
    sensors = []
    if debug_log:
        sensors.append(RandomSensor())
    if dht_port != -1:
        # Grove - Temperature&Humidity Sensor connected to port D<port>
        sensors.append(DHTSensor(dht_port))
    if power_url != '':
        sensors.append(PowerSensor(power_url))

    with LogSubscriber(logfname) as loghandler:
        subscribers = [PrintSubscriber(), loghandler, Sleeper(interval_s)]
        try:
            loop(sensors, subscribers)
        except KeyboardInterrupt:
            print("Exiting")

def main():
    """Parse command-line arguments and start measurements."""
    parser = argparse.ArgumentParser()
    parser.add_argument('--interval_s', default=15*60, type=int)
    parser.add_argument('--log', default='measurements.sqlite')
    parser.add_argument('--log_dht', type=int, default=5,
                        help=('Grove H&T sensor port number;'
                              '-1 to disable'))
    parser.add_argument('--log_random', default=False,
                        action='store_true',
                        help='(debug) Save random data to log')
    parser.add_argument('--log_power', type=str,
                        default='http://localhost/',
                        help='URL to log power data from')
    args = parser.parse_args()
    measure(args.interval_s, args.log,
            args.log_dht,
            args.log_power,
            args.log_random)


if __name__ == '__main__':
    main()
