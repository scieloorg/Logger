import csv
import requests
import os
import sqlite3
import json
from datetime import datetime
import argparse

import logging
from random import choice


# CREATE_TABLE_INSTRUCTIONS = (
# """
# CREATE TABLE IF NOT EXISTS pids (
#   id SERIAL PRIMARY KEY,
#   v2 varchar(23),
#   v3 varchar(23),
#   upd varchar(8),
#   created_at timestamptz DEFAULT now()
# );

# CREATE INDEX IF NOT EXISTS index_pids_v2 ON pids (v2);
# CREATE INDEX IF NOT EXISTS index_pids_v3 ON pids (v3);
# """
# )

CREATE_TABLE_INSTRUCTIONS = (
"""CREATE TABLE IF NOT EXISTS pids (
  id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
  v2 VARCHAR(23) NOT NULL,
  v3 VARCHAR(23) NOT NULL,
  j_acron VARCHAR(23) NOT NULL,
  upd VARCHAR(8) NOT NULL,
  created_at timestamptz default current_timestamp
);
""",

"CREATE INDEX IF NOT EXISTS idx_v2 ON pids (v2);",

"CREATE INDEX IF NOT EXISTS idx_v3 ON pids (v3);"
)

logger = logging.getLogger(__name__)


def _config_logging(logging_level='INFO', logging_file=None):

    allowed_levels = {
        'DEBUG': logging.DEBUG,
        'INFO': logging.INFO,
        'WARNING': logging.WARNING,
        'ERROR': logging.ERROR,
        'CRITICAL': logging.CRITICAL
    }

    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    logger.setLevel(allowed_levels.get(logging_level, 'INFO'))

    if logging_file:
        hl = logging.FileHandler(logging_file, mode='a')
    else:
        hl = logging.StreamHandler()

    hl.setFormatter(formatter)
    hl.setLevel(allowed_levels.get(logging_level, 'INFO'))

    logger.addHandler(hl)


def fix_date_format(date_from_api):
    # 'Tue, 24 Aug 2021 19:22:04 GMT' to '20210824'
    parts = date_from_api.split(" ")
    try:
        if len(parts) == 6:
            dt = datetime.strptime(date_from_api, '%a, %d %b %Y %H:%M:%S %Z')
        elif len(parts) == 5:
            dt = datetime.strptime(date_from_api, '%a, %d %b %Y %H:%M:%S')
    except Exception as e:
        logger.debug(e)
    else:
        return dt.strftime('%Y%m%d')


class PidManagerDB:
    def __init__(self, db_path):
        if not db_path:
            raise ValueError(
                "PidManagerDB requires db location")
        self._db_path = db_path
        self._cursor = None
        self._con = None
        self._create_table()

    def connect(self):
        logger.debug(">>> Connect")
        self._con = sqlite3.connect(self._db_path)
        self._cursor = self._con.cursor()

    def _create_table(self):
        logger.debug(">>> _create_table")
        # Create table
        for instruction in CREATE_TABLE_INSTRUCTIONS:
            logger.debug(instruction)
            self.cursor.execute(instruction)
        self.commit()
        self.close()

    def _create_table_from_csv(self, file_path):
        logger.debug(">>> _create_table_from_csv")
        rows = []
        with open(file_path, newline='') as fp:
            for row in csv.reader(fp):
                rows.append(row)
                if len(rows) == 50:
                    self.insert_multiple_rows(rows)
                    rows = []
            if rows:
                self.insert_multiple_rows(rows)

    def _create_table_from_json(self, file_path):
        logger.debug(">>> _create_table_from_json")
        rows = []
        d = json.load(open(file_path, "r"))
        for v3, data in d.items():
            row = (
                data["pid_v2"], v3, data["journal_acronym"],
                fix_date_format(data["update"]))
            rows.append(row)
            if len(rows) == 50:
                self.insert_multiple_rows(rows)
                rows = []
        if rows:
            self.insert_multiple_rows(rows)

    @property
    def cursor(self):
        # logger.debug(">>> cursor")
        if not self._cursor:
            if self._con:
                self._cursor = self._con.cursor()
            else:
                self.connect()
        return self._cursor

    def commit(self):
        logger.debug(">>> commit")
        # Save (commit) the changes
        self._con.commit()

    def close(self):
        # We can also close the connection if we are done with it.
        # Just be sure any changes have been committed or they will be lost.
        logger.debug(">>> close")
        self._con.close()
        self._con = None
        self._cursor = None

    def _format_values_to_insert(self, v2, v3, j_acron, update):
        return "('%s', '%s', '%s', '%s')" % (v2, v3, j_acron, update)

    def _multiple_insert_command(self, v2_and_v3_items):
        values = ", ".join([
            self._format_values_to_insert(v2, v3, j_acron, update)
            for v2, v3, j_acron, update in v2_and_v3_items
        ])
        return "INSERT INTO pids (v2, v3, j_acron, upd) VALUES %s;" % values

    def insert_multiple_rows(self, rows):
        # Insert a row of data
        r = self.cursor.execute(self._multiple_insert_command(rows))
        self.commit()
        return r

    def insert(self, v2, v3, j_acron, update):
        # Insert a row of data
        r = self.cursor.execute(
            "SELECT * FROM pids WHERE v2='%s' and v3='%s' and j_acron='%s' and upd='%s'" %
            (v2, v3, j_acron, update)
        )
        logger.debug((v2, v3, j_acron, update))
        for i in r:
            logger.debug("Found it. Not inserted again")
            return

        logger.debug("Not found. Insert it")
        return self.insert_multiple_rows([(v2, v3, j_acron, update)])

    def pid_v3_to_pid_v2(self, v3):
        for row in self.cursor.execute(
                "SELECT * FROM pids WHERE v3 = '%s' ORDER BY upd DESC" % v3):
            logger.debug(row)
            return row[1]


class PidManagerAPI:

    def __init__(self, url=None):
        self._url = url

    def _get_response(self, v3):
        if not self._url:
            return
        try:
            response = requests.get("%s/%s" % (self._url, v3), timeout=10)
        except requests.HTTPError:
            return None
        else:
            return response.text

    def pid_v3_to_pid_v2(self, v3):
        resp = self._get_response(v3)
        try:
            return json.loads(resp)
        except:
            return None


class PidManager:

    def __init__(self, pid_manager_db, pid_manager_api, max_items_in_mem=None):
        self._db = pid_manager_db
        self._api = pid_manager_api

        # evita exceder uso de memoria / limita numero de itens no dict
        self._max_items_in_mem = int(max_items_in_mem or 5000)
        self._pid_v3_to_pid_v2 = {}

    def _pid_v3_to_pid_v2_from_api(self, v3):
        if self._api:
            return self._api.pid_v3_to_pid_v2(v3)

    def _pid_v3_to_pid_v2_from_db(self, v3):
        if self._db:
            return self._db.pid_v3_to_pid_v2(v3)

    def pid_v3_to_pid_v2(self, v3):
        v2 = self._pid_v3_to_pid_v2.get(v3)
        logger.debug(len(self._pid_v3_to_pid_v2))
        if v2:
            return v2

        v2 = self._pid_v3_to_pid_v2_from_db(v3)
        if not v2:
            data = self._pid_v3_to_pid_v2_from_api(v3)
            if data:
                try:
                    v2 = data["v2"]
                    self._db.insert(v2, v3, data["j_acron"], data["update"])
                except KeyError:
                    pass
        self._db.close()
        logger.debug(len(self._pid_v3_to_pid_v2))
        if v2:
            self.add(v2, v3)
            return v2

    def add(self, v2, v3):
        self._pid_v3_to_pid_v2[v3] = v2
        if len(self._pid_v3_to_pid_v2) > self._max_items_in_mem:
            # evita exceder uso de memoria / limita numero de itens no dict
            random_index = choice(range(self._max_items_in_mem))
            random_key = self._pid_v3_to_pid_v2.keys()[random_index]
            self._pid_v3_to_pid_v2.pop(random_key)
            logger.debug("%s %s" % (random_index, random_key))


def main():

    parser = argparse.ArgumentParser(
        description="PidManager"
    )

    subparsers = parser.add_subparsers(
        title="Commands", metavar="", dest="command")

    populate_db_parser = subparsers.add_parser(
        "populate_db",
        help=(
            "Populate database with v2, v3, j_acron. "
        )
    )
    populate_db_parser.add_argument(
        '--source',
        '-s',
        required=True,
        help='Full path to the directory with pids'
    )

    populate_db_parser.add_argument(
        '--destination',
        '-d',
        required=True,
        help='Full path to the directory with pids'
    )

    populate_db_parser.add_argument(
        '--logging_file',
        '-o',
        help='Full path to the log file'
    )

    populate_db_parser.add_argument(
        '--logging_level',
        '-l',
        default='DEBUG',
        choices=['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'],
        help='Logggin level'
    )

    ###
    pid_v3_to_pid_v2_parser = subparsers.add_parser(
        "pid_v3_to_pid_v2",
        help=(
            "Get v2 by v3"
        )
    )
    pid_v3_to_pid_v2_parser.add_argument(
        '--source',
        '-s',
        required=True,
        help='Full path to the db'
    )
    pid_v3_to_pid_v2_parser.add_argument(
        '--v3',
        required=True,
        help='v3'
    )

    pid_v3_to_pid_v2_parser.add_argument(
        '--max_items_in_mem',
        required=True,
        type=int,
        help='max_items_in_mem'
    )

    pid_v3_to_pid_v2_parser.add_argument(
        '--logging_file',
        '-o',
        help='Full path to the log file'
    )

    pid_v3_to_pid_v2_parser.add_argument(
        '--logging_level',
        '-l',
        default='DEBUG',
        choices=['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'],
        help='Logggin level'
    )

    ###
    insert_parser = subparsers.add_parser(
        "insert",
        help=(
            "insert v2 v3 j_acron"
        )
    )
    insert_parser.add_argument(
        '--source',
        '-s',
        required=True,
        help='Full path to the db'
    )
    insert_parser.add_argument(
        '--v2',
        required=True,
        help='v2'
    )
    insert_parser.add_argument(
        '--v3',
        required=True,
        help='v3'
    )
    insert_parser.add_argument(
        '--j_acron',
        required=True,
        help='j_acron'
    )
    insert_parser.add_argument(
        '--update',
        required=True,
        help='update'
    )

    insert_parser.add_argument(
        '--logging_file',
        '-o',
        help='Full path to the log file'
    )

    insert_parser.add_argument(
        '--logging_level',
        '-l',
        default='DEBUG',
        choices=['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'],
        help='Logggin level'
    )

    args = parser.parse_args()
    pid_manager_api = PidManagerAPI()

    _config_logging(args.logging_level, args.logging_file)

    if args.command == "populate_db":
        pid_manager_db = PidManagerDB(args.destination)
        pid_manager_db._create_table_from_json(args.source)

    elif args.command == "pid_v3_to_pid_v2":
        pid_manager_db = PidManagerDB(args.source)
        pid_manager = PidManager(
            pid_manager_db, pid_manager_api, args.max_items_in_mem)

        items = args.v3.split(" ")
        for item in items:
            result = pid_manager.pid_v3_to_pid_v2(item)
            logger.debug(result)

    elif args.command == "insert":
        pid_manager_db = PidManagerDB(args.source)
        result = pid_manager_db.insert(
            args.v2, args.v3, args.j_acron, args.update)
        logger.debug(result)


if __name__ == "__main__":
    main()
