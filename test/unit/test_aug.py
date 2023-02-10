################################################################################
# Copyright IBM Corporation 2021, 2022
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
################################################################################

import unittest
import sqlite3
import os
from kg_utils import kg_aug

class TestAug(unittest.TestCase):
    def test_insert_to_kg(self):
        conn = sqlite3.connect("./db/1.0.5.db")
        cur = conn.cursor()
        appL = kg_aug.insert_to_kg("batch", "./test/unit/test.csv", cur, True)
        expected = "Entry 0 inserted to table..Entry 1 cannot be processed.."
        self.assertTrue(appL == expected)
