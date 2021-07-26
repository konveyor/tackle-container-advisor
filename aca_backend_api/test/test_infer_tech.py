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
from service.infer_tech import InferTech

class TestInferTech(unittest.TestCase):
    def test_infer_missing_tech(self):
        inferTech = InferTech()
        appL = [{'application_id': 'App ID 0114', 'application_name': 'App Name 0114', 'application_description': 'App Desc 0114', 'component_name': 'Comp 1', 'operating_system': 'Linux, Windows', 'programming_languages': '', 'middleware': 'WebSphere App Server', 'database': 'db2 10.0', 'integration_services_and_additional_softwares': 'WinForms', 'technology_summary': 'json, ilog, newtech', 'versioning_tool_type': '1', 'application_inbound_interfaces': 5, 'application_outbound_interfaces': 1, 'devops_maturity_level': 'Moderate', 'devops_tooling': 'Jenkins, Git, JIRA', 'test_automation_%': '50%', 'performance_testing_enabled': 'No', 'HW': {}, 'Runtime': {}, 'Runlib': {'winforms': {'.NET Framework|WinForms': ''}}, 'App': {'db2 10.0': {'DB2': '10.0'}}, 'Lang': {}, 'Storage': {}, 'Plugin': {}, 'OS': {'linux': {'Linux': ''}, 'windows': {'Windows': ''}}, 'App Server': {'websphere app server': {'Websphere Application Server (WAS)': ''}}, 'Lib': {}, 'VM': {}, 'Technology': {'json': {'JSON': ''}}, 'low_medium_confidence': {'ilog': {'IBM ILOG Views': '', 'IBM ILOG CPLEX': '', 'IBM ILOG Jviews': ''}}, 'unknown': ['newtech']}]
        expected =  [{'application_id': 'App ID 0114', 'application_name': 'App Name 0114', 'application_description': 'App Desc 0114', 'component_name': 'Comp 1', 'operating_system': 'Linux, Windows', 'programming_languages': '', 'middleware': 'WebSphere App Server', 'database': 'db2 10.0', 'integration_services_and_additional_softwares': 'WinForms', 'technology_summary': 'json, ilog, newtech', 'versioning_tool_type': '1', 'application_inbound_interfaces': 5, 'application_outbound_interfaces': 1, 'devops_maturity_level': 'Moderate', 'devops_tooling': 'Jenkins, Git, JIRA', 'test_automation_%': '50%', 'performance_testing_enabled': 'No', 'HW': {}, 'Runtime':  {'winforms': {'.NET Framework': ''}}, 'Runlib': {'winforms': {'.NET Framework|WinForms': ''}}, 'App': {'db2 10.0': {'DB2': '10.0'}}, 'Lang': {}, 'Storage': {}, 'Plugin': {}, 'OS': {'linux': {'Linux': ''}, 'windows': {'Windows': ''}}, 'App Server': {'websphere app server': {'Websphere Application Server (WAS)': ''}}, 'Lib': {}, 'VM': {}, 'Technology': {'json': {'JSON': ''}}, 'low_medium_confidence': {'ilog': {'IBM ILOG Views': '', 'IBM ILOG CPLEX': '', 'IBM ILOG Jviews': ''}}, 'unknown': ['newtech'], 'Inferred': {'Lang': [], 'App': [], 'App Server': [], 'Runtime': ['.NET Framework'], 'OS': []}, 'Recommended OS': 'Windows', 'Linux': {'Lang': [], 'App': ['DB2'], 'App Server': ['Websphere Application Server (WAS)'], 'Runtime': []}, 'Windows': {'Lang': [], 'App': [], 'App Server': [], 'Runtime': ['.NET Framework']}, 'RepackageOS': ['Linux', 'Windows']}]
        appL = inferTech.infer_missing_tech(appL)
        self.assertTrue(appL == expected)