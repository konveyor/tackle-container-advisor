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
from service.entity_detection import EntityDetection
from deepdiff import DeepDiff

class TestEntityDetection(unittest.TestCase):
    def test_compose_app(self):
        entity_detection = EntityDetection()
        app_data = [
            {
            'application_id': 'App ID 0114',
            'application_name': 'App Name 0114',
            'application_description': 'App Desc 0114',
            'component_name': 'Comp 1',
            'operating_system': 'Oracle Linux 4.5',
            'programming_languages': 'PHP',
            'middleware': 'Oracle WebLogic Server 14c',
            'database': 'PostgreSQL',
            'integration_services_and_additional_softwares': 'Redis',
            'technology_summary': 'HTTP Client',
            'versioning_tool_type': '1',
            'application_inbound_interfaces': 5,
            'application_outbound_interfaces': 1,
            'devops_maturity_level': 'Moderate',
            'devops_tooling': 'Jenkins, Git, JIRA',
            'test_automation_%': '50%',
            'performance_testing_enabled': 'No'
        }
        ]
        expected = [{'application_id': 'App ID 0114', 'application_name': 'App Name 0114', 'application_description': 'App Desc 0114', 'component_name': 'Comp 1', 'operating_system': 'Oracle Linux 4.5', 'programming_languages': 'PHP', 'middleware': 'Oracle WebLogic Server 14c', 'database': 'PostgreSQL', 'integration_services_and_additional_softwares': 'Redis', 'technology_summary': 'HTTP Client', 'versioning_tool_type': '1', 'application_inbound_interfaces': 5, 'application_outbound_interfaces': 1, 'devops_maturity_level': 'Moderate', 'devops_tooling': 'Jenkins, Git, JIRA', 'test_automation_%': '50%', 'performance_testing_enabled': 'No', 'KG Version': '1.0.3', 'Plugin': {}, 'Storage': {}, 'Lib': {}, 'Runtime': {}, 'App': {'PostgreSQL': {'PostgreSQL': ('NA_VERSION', '14')}, 'Redis': {'Redis': ('NA_VERSION', '6.2.4')}}, 'VM': {}, 'Technology': {'HTTP Client': {'HTTP client': ('NA_VERSION', 'NA_VERSION')}}, 'App Server': {'Oracle WebLogic Server 14c': {'Oracle WebLogic Server': ('14c', '14c')}}, 'OS': {'Oracle Linux 4.5': {'Linux': ('4.5', '4.5')}}, 'Runlib': {}, 'Lang': {'PHP': {'PHP': ('NA_VERSION', '8')}}, 'HW': {}}]
        app_data = entity_detection.compose_app(app_data)
        # print("App data = ", app_data)
        # print("Expected = ", expected)
        if app_data != expected:
            diff = DeepDiff(expected, app_data)
            print("Test app diff = ", diff) 
        else:
            print("Test app passed")            
        self.assertTrue(app_data == expected)

    def test_compose_app1(self):
        entity_detection = EntityDetection()
        app_data = [
            {
            'application_id': 'App ID 0115',
            'application_name': 'App Name 0115',
            'application_description': 'App Desc 0115',
            'component_name': 'Comp 2',
            'operating_system': 'Linux|Amazon Linux 2013.09.1',
            'programming_languages': 'Java 1.2',
            'middleware': 'Oracle WebLogic Server 14c',
            'database': 'Sybase SQL Server 4.9',
            'integration_services_and_additional_softwares': 'Splunk 6',
            'technology_summary': 'Nexus Repository OSS 3.22.0',
            'versioning_tool_type': '1',
            'application_inbound_interfaces': 5,
            'application_outbound_interfaces': 1,
            'devops_maturity_level': 'Moderate',
            'devops_tooling': 'Jenkins, Git, JIRA',
            'test_automation_%': '50%',
            'performance_testing_enabled': 'No'
        }
        ]
        expected = [{'application_id': 'App ID 0115', 'application_name': 'App Name 0115', 'application_description': 'App Desc 0115', 'component_name': 'Comp 2', 'operating_system': 'Linux|Amazon Linux 2013.09.1', 'programming_languages': 'Java 1.2', 'middleware': 'Oracle WebLogic Server 14c', 'database': 'Sybase SQL Server 4.9', 'integration_services_and_additional_softwares': 'Splunk 6', 'technology_summary': 'Nexus Repository OSS 3.22.0', 'versioning_tool_type': '1', 'application_inbound_interfaces': 5, 'application_outbound_interfaces': 1, 'devops_maturity_level': 'Moderate', 'devops_tooling': 'Jenkins, Git, JIRA', 'test_automation_%': '50%', 'performance_testing_enabled': 'No', 'KG Version': '1.0.3', 'Storage': {}, 'Runtime': {}, 'VM': {}, 'Plugin': {}, 'Technology': {}, 'App': {'Sybase SQL Server 4.9': {'Sybase SQL Server': ('4.9', '4.9.2')}, 'Splunk 6': {'Splunk': ('6', '6.6')}, 'Nexus Repository OSS 3.22.0': {'Nexus Repository OSS': ('3.22.0', '3.29.1')}}, 'HW': {}, 'Lib': {}, 'App Server': {'Oracle WebLogic Server 14c': {'Oracle WebLogic Server': ('14c', '14c')}}, 'Runlib': {}, 'Lang': {'Java 1.2': {'Java': ('1.2', '1.4')}}, 'OS': {'Linux|Amazon Linux 2013.09.1': {'Linux|Amazon Linux': ('2013.09.1', '2013.09.2')}}}]
        app_data = entity_detection.compose_app(app_data)
        if app_data != expected:
            diff = DeepDiff(expected, app_data)
            print("Test app1 Diff = ", diff) 
        else:
            print("Test app1 passed")

        self.assertTrue(app_data == expected)

    def test_compose_app2(self):
        entity_detection = EntityDetection()
        app_data = [
            {
            'application_id': 'App ID 0116',
            'application_name': 'App Name 0116',
            'application_description': 'App Desc 0116',
            'component_name': 'Comp 4',
            'operating_system': 'RHEL 8.1',
            'programming_languages': 'python 3.9.6',
            'middleware': 'JBoss 4.0.1',
            'database': 'Oracle SQl Developer 19.2',
            'integration_services_and_additional_softwares': 'PeopleSoft 7',
            'technology_summary': 'HTTP Client 4.5.6',
            'versioning_tool_type': '1',
            'application_inbound_interfaces': 5,
            'application_outbound_interfaces': 1,
            'devops_maturity_level': 'Moderate',
            'devops_tooling': 'Jenkins, Git, JIRA',
            'test_automation_%': '50%',
            'performance_testing_enabled': 'No'
        }
        ]
        expected = [{'application_id': 'App ID 0116', 'application_name': 'App Name 0116', 'application_description': 'App Desc 0116', 'component_name': 'Comp 4', 'operating_system': 'RHEL 8.1', 'programming_languages': 'python 3.9.6', 'middleware': 'JBoss 4.0.1', 'database': 'Oracle SQl Developer 19.2', 'integration_services_and_additional_softwares': 'PeopleSoft 7', 'technology_summary': 'HTTP Client 4.5.6', 'versioning_tool_type': '1', 'application_inbound_interfaces': 5, 'application_outbound_interfaces': 1, 'devops_maturity_level': 'Moderate', 'devops_tooling': 'Jenkins, Git, JIRA', 'test_automation_%': '50%', 'performance_testing_enabled': 'No', 'KG Version': '1.0.3', 'App': {'Oracle SQl Developer 19.2': {'Oracle SQL Developer': ('19.2', '19.4')}, 'PeopleSoft 7': {'PeopleSoft': ('7', '7.5')}}, 'Runlib': {}, 'Lib': {}, 'HW': {}, 'App Server': {'JBoss 4.0.1': {'JBoss': ('4.0.1', '4.2.3')}}, 'Lang': {'python 3.9.6': {'Python': ('3.9.6', '3.10.0')}}, 'OS': {'RHEL 8.1': {'Linux|Red Hat Enterprise Linux': ('8.1', '8.3')}}, 'Runtime': {}, 'VM': {}, 'Technology': {'HTTP Client 4.5.6': {'HTTP client': ('4.5.6', '4.5.6')}}, 'Storage': {}, 'Plugin': {}, 'low_medium_confidence': {'HTTP Client 4.5.6': {'MQ Client': ('4.5.6', '4.5.6'), 'IBM Tivoli Storage Manager|TSM Client': ('4.5.6', '4.5.6')}}}]
        app_data = entity_detection.compose_app(app_data)
        if app_data != expected:
            diff = DeepDiff(expected, app_data)
            print("Test app2 Diff = ", diff) 
        else:
            print("Test app2 passed")
        self.assertTrue(app_data == expected)
