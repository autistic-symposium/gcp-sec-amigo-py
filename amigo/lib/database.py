#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#   database.py
#
#   Class for Amigo's database. This class wraps
#   the methods from TinyDB and make it easier for
#   changing the intrinsic database in the future
#   if we have issues with scalability.
#

from tinydb import TinyDB, Query


class Database():

    def __init__(self, db_json_file):

        self.database = TinyDB(db_json_file)


    def get_table(self, table):
        """
            Return the items from a given table in the database.
        """
        return self.database.table(table).all()


    def get_database(self):
        """
            Return the entire database as a dictionary.
        """
        return self.database.all()


    def insert(self, table, item):
        """
            Insert an item in a given table.
        """
        self.database.table(table).insert(item)
