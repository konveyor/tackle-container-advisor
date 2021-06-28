# *****************************************************************
# Copyright IBM Corporation 2021
# Licensed under the Eclipse Public License 2.0, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# *****************************************************************


import sys
sys.path.append("./")

import unittest
from service.utils import Utils

class TestUtils(unittest.TestCase):


    def test_preprocess_tech_stack(self):
        tech_stack = Utils.preprocess_tech_stack_for_sim('Tivoli Access Manager\u00a0(TAM), DB2_[WAS] Tivoli')
        print(tech_stack)
        tech_stack_List = tech_stack.split()
        tech_stack_List.sort()
        tech_stack = ' '.join(tech_stack_List)
        expectedList = 'Tivoli Access Manager (TAM), DB2_[WAS] Tivoli'.split()
        expectedList.sort()
        expected = ' '.join(expectedList)
        self.assertEqual(tech_stack, expected)
