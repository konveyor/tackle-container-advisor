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
from entity_standardizer.tfidf import utils
from service.standardization import Standardization
from kg_utils.test_check import Test_check
import numpy as np

class TestApplySIM(unittest.TestCase):

    def test_sim_tech_stack_standardization(self):
        tech_stack="cobol    java    javascript:  : , , unix/mainframe, unix/mainframe: unknown , db2    "
        mentions  = utils.preprocess(tech_stack)
        mention_data = []
        for idx, mention in enumerate(mentions):
            mention_data.append({"mention_id": idx, "mention": mention})
        standardizer = Standardization()
        std_mentions = standardizer.entity_standardizer(mention_data)
        extracted = []
        for mention_data in std_mentions:
            entity_names = mention_data.get("entity_names", [""])
            conf_scores  = mention_data.get("confidence", [0.0])
            extracted.append([entity_names[0], conf_scores[0]])
        expected = [['COBOL', np.float64(1.0)], ['Java|*', np.float64(1.0)], ['JavaScript|*', np.float64(1.0)], ['Unix|*', np.float64(1.0)], ['mainframe', np.float64(1.0)], ['DB2', np.float64(1.0)]]
        # print("Expected",expected)
        # print("extracted", extracted)
        self.assertTrue(Test_check.checkEqual(Test_check,expected,extracted))
