#!/usr/bin/env python

# wikiware - a python wiki system
# Copyright (C) 2016-2017 izrik
#
# This file is a part of wikiware.
#
# Wikiware is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Wikiware is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with wikiware.  If not, see <http://www.gnu.org/licenses/>.


import argparse
from os import environ
import MySQLdb


class Config(object):
    PASSWORD = environ.get('PASSWORD')


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('host', type=str, action='store')
    parser.add_argument('user', type=str, action='store')
    parser.add_argument('--password', type=str, action='store',
                        default=Config.PASSWORD)
    parser.add_argument('db', type=str, action='store')
    parser.add_argument('--ssl-cert', type=str, action='store')
    parser.add_argument('--ssl-key', type=str, action='store')

    args = parser.parse_args()

    Config.PASSWORD = args.password


def run():
    print('DB URI: {}'.format(Config.DB_URI))
    conn = MySQLdb.connect(
        host=args.host,
        user=args.user,
        passwd=Config.PASSWORD,
        db=args.db,
    )


if __name__ == "__main__":
    run()
