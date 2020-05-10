"""
Stores time series of functions using sqlite3 as the underlying
storage.
"""

import json
import sqlite3
from typing import Sequence

_SCHEMA = """
CREATE TABLE IF NOT EXISTS {} (
  ts REAL NOT NULL PRIMARY KEY,
  data TEXT NOT NULL);
"""

class TableAlreadyExists(Exception):
    """Table already exists"""


class CannotConnect(Exception):
    """Cannot connect to given database"""


def json_convert(sequence: Sequence):
    """Does on-the-fly sequence conversion, by converting the second
    tuple element via json.loads."""
    for time_stamp, data in sequence:
        yield time_stamp, json.loads(data)


class Storage:
    """Provides write and read access to log data."""

    def __init__(self, logbasename: str):
        self.logbasename = logbasename
        self.table = "series"
        try:
            self.connection = sqlite3.connect(logbasename)
        except sqlite3.OperationalError as exc:
            raise CannotConnect() from exc
        try:
            cursor = self.connection.cursor()
            cursor.execute(_SCHEMA.format(self.table))
        except sqlite3.OperationalError as exc:
            raise TableAlreadyExists() from exc

    def store(self, time_stamp, data: dict):
        """Stores data string at given timestamp."""
        cursor = self.connection.cursor()
        cursor.execute("INSERT INTO series VALUES(?,?)",
                       (time_stamp, json.dumps(data)))
        self.connection.commit()

    def read_set(self, tstart, tend):
        """
        @returns a sequence of datapoints: timestamp,
         and data as a dictionary
        """
        cursor = self.connection.cursor()
        return json_convert(cursor.execute("""
            SELECT ts, data FROM {}
            WHERE ts >= ? and ts <= ? ORDER BY ts ASC
            """.format(self.table), (tstart, tend)))

    def has_before(self, tstamp):
        """Returns true if db has data with stamps before tstamp"""
        cursor = self.connection.cursor()
        cursor.execute("SELECT MIN(ts) FROM {}".format(self.table))
        row_minval = cursor.fetchone()
        return row_minval[0] is not None and row_minval[0] < tstamp

    def has_after(self, tstamp):
        """Returns true if db has data with stamps after tstamp"""
        cursor = self.connection.cursor()
        cursor.execute("SELECT MAX(ts) FROM {}".format(self.table))
        row_maxval = cursor.fetchone()
        return row_maxval[0] is not None and row_maxval[0] > tstamp

    def close(self):
        """Closes the connection. No method should be called on this
         object any more.
         """
        self.connection.close()
        self.connection = None
