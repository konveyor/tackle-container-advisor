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



import unittest
from service.sim_applier import sim_applier

class TestApplySIM(unittest.TestCase):

    def test_sim_tech_stack_standardization(self):
        sim = sim_applier()
        tech_stack="cobol    java    javascript:  : , , unix/mainframe, unix/mainframe: unknown , db2    "
        extracted = sim.tech_stack_standardization(tech_stack)
        expected = [['Java', 1.0], ['JavaScript', 1.0], ['DB2', 1.0], ['Linux|Red Hat Enterprise Linux', 0.731887500343426], ['NA_CATEGORY', 0.3]]
        self.assertTrue(extracted == expected)
