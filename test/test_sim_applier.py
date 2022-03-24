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
from entity_standardizer.tfidf import utils
from service.standardizer import entity_standardizer

class TestApplySIM(unittest.TestCase):

    def test_sim_tech_stack_standardization(self):
        tech_stack="cobol    java    javascript:  : , , unix/mainframe, unix/mainframe: unknown , db2    "
        mentions  = utils.preprocess(tech_stack)        
        entities  = entity_standardizer(mentions)
        extracted = []
        for mention in mentions:
            entity_list = entities.get(mention, [])
            extracted.append(entity_list[0])        
        expected = [['COBOL|*', 1.0], ['Java|*', 1.0], ['JavaScript', 1.0], ['Unix|*', 1.0], ['mainframe', 1.0], ['DB2', 1.0]]
        self.assertTrue(extracted == expected)
