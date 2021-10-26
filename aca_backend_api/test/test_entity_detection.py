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

class TestEntityDetection(unittest.TestCase):
    def test_compose_app(self):
        entity_detection = EntityDetection()
        app_data = [
            {
            'application_id': 'App ID 0114',
            'application_name': 'App Name 0114',
            'application_description': 'App Desc 0114',
            'component_name': 'Comp 1',
            'operating_system': 'RHEL',
            'programming_languages': 'Java',
            'middleware': 'WebSphere Application Server',
            'database': 'db2 10.0',
            'integration_services_and_additional_softwares': 'Redis',
            'technology_summary': 'angularJs,express.js,jenkins',
            'versioning_tool_type': '1',
            'application_inbound_interfaces': 5,
            'application_outbound_interfaces': 1,
            'devops_maturity_level': 'Moderate',
            'devops_tooling': 'Jenkins, Git, JIRA',
            'test_automation_%': '50%',
            'performance_testing_enabled': 'No'
        }
        ]
        expected = [{'application_id': 'App ID 0114', 'application_name': 'App Name 0114', 'application_description': 'App Desc 0114', 'component_name': 'Comp 1', 'operating_system': 'RHEL', 'programming_languages': 'Java', 'middleware': 'WebSphere Application Server', 'database': 'db2 10.0', 'integration_services_and_additional_softwares': 'Redis', 'technology_summary': 'angularJs,express.js,jenkins', 'versioning_tool_type': '1', 'application_inbound_interfaces': 5, 'application_outbound_interfaces': 1, 'devops_maturity_level': 'Moderate', 'devops_tooling': 'Jenkins, Git, JIRA', 'test_automation_%': '50%', 'performance_testing_enabled': 'No', 'KG Version': '1.0.2', 'Storage': {}, 'App': {'db2 10.0': {'DB2': '10.0'}, 'Redis': {'Redis': ''}, 'jenkins': {'Jenkins': ''}}, 'Plugin': {}, 'Lang': {'Java': {'Java': ''}}, 'Runlib': {}, 'Runtime': {}, 'Lib': {'angularJs': {'JavaScript|AngularJS': ''}, 'express.js': {'JavaScript|Express.js': ''}}, 'VM': {}, 'HW': {}, 'Technology': {}, 'App Server': {'WebSphere Application Server': {'Websphere Application Server (WAS)': ''}}, 'OS': {'RHEL': {'Linux|Red Hat Enterprise Linux': ''}}}]
        app_data = entity_detection.compose_app(app_data)
        self.assertTrue(app_data == expected)
