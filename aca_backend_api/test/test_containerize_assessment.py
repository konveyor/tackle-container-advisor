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
from collections import OrderedDict
from service.containerize_assessment import Assessment


class TestAssessment(unittest.TestCase):

    def test_app_validation(self):
        assessment = Assessment()
        appL = [{'application_id': 'App ID 0114', 'application_name': 'App Name 0114', 'application_description': 'App Desc 0114', 'component_name': 'Comp 1', 'operating_system': 'RHEL', 'programming_languages': 'Java', 'middleware': 'WebSphere Application Server', 'database': 'db2 10.0', 'integration_services_and_additional_softwares': 'Redis', 'technology_summary':'angularJs,express.js,jenkins', 'versioning_tool_type': '1', 'application_inbound_interfaces': 5, 'application_outbound_interfaces': 1, 'devops_maturity_level': 'Moderate', 'devops_tooling': 'Jenkins, Git, JIRA', 'test_automation_%': '50%', 'performance_testing_enabled': 'No', 'KG Version': '1.0.0', 'App Server': {'WebSphere Application Server': {'Websphere Application Server (WAS)': ''}}, 'Runtime': {}, 'Lang': {'Java': {'Java': ''}}, 'App': {'db2 10.0': {'DB2': '10.0'}, 'Redis': {'Redis': ''}, 'jenkins': {'Jenkins': ''}},'OS': {'RHEL': {'Linux|Red Hat Enterprise Linux': ''}}, 'Lib': {'angularJs': {'JavaScript|AngularJS': ''}, 'express.js': {'JavaScript|Express.js': ''}}}]
        expected = [{'application_id': 'App ID 0114', 'application_name': 'App Name 0114', 'application_description': 'App Desc 0114', 'component_name': 'Comp 1', 'operating_system': 'RHEL', 'programming_languages': 'Java', 'middleware': 'WebSphere Application Server', 'database': 'db2 10.0', 'integration_services_and_additional_softwares': 'Redis', 'technology_summary':'angularJs,express.js,jenkins', 'versioning_tool_type': '1', 'application_inbound_interfaces': 5, 'application_outbound_interfaces': 1, 'devops_maturity_level': 'Moderate', 'devops_tooling': 'Jenkins, Git, JIRA', 'test_automation_%': '50%', 'performance_testing_enabled': 'No', 'KG Version': '1.0.0', 'App Server': {'WebSphere Application Server': {'Websphere Application Server (WAS)': ''}}, 'Runtime': {}, 'Lang': {'Java': {'Java': ''}}, 'App': {'db2 10.0': {'DB2': '10.0'}, 'Redis': {'Redis': ''}, 'jenkins': {'Jenkins': ''}},'OS': {'RHEL': {'Linux|Red Hat Enterprise Linux': ''}}, 'Lib': {'angularJs': {'JavaScript|AngularJS': ''}, 'express.js': {'JavaScript|Express.js': ''}}, 'assessment_reason': ''}]

        appL = assessment.app_validation(appL)
        self.assertTrue(appL == expected)


    def test_output_assessment(self):
        assessment = Assessment()
        appL = [{'application_id': 'App ID 0114', 'application_name': 'App Name 0114', 'application_description': 'App Desc 0114', 'component_name': 'Comp 1', 'operating_system': 'RHEL', 'programming_languages': 'Java', 'middleware': 'WebSphere Application Server', 'database': 'db2 10.0', 'integration_services_and_additional_softwares': 'Redis', 'technology_summary':'angularJs,express.js,jenkins', 'versioning_tool_type': '1', 'application_inbound_interfaces': 5, 'application_outbound_interfaces': 1, 'devops_maturity_level': 'Moderate', 'devops_tooling': 'Jenkins, Git, JIRA', 'test_automation_%': '50%', 'performance_testing_enabled': 'No', 'KG Version': '1.0.0', 'App Server': {'WebSphere Application Server': {'Websphere Application Server (WAS)': ''}}, 'Runtime': {}, 'Lang': {'Java': {'Java': ''}}, 'App': {'db2 10.0': {'DB2': '10.0'}, 'Redis': {'Redis': ''}, 'jenkins': {'Jenkins': ''}},'OS': {'RHEL': {'Linux|Red Hat Enterprise Linux': ''}}, 'Lib': {'angularJs': {'JavaScript|AngularJS': ''}, 'express.js': {'JavaScript|Express.js': ''}}, 'assessment_reason': ''}]

        expected = {
            'Name': 'App Name 0114',
            'Desc': 'App Desc 0114',
            'Cmpt': 'Comp 1',
            'OS': {'RHEL': {'Linux|Red Hat Enterprise Linux': ''}},
            'Lang': {'Java': {'Java': ''}},
            'App Server': {'WebSphere Application Server': {'Websphere Application Server (WAS)': ''}},
            'Dependent Apps': {'db2 10.0': {'DB2': '10.0'}, 'Redis': {'Redis': ''}, 'jenkins': {'Jenkins': ''}},
            'Libs': {'angularJs': {'JavaScript|AngularJS': ''}, 'express.js': {'JavaScript|Express.js': ''}},
            'KG Version': '1.0.0',
            'Reason': ''
        }
        expected = OrderedDict(expected)
        expected = [expected]
        pAppL = assessment.output_to_ui_assessment(appL)
        self.assertTrue(pAppL == expected)