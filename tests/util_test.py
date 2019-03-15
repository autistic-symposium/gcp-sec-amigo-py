#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#   util_test.py
#
#   Test the module util.py
#

import unittest
from amigo.lib import util

# TODO: write success and and failure for relevant methods in util.py,
# following example below. Tracked on SETEC-1513

class TestUtil(unittest.TestCase):

    def setUp(self):
        self.empty_dict = {}
        self.network_dict = {
                "resource": "test-163318",
                "attribute": "networks",
                 "raw_data": {
                    "kind": "compute#network",
                    "description": "Default network for the project",
                    "subnetworks": [
                                     "https://test1",
                                     "https://test2",
                                    ],
                "id": "4960383145466457290",
                "creationTimestamp": "2017-10-25T20:10:29.216-07:00",
                }
            }
        self.network_dict_2 = {
                "resource": "test-177777",
                "attribute": "networks",
                 "raw_data": {
                    "kind": "compute#network",
                    "description": "Default network for the project",
                    "subnetworks": [
                                     "https://test3",
                                     "https://test4",
                                    ],
                "id": "49603831454664572340",
                "creationTimestamp": "2017-11-25T20:10:29.216-07:00",
                }
            }


    def test_get_diff_dicts_empty(self):

        test_not_diff = util.get_diff_dicts(self.network_dict, self.network_dict)
        test_diff_empty_to_empty = util.get_diff_dicts(self.empty_dict, self.empty_dict)

        self.assertEqual(test_not_diff, str(self.empty_dict))
        self.assertEqual(test_diff_empty_to_empty, str(self.empty_dict))


    def test_get_diff_dicts_empty_and_nonempty(self):

        test_diff_empty_to_full = util.get_diff_dicts(self.empty_dict, self.network_dict)
        test_diff_full_to_empty = util.get_diff_dicts(self.network_dict, self.empty_dict)

        self.assertEqual(test_diff_full_to_empty, str(self.empty_dict))
        self.assertEqual(util.jsonfy(test_diff_empty_to_full), self.network_dict)


    def test_get_diff_dicts_nonempty_nonempty(self):

        diff_dict1_to_2 = '{"$update": {"raw_data": {"$update": {"subnetworks": ["https://test3", "https://test4"], "creationTimestamp": "2017-11-25T20:10:29.216-07:00", "id": "49603831454664572340"}}, "resource": "test-177777"}}'
        test_diff_dict1_to_2 = util.get_diff_dicts(self.network_dict, self.network_dict_2)

        self.assertEqual(test_diff_dict1_to_2, diff_dict1_to_2)



if __name__ == "__main__":
    unittest.main()