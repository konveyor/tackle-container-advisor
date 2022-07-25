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
from service.standardization import Standardization
from deepdiff import DeepDiff

class TestEntityDetection(unittest.TestCase):
    def test_compose_app1(self):
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
        expected = [{'application_id': 'App ID 0114', \
                     'application_name': 'App Name 0114', \
                     'application_description': 'App Desc 0114', \
                     'component_name': 'Comp 1', \
                     'operating_system': 'Oracle Linux 4.5', \
                     'programming_languages': 'PHP', \
                     'middleware': 'Oracle WebLogic Server 14c', \
                     'database': 'PostgreSQL', \
                     'integration_services_and_additional_softwares': 'Redis', \
                     'technology_summary': 'HTTP Client', \
                     'versioning_tool_type': '1', \
                     'application_inbound_interfaces': 5, \
                     'application_outbound_interfaces': 1, \
                     'devops_maturity_level': 'Moderate', \
                     'devops_tooling': 'Jenkins, Git, JIRA', \
                     'test_automation_%': '50%', \
                     'performance_testing_enabled': 'No', \
                     'KG Version': '1.0.4', \
                     'Plugin': {}, \
                     'Storage': {}, \
                     'Lib': {}, \
                     'Runtime': {}, \
                     'App': {'PostgreSQL': {'PostgreSQL': ('NA_VERSION', '14')}, \
                             'Redis': {'Redis': ('NA_VERSION', '6.2.4')} \
                             }, \
                     'VM': {}, \
                     'Technology': {'HTTP Client': {'HTTP client': ('NA_VERSION', 'NA_VERSION')}}, \
                     'App Server': {'Oracle WebLogic Server 14c': {'Oracle WebLogic Server': ('14c', '14c')}}, \
                     'OS': {'Oracle Linux 4.5': {'Linux|Oracle Linux': ('4.5', '4.9')}}, \
                     'Runlib': {}, \
                     'Lang': {'PHP': {'PHP': ('NA_VERSION', '8')}}, \
                     'HW': {} \
                     }]
        standardizer = Standardization()
        app_data = standardizer.app_standardizer(app_data)
        if app_data != expected:
            diff = DeepDiff(expected, app_data)
            print("Test app1 diff = ", diff)
        self.assertTrue(app_data == expected)

    def test_compose_app2(self):
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
        expected = [{'application_id': 'App ID 0115', \
                     'application_name': 'App Name 0115', \
                     'application_description': 'App Desc 0115', \
                     'component_name': 'Comp 2', \
                     'operating_system': 'Linux|Amazon Linux 2013.09.1', \
                     'programming_languages': 'Java 1.2', \
                     'middleware': 'Oracle WebLogic Server 14c', \
                     'database': 'Sybase SQL Server 4.9', \
                     'integration_services_and_additional_softwares': 'Splunk 6', \
                     'technology_summary': 'Nexus Repository OSS 3.22.0', \
                     'versioning_tool_type': '1', \
                     'application_inbound_interfaces': 5, \
                     'application_outbound_interfaces': 1, \
                     'devops_maturity_level': 'Moderate', \
                     'devops_tooling': 'Jenkins, Git, JIRA', \
                     'test_automation_%': '50%', \
                     'performance_testing_enabled': 'No', \
                     'KG Version': '1.0.4', \
                     'Storage': {}, \
                     'Runtime': {}, \
                     'VM': {}, \
                     'Plugin': {}, \
                     'Technology': {}, \
                     'App': {'Sybase SQL Server 4.9': {'Sybase SQL Server|*': ('4.9', '4.9.2')}, \
                             'Splunk 6': {'Splunk': ('6', '6.6')}, \
                             'Nexus Repository OSS 3.22.0': {'Nexus Repository OSS': ('3.22.0', '3.29.1')}, \
                             }, \
                     'HW': {}, \
                     'Lib': {}, \
                     'App Server': {'Oracle WebLogic Server 14c': {'Oracle WebLogic Server|*': ('14c', '14c')}}, \
                     'Runlib': {}, \
                     'Lang': {'Java 1.2': {'Java|*': ('1.2', '1.4')}}, \
                     'OS': {'Linux|Amazon Linux 2013.09.1': {'Linux|Amazon Linux': ('2013.09.1', '2013.09.2')}}
                     }]
        standardizer = Standardization()
        app_data = standardizer.app_standardizer(app_data)
        if app_data != expected:
            diff = DeepDiff(expected, app_data)
            print("Test app2 Diff = ", diff)

        self.assertTrue(app_data == expected)

    def test_compose_app3(self):
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
        expected = [{'application_id': 'App ID 0116', \
                     'application_name': 'App Name 0116', \
                     'application_description': 'App Desc 0116', \
                     'component_name': 'Comp 4', \
                     'operating_system': 'RHEL 8.1', \
                     'programming_languages': 'python 3.9.6', \
                     'middleware': 'JBoss 4.0.1', \
                     'database': 'Oracle SQl Developer 19.2', \
                     'integration_services_and_additional_softwares': 'PeopleSoft 7', \
                     'technology_summary': 'HTTP Client 4.5.6', \
                     'versioning_tool_type': '1', \
                     'application_inbound_interfaces': 5, \
                     'application_outbound_interfaces': 1, \
                     'devops_maturity_level': 'Moderate', \
                     'devops_tooling': 'Jenkins, Git, JIRA', \
                     'test_automation_%': '50%', \
                     'performance_testing_enabled': 'No', \
                     'KG Version': '1.0.4', \
                     'App': {'Oracle SQl Developer 19.2': {'Oracle SQL Developer': ('19.2', '19.4')}, \
                             'PeopleSoft 7': {'PeopleSoft': ('7', '7.5')} \
                             }, \
                     'Runlib': {}, \
                     'Lib': {}, \
                     'HW': {}, \
                     'App Server': {'JBoss 4.0.1': {'JBoss|*': ('4.0.1', '4.2.3')}}, \
                     'Lang': {'python 3.9.6': {'Python': ('3.9.6', '3.10.0')}}, \
                     'OS': {'RHEL 8.1': {'Linux|Red Hat Enterprise Linux': ('8.1', '8.3')}}, \
                     'Runtime': {}, \
                     'VM': {}, \
                     'Technology': {'HTTP Client 4.5.6': {'HTTP client': ('4.5.6', '4.5.6')}}, \
                     'Storage': {}, \
                     'Plugin': {} \
                     }]
        standardizer = Standardization()
        app_data = standardizer.app_standardizer(app_data)
        if app_data != expected:
            diff = DeepDiff(expected, app_data)
            print("Test app3 Diff = ", diff)
        self.assertTrue(app_data == expected)


    def test_compose_app4(self):
        app_data = [{'application_name': 'App 1 ',
                     'application_description': 'desc 1',
                     'technology_summary': "ZOS, JavaScript\nPL1, Private Cloud"},
                    {'application_name': 'App 2',
                     'application_description': 'desc 2',
                     'technology_summary': 'ZOS, PL1, Linux Red Hat\nLinux Ubuntu, JavaScript\nNode.js\nPHP\nPython\nScala'},
                    {'application_name': 'App 3',
                     'application_description': 'desc 3',
                     'technology_summary': 'AIX\nLinux Red Hat, Java\nOther, microservices, angular'}]

        expected = [{'application_name': 'App 1 ', 'application_description': 'desc 1', \
                     'technology_summary': 'ZOS, JavaScript\nPL1, Private Cloud', \
                     'KG Version': '1.0.4', \
                     'Lang': {'JavaScript': {'JavaScript': ('NA_VERSION', 'ES6')}, 'PL1': {'PL/I': ('1', '1')}}, \
                     'Runlib': {}, \
                     'Storage': {}, \
                     'OS': {'ZOS': {'MVS|z/OS': ('NA_VERSION', 'NA_VERSION')}}, \
                     'Plugin': {}, 'App': {}, \
                     'Technology': {'Private Cloud': {'Cloud': ('NA_VERSION', 'NA_VERSION')}}, \
                     'VM': {}, 'Lib': {}, 'App Server': {}, 'HW': {}, 'Runtime': {}}, \
                    {'application_name': 'App 2', 'application_description': 'desc 2', \
                     'technology_summary': 'ZOS, PL1, Linux Red Hat\nLinux Ubuntu, JavaScript\nNode.js\nPHP\nPython\nScala', \
                     'KG Version': '1.0.4', \
                     'Lang': {'PL1': {'PL/I': ('1', '1')}, 'JavaScript': {'JavaScript': ('NA_VERSION', 'ES6')}, \
                              'PHP': {'PHP': ('NA_VERSION', '8')}, 'Python': {'Python': ('NA_VERSION', '3.10.0')}, \
                              'Scala': {'Scala': ('NA_VERSION', '2.9.0')},
                     'Runlib': {}, 'Storage': {}, \
                     'OS': {'Linux Red Hat': {'Linux|Red Hat Enterprise Linux': ('NA_VERSION', '8.3')},
                            'Linux Ubuntu': {'Linux|Ubuntu': ('NA_VERSION', '20.10')},
                            'ZOS': {'MVS|z/OS': ('NA_VERSION', 'NA_VERSION')}}, \
                     'Plugin': {}, 'App': {}, 'Technology': {}, 'VM': {}, 'Lib': {}, 'App Server': {}, 'HW': {}, \
                     'Runtime': {'Node.js': {'Node.js': ('NA_VERSION', '18')}}
                     }, \
                    {'application_name': 'App 3', 'application_description': 'desc 3', \
                     'technology_summary': 'AIX\nLinux Red Hat, Java\nOther, microservices, angular', \
                     'KG Version': '1.0.4', \
                     'Lang': {'Java': {'Java|*': ('NA_VERSION', '21')}}, \
                     'Runlib': {}, 'Storage': {}, \
                     'OS': {'AIX': {'Unix|AIX': ('NA_VERSION', 'NA_VERSION')},
                            'Linux Red Hat': {'Linux|Red Hat Enterprise Linux': ('NA_VERSION', '8.3')}}, \
                     'Plugin': {}, 'App': {}, 'Technology': {}, 'VM': {}, \
                     'Lib': {'angular': {'JavaScript|AngularJS': ('NA_VERSION', 'NA_VERSION')}}, \
                     'App Server': {}, 'HW': {}, 'Runtime': {}, \
                     'unknown': ['microservices']}]
        standardizer = Standardization()
        app_data = standardizer.app_standardizer(app_data)
        if app_data != expected:
            diff = DeepDiff(expected, app_data)
            print("Test app4 Diff = ", diff)
        self.assertTrue(app_data == expected)


    def test_compose_app5(self):
        app_data = [{'application_name': 'App 1 ',
                     'application_description': 'desc 1',
                     'technology_summary': 'RHEL Java db2 10.0 WebSphere Application Server Redis angularJs,express.js,jenkins'}]

        expected = [{'application_name': 'App 1 ', 'application_description': 'desc 1', \
                     'technology_summary': 'RHEL Java db2 10.0 WebSphere Application Server Redis angularJs,express.js,jenkins', \
                     'KG Version': '1.0.4', \
                     'Technology': {'Application Server': {'Application Server': ('NA_VERSION', 'NA_VERSION')}}, \
                     'Runtime': {}, 'Runlib': {}, 'Plugin': {}, \
                     'Lang': {'Java': {'Java|*': ('NA_VERSION', '21')}}, 'Storage': {}, \
                     'App': {'db2 10.0': {'DB2': ('10.0', '10.5')}, 'Redis': {'Redis': ('NA_VERSION', '6.2.4')},
                             'jenkins': {'Jenkins': ('NA_VERSION', '2.314')}}, \
                     'OS': {'RHEL': {'Linux|Red Hat Enterprise Linux': ('NA_VERSION', '8.3')}}, \
                     'Lib': {'angularJs': {'JavaScript|AngularJS': ('NA_VERSION', 'NA_VERSION')},
                             'express.js': {'JavaScript|Express.js': ('NA_VERSION', 'NA_VERSION')}}, \
                     'VM': {}, 'HW': {},
                     'App Server': {
                         'WebSphere Application Server': {'Websphere Application Server (WAS)': ('NA_VERSION', '9')}}}]
        standardizer = Standardization()
        app_data = standardizer.app_standardizer(app_data)
        if app_data != expected:
            diff = DeepDiff(expected, app_data)
            print("Test app5 Diff = ", diff)
        self.assertTrue(app_data == expected)
