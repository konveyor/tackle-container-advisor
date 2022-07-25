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
from collections import OrderedDict
from service.planning import Plan
from service.infer_tech import InferTech

class TestPlan(unittest.TestCase):

    def test_ui_to_input_assessment(self):
        plan = Plan()
        assessment_data = [
            {
                "Name": "App Name 0114",
                "Desc": "App Desc 0114",
                "Cmpt": "Comp 1",
                "OS": "{'RHEL': {'Linux|Red Hat Enterprise Linux': ''}}",
                "Lang": "{'Java': {'Java|*': ''}}",
                "App Server": "{'WebSphere Application Server': {'Websphere Application Server (WAS)': ''}}",
                "Dependent Apps": "{'db2 10.0': {'DB2': '10.0'}, 'Redis': {'Redis': ''}, 'jenkins': {'Jenkins': ''}}",
                "Runtime": "{}",
                "Libs": "{'angularJs': {'JavaScript|AngularJS': ''}, 'express.js': {'JavaScript|Express.js': ''}}",
                "KG Version": "1.0.1",
                "Reason": ""
            }]
        expected = [{'application_name': 'App Name 0114', 'application_description': 'App Desc 0114',
                     'component_name': 'Comp 1', 'OS': {'RHEL': {'Linux|Red Hat Enterprise Linux': ''}},
                     'Lang': {'Java': {'Java|*': ''}},
                     'App Server': {'WebSphere Application Server': {'Websphere Application Server (WAS)': ''}},
                     'App': {'db2 10.0': {'DB2': '10.0'}, 'Redis': {'Redis': ''}, 'jenkins': {'Jenkins': ''}},
                     'Runtime': {},
                     'Lib': {'angularJs': {'JavaScript|AngularJS': ''}, 'express.js': {'JavaScript|Express.js': ''}},
                     'assessment_reason': '', 'KG Version': '1.0.1'}]
        appL = plan.ui_to_input_assessment(assessment_data)
        assert [dict(appL[0])] == expected

    def test_validate_app(self):
        plan = Plan()
        appL = [{'application_name': 'App Name 0114', 'application_description': 'App Desc 0114',
                 'component_name': 'Comp 1', 'OS': {'RHEL': {'Linux|Red Hat Enterprise Linux': ''}},
                 'Lang': {'Java': {'Java|*': ''}},
                 'App Server': {'WebSphere Application Server': {'Websphere Application Server (WAS)': ''}},
                 'App': {'db2 10.0': {'DB2': '10.0'}, 'Redis': {'Redis': ''}, 'jenkins': {'Jenkins': ''}},
                 'Runtime': {},
                 'Lib': {'angularJs': {'JavaScript|AngularJS': ''}, 'express.js': {'JavaScript|Express.js': ''}},
                 'assessment_reason': '', 'KG Version': '1.0.1'}]
        expected = [{'application_name': 'App Name 0114', 'application_description': 'App Desc 0114',
                     'component_name': 'Comp 1', 'OS': {'RHEL': {'Linux|Red Hat Enterprise Linux': ''}},
                     'Lang': {'Java': {'Java|*': ''}},
                     'App Server': {'WebSphere Application Server': {'Websphere Application Server (WAS)': ''}},
                     'App': {'db2 10.0': {'DB2': '10.0'}, 'Redis': {'Redis': ''}, 'jenkins': {'Jenkins': ''}},
                     'Runtime': {},
                     'Lib': {'angularJs': {'JavaScript|AngularJS': ''}, 'express.js': {'JavaScript|Express.js': ''}},
                     'assessment_reason': '', 'KG Version': '1.0.1', 'valid_assessment': True}]

        appL = plan.validate_app(appL)
        assert appL == expected

    def test_infer_missing_tech(self):
        inferTech = InferTech()
        appL = [{'application_name': 'App Name 0114', 'application_description': 'App Desc 0114',
                 'component_name': 'Comp 1', 'OS': {'RHEL': {'Linux|Red Hat Enterprise Linux': ''}},
                 'Lang': {'Java': {'Java': ''}},
                 'App Server': {'WebSphere Application Server': {'Websphere Application Server (WAS)': ''}},
                 'App': {'db2 10.0': {'DB2': '10.0'}, 'Redis': {'Redis': ''}, 'jenkins': {'Jenkins': ''}},
                 'Runtime': {},
                 'Lib': {'angularJs': {'JavaScript|AngularJS': ''}, 'express.js': {'JavaScript|Express.js': ''}},
                 'assessment_reason': '', 'KG Version': '1.0.1', 'valid_assessment': True}]
        expected = [{'application_name': 'App Name 0114', 'application_description': 'App Desc 0114',
                     'component_name': 'Comp 1', 'OS': {'RHEL': {'Linux|Red Hat Enterprise Linux': ''}},
                     'Lang': {'Java': {'Java': ''}, 'angularJs': {'JavaScript': ''}},
                     'App Server': {'WebSphere Application Server': {'Websphere Application Server (WAS)': ''}},
                     'App': {'db2 10.0': {'DB2': '10.0'}, 'Redis': {'Redis': ''}, 'jenkins': {'Jenkins': ''}},
                     'Runtime': {},
                     'Lib': {'angularJs': {'JavaScript|AngularJS': ''}, 'express.js': {'JavaScript|Express.js': ''}},
                     'assessment_reason': '', 'KG Version': '1.0.1', 'valid_assessment': True, 'VM': {},
                     'Technology': {}, 'Storage': {}, 'Plugin': {}, 'Runlib': {}, 'HW': {},
                     'Inferred': {'Lang': ['JavaScript'], 'App': [], 'App Server': [], 'Runtime': [], 'OS': []},
                     'Recommended OS': 'Linux',
                     'Linux': {'Lang': ['Java', 'JavaScript'], 'App': ['DB2', 'Redis', 'Jenkins'],
                               'App Server': ['Websphere Application Server (WAS)'], 'Runtime': []},
                     'Windows': {'Lang': [], 'App': [], 'App Server': [], 'Runtime': []}, 'RepackageOS': ['Linux']}]

        appL = inferTech.infer_missing_tech(appL)
        assert appL == expected


    def test_map_to_docker(self):
        plan = Plan()
        appL = [{'application_name': 'App Name 0114', 'application_description': 'App Desc 0114',
                 'component_name': 'Comp 1', 'OS': {'RHEL': {'Linux|Red Hat Enterprise Linux': ''}},
                 'Lang': {'Java': {'Java|*': ''}, 'angularJs': {'JavaScript': ''}},
                 'App Server': {'WebSphere Application Server': {'Websphere Application Server (WAS)': ''}},
                 'App': {'db2 10.0': {'DB2': '10.0'}, 'Redis': {'Redis': ''}, 'jenkins': {'Jenkins': ''}},
                 'Runtime': {},
                 'Lib': {'angularJs': {'JavaScript|AngularJS': ''}, 'express.js': {'JavaScript|Express.js': ''}},
                 'assessment_reason': '', 'KG Version': '1.0.1', 'valid_assessment': True, 'VM': {}, 'Runlib': {},
                 'Plugin': {}, 'Technology': {}, 'HW': {}, 'Storage': {},
                 'Inferred': {'Lang': ['JavaScript|*'], 'App': [], 'App Server': [], 'Runtime': [], 'OS': []},
                 'Recommended OS': 'Linux',
                 'Linux': {'Lang': ['Java|*', 'JavaScript|*'], 'App': ['DB2', 'Redis', 'Jenkins'],
                           'App Server': ['Websphere Application Server (WAS)'], 'Runtime': []},
                 'Windows': {'Lang': [], 'App': [], 'App Server': [], 'Runtime': []}, 'RepackageOS': ['Linux']}]
        expected = [{'application_name': 'App Name 0114', 'application_description': 'App Desc 0114',
                     'component_name': 'Comp 1', 'OS': {'RHEL': {'Linux|Red Hat Enterprise Linux': ''}},
                     'Lang': {'Java': {'Java|*': ''}, 'angularJs': {'JavaScript': ''}},
                     'App Server': {'WebSphere Application Server': {'Websphere Application Server (WAS)': ''}},
                     'App': {'db2 10.0': {'DB2': '10.0'}, 'Redis': {'Redis': ''}, 'jenkins': {'Jenkins': ''}},
                     'Runtime': {},
                     'Lib': {'angularJs': {'JavaScript|AngularJS': ''}, 'express.js': {'JavaScript|Express.js': ''}},
                     'assessment_reason': '', 'KG Version': '1.0.1', 'valid_assessment': True, 'VM': {}, 'Runlib': {},
                     'Plugin': {}, 'Technology': {}, 'HW': {}, 'Storage': {},
                     'Inferred': {'Lang': ['JavaScript|*'], 'App': [], 'App Server': [], 'Runtime': [], 'OS': []},
                     'Recommended OS': 'Linux',
                     'Linux': {'Lang': ['Java|*', 'JavaScript|*'], 'App': ['DB2', 'Redis', 'Jenkins'],
                               'App Server': ['Websphere Application Server (WAS)'], 'Runtime': []},
                     'Windows': {'Lang': [], 'App': [], 'App Server': [], 'Runtime': []}, 'RepackageOS': ['Linux'],
                     'valid_planning': True, 'planning_reason': '', 'scope_images': {
                'websphere-traditional': {'Docker_URL': 'https://hub.docker.com/r/ibmcom/websphere-traditional/',
                                          'Status': ''},
                'db2': {'Docker_URL': 'https://hub.docker.com/r/ibmcom/db2', 'Status': 'Verified Publisher'},
                'redis_Linux': {'Docker_URL': 'https://hub.docker.com/_/redis/', 'Status': 'Official Image'},
                'jenkins': {'Docker_URL': 'https://hub.docker.com/_/jenkins/', 'Status': 'Official Image'}},
                     'scope_images_confidence': {
                         'mapping': {'Websphere Application Server (WAS)': 'websphere-traditional', 'DB2': 'db2',
                                     'Redis': 'redis_Linux', 'Jenkins': 'jenkins'}, 'image_confidence': 0.929,
                         'images_score': 130, 'cum_scores': 140, 'custom_installations_needed': ['JavaScript|*'],
                         'custom_images_needed': []}}]

        appL = plan.map_to_docker(appL)
        self.assertTrue(appL == expected)



    def test_output_to_ui_planning(self):
        plan = Plan()
        appL = [{'application_name': 'App Name 0114', 'application_description': 'App Desc 0114',
                 'component_name': 'Comp 1', 'OS': {'RHEL': {'Linux|Red Hat Enterprise Linux': ''}},
                 'Lang': {'Java': {'Java': ''}, 'angularJs': {'JavaScript': ''}},
                 'App Server': {'WebSphere Application Server': {'Websphere Application Server (WAS)': ''}},
                 'App': {'db2 10.0': {'DB2': '10.0'}, 'Redis': {'Redis': ''}, 'jenkins': {'Jenkins': ''}},
                 'Runtime': {},
                 'Lib': {'angularJs': {'JavaScript|AngularJS': ''}, 'express.js': {'JavaScript|Express.js': ''}},
                 'assessment_reason': '', 'KG Version': '1.0.1', 'valid_assessment': True, 'VM': {}, 'Runlib': {},
                 'Plugin': {}, 'Technology': {}, 'HW': {}, 'Storage': {},
                 'Inferred': {'Lang': ['JavaScript'], 'App': [], 'App Server': [], 'Runtime': [], 'OS': []},
                 'Recommended OS': 'Linux',
                 'Linux': {'Lang': ['Java', 'JavaScript'], 'App': ['DB2', 'Redis', 'Jenkins'],
                           'App Server': ['Websphere Application Server (WAS)'], 'Runtime': []},
                 'Windows': {'Lang': [], 'App': [], 'App Server': [], 'Runtime': []}, 'RepackageOS': ['Linux'],
                 'valid_planning': True, 'planning_reason': '', 'scope_images': {
                'websphere-traditional': {'Docker_URL': 'https://hub.docker.com/r/ibmcom/websphere-traditional/',
                                          'Status': ''},
                'db2': {'Docker_URL': 'https://hub.docker.com/r/ibmcom/db2', 'Status': ''},
                'redis_Linux': {'Docker_URL': 'https://hub.docker.com/_/redis/', 'Status': 'Official Image'},
                'jenkins': {'Docker_URL': 'https://hub.docker.com/_/jenkins/', 'Status': 'Official Image'}},
                 'scope_images_confidence': {
                     'mapping': {'Websphere Application Server (WAS)': 'websphere-traditional', 'DB2': 'db2',
                                 'Redis': 'redis_Linux', 'Jenkins': 'jenkins'}, 'image_confidence': 0.929,
                     'images_score': 130, 'cum_scores': 140, 'custom_installations_needed': ['JavaScript'],
                     'custom_images_needed': []}}]

        expected = {
            'Name': 'App Name 0114',
            'Desc': 'App Desc 0114',
            'Cmpt': 'Comp 1',
            'Valid': True,
            'Ref Dockers': "1. {'websphere-traditional': 'https://hub.docker.com/r/ibmcom/websphere-traditional/'}\n2. {'db2': 'https://hub.docker.com/r/ibmcom/db2'}\n3. {'redis_Linux(Official Image)': 'https://hub.docker.com/_/redis/'}\n4. {'jenkins(Official Image)': 'https://hub.docker.com/_/jenkins/'}",
            'Confidence': 0.93,
            'Reason': 'Additional Installations in container image 1,2,3,4: JavaScript',
            'Recommend': 'Containerize',
        }

        expected = OrderedDict(expected)
        expected = [expected]
        pAppL = plan.output_to_ui_planning(appL)
        self.assertTrue(pAppL == expected)

    def test_map_to_docker_openshift(self):
        plan = Plan()
        appL = [{'application_name': 'App Name 0114', 'application_description': 'App Desc 0114',
                 'component_name': 'Comp 1', 'OS': {'RHEL': {'Linux|Red Hat Enterprise Linux': ''}},
                 'Lang': {'Java': {'Java|*': ''}, 'angularJs': {'JavaScript': ''}},
                 'App Server': {'WebSphere Application Server': {'Websphere Application Server (WAS)': ''}},
                 'App': {'db2 10.0': {'DB2': '10.0'}, 'Redis': {'Redis': ''}, 'jenkins': {'Jenkins': ''}},
                 'Runtime': {},
                 'Lib': {'angularJs': {'JavaScript|AngularJS': ''}, 'express.js': {'JavaScript|Express.js': ''}},
                 'assessment_reason': '', 'KG Version': '1.0.1', 'valid_assessment': True, 'VM': {}, 'Runlib': {},
                 'Plugin': {}, 'Technology': {}, 'HW': {}, 'Storage': {},
                 'Inferred': {'Lang': ['JavaScript|*'], 'App': [], 'App Server': [], 'Runtime': [], 'OS': []},
                 'Recommended OS': 'Linux',
                 'Linux': {'Lang': ['Java|*', 'JavaScript|*'], 'App': ['DB2', 'Redis', 'Jenkins'],
                           'App Server': ['Websphere Application Server (WAS)'], 'Runtime': []},
                 'Windows': {'Lang': [], 'App': [], 'App Server': [], 'Runtime': []}, 'RepackageOS': ['Linux']}]
        expected = [{'application_name': 'App Name 0114', 'application_description': 'App Desc 0114',
                     'component_name': 'Comp 1', 'OS': {'RHEL': {'Linux|Red Hat Enterprise Linux': ''}},
                     'Lang': {'Java': {'Java|*': ''}, 'angularJs': {'JavaScript': ''}},
                     'App Server': {'WebSphere Application Server': {'Websphere Application Server (WAS)': ''}},
                     'App': {'db2 10.0': {'DB2': '10.0'}, 'Redis': {'Redis': ''}, 'jenkins': {'Jenkins': ''}},
                     'Runtime': {},
                     'Lib': {'angularJs': {'JavaScript|AngularJS': ''}, 'express.js': {'JavaScript|Express.js': ''}},
                     'assessment_reason': '', 'KG Version': '1.0.1', 'valid_assessment': True, 'VM': {}, 'Runlib': {},
                     'Plugin': {}, 'Technology': {}, 'HW': {}, 'Storage': {},
                     'Inferred': {'Lang': ['JavaScript|*'], 'App': [], 'App Server': [], 'Runtime': [], 'OS': []},
                     'Recommended OS': 'Linux',
                     'Linux': {'Lang': ['Java|*', 'JavaScript|*'], 'App': ['DB2', 'Redis', 'Jenkins'],
                               'App Server': ['Websphere Application Server (WAS)'], 'Runtime': []},
                     'Windows': {'Lang': [], 'App': [], 'App Server': [], 'Runtime': []}, 'RepackageOS': ['Linux'],
                     'valid_planning': True, 'planning_reason': '', 'scope_images': {'websphere-traditional': {
                'Docker_URL': 'https://catalog.redhat.com/software/containers/r/ibmcom/websphere-traditional/5d77b2e4702c566f4cbf438b',
                'Status': ''}, 'db2': {
                'Docker_URL': 'https://catalog.redhat.com/software/containers/ibm/ibm-db2z-ui/5d8bd4bf69aea310b5373e17',
                'Status': ''}, 'redis_Linux': {
                'Docker_URL': 'https://catalog.redhat.com/software/containers/rhel8/redis-5/5c401b0cbed8bd75a2c4c287',
                'Status': ''}, 'jenkins': {
                'Docker_URL': 'https://catalog.redhat.com/software/containers/openshift3/jenkins-2-rhel7/581d2f4500e5d05639b6517b',
                'Status': ''}}, 'scope_images_confidence': {
                'mapping': {'Websphere Application Server (WAS)': 'websphere-traditional', 'DB2': 'db2',
                            'Redis': 'redis_Linux', 'Jenkins': 'jenkins'}, 'image_confidence': 0.929,
                'images_score': 130, 'cum_scores': 140, 'custom_installations_needed': ['JavaScript|*'],
                'custom_images_needed': []}}]

        appL = plan.map_to_docker(appL, 'openshift')
        self.assertTrue(appL == expected)

    def test_output_to_ui_planning_openshift(self):
        plan = Plan()
        appL = [{'application_name': 'App Name 0114', 'application_description': 'App Desc 0114',
                 'component_name': 'Comp 1', 'OS': {'RHEL': {'Linux|Red Hat Enterprise Linux': ''}},
                 'Lang': {'Java': {'Java': ''}, 'angularJs': {'JavaScript': ''}},
                 'App Server': {'WebSphere Application Server': {'Websphere Application Server (WAS)': ''}},
                 'App': {'db2 10.0': {'DB2': '10.0'}, 'Redis': {'Redis': ''}, 'jenkins': {'Jenkins': ''}},
                 'Runtime': {},
                 'Lib': {'angularJs': {'JavaScript|AngularJS': ''}, 'express.js': {'JavaScript|Express.js': ''}},
                 'assessment_reason': '', 'KG Version': '1.0.1', 'valid_assessment': True, 'VM': {}, 'Runlib': {},
                 'Plugin': {}, 'Technology': {}, 'HW': {}, 'Storage': {},
                 'Inferred': {'Lang': ['JavaScript'], 'App': [], 'App Server': [], 'Runtime': [], 'OS': []},
                 'Recommended OS': 'Linux',
                 'Linux': {'Lang': ['Java', 'JavaScript'], 'App': ['DB2', 'Redis', 'Jenkins'],
                           'App Server': ['Websphere Application Server (WAS)'], 'Runtime': []},
                 'Windows': {'Lang': [], 'App': [], 'App Server': [], 'Runtime': []}, 'RepackageOS': ['Linux'],
                 'valid_planning': True, 'planning_reason': '', 'scope_images': {'websphere-traditional': {
                'Docker_URL': 'https://catalog.redhat.com/software/containers/r/ibmcom/websphere-traditional/5d77b2e4702c566f4cbf438b',
                'Status': ''}, 'db2': {
                'Docker_URL': 'https://catalog.redhat.com/software/containers/ibm/ibm-db2z-ui/5d8bd4bf69aea310b5373e17?container-tabs=gti',
                'Status': ''}, 'redis_Linux': {
                'Docker_URL': 'https://catalog.redhat.com/software/containers/rhscl/redis-5-rhel7/5c9922045a13464733ee0ecc',
                'Status': ''}, 'jenkins': {
                'Docker_URL': 'https://catalog.redhat.com/software/containers/openshift3/jenkins-2-rhel7/581d2f4500e5d05639b6517b?container-tabs=gti&gti-tabs=get-the-source',
                'Status': ''}}, 'scope_images_confidence': {
                'mapping': {'Websphere Application Server (WAS)': 'websphere-traditional', 'DB2': 'db2',
                            'Redis': 'redis_Linux', 'Jenkins': 'jenkins'}, 'image_confidence': 0.929,
                'images_score': 130, 'cum_scores': 140, 'custom_installations_needed': ['JavaScript'],
                'custom_images_needed': []}}]
        expected = {
            'Name': 'App Name 0114',
            'Desc': 'App Desc 0114',
            'Cmpt': 'Comp 1',
            'Valid': True,
            'Ref Dockers': "1. {'websphere-traditional': 'https://catalog.redhat.com/software/containers/r/ibmcom/websphere-traditional/5d77b2e4702c566f4cbf438b'}\n2. {'db2': 'https://catalog.redhat.com/software/containers/ibm/ibm-db2z-ui/5d8bd4bf69aea310b5373e17?container-tabs=gti'}\n3. {'redis_Linux': 'https://catalog.redhat.com/software/containers/rhscl/redis-5-rhel7/5c9922045a13464733ee0ecc'}\n4. {'jenkins': 'https://catalog.redhat.com/software/containers/openshift3/jenkins-2-rhel7/581d2f4500e5d05639b6517b?container-tabs=gti&gti-tabs=get-the-source'}",
            'Confidence': 0.93,
            'Reason': 'Additional Installations in container image 1,2,3,4: JavaScript',
            'Recommend': 'Containerize'
        }

        expected = OrderedDict(expected)
        expected = [expected]
        pAppL = plan.output_to_ui_planning(appL)
        self.assertTrue(pAppL == expected)

    def test_map_to_docker_operator(self):
        plan = Plan()
        appL = [{'application_name': 'app1', 'application_description': 'app1', 'component_name': '',
                 'OS': {'linux': {'Linux': ''}}, 'Lang': {}, 'App Server': {}, 'App': {'mongodb': {'MongoDB': ''}},
                 'Runtime': {}, 'Lib': {}, 'assessment_reason': '', 'KG Version': '1.0.2', 'VM': {}, 'Runlib': {},
                 'Technology': {}, 'Plugin': {}, 'HW': {}, 'Storage': {},
                 'Inferred': {'Lang': [], 'App': [], 'App Server': [], 'Runtime': [], 'OS': []},
                 'Recommended OS': 'Linux, Unix, Windows, macOS',
                 'Linux': {'Lang': [], 'App': ['MongoDB'], 'App Server': [], 'Runtime': []},
                 'Windows': {'Lang': [], 'App': [], 'App Server': [], 'Runtime': []}, 'RepackageOS': ['Linux'],
                 'valid_assessment': True}]

        expected = [{'application_name': 'app1', 'application_description': 'app1', 'component_name': '',
                     'OS': {'linux': {'Linux': ''}}, 'Lang': {}, 'App Server': {}, 'App': {'mongodb': {'MongoDB': ''}},
                     'Runtime': {}, 'Lib': {}, 'assessment_reason': '', 'KG Version': '1.0.2', 'VM': {}, 'Runlib': {},
                     'Technology': {}, 'Plugin': {}, 'HW': {}, 'Storage': {},
                     'Inferred': {'Lang': [], 'App': [], 'App Server': [], 'Runtime': [], 'OS': []},
                     'Recommended OS': 'Linux, Unix, Windows, macOS',
                     'Linux': {'Lang': [], 'App': ['MongoDB'], 'App Server': [], 'Runtime': []},
                     'Windows': {'Lang': [], 'App': [], 'App Server': [], 'Runtime': []}, 'RepackageOS': ['Linux'],
                     'valid_assessment': True, 'valid_planning': True, 'planning_reason': '', 'scope_images': {
                'MongoDB Enterprise Operator': {'Docker_URL': 'quay.io/mongodb/mongodb-enterprise-operator:1.12.0',
                                                'Status': None}},
                     'scope_images_confidence': {'mapping': {'MongoDB': 'MongoDB Enterprise Operator'},
                                                 'image_confidence': 1.0, 'images_score': 60, 'cum_scores': 60,
                                                 'custom_installations_needed': [], 'custom_images_needed': []}}]

        appL = plan.map_to_docker(appL, 'operator')
        self.assertTrue(appL == expected)

    def test_output_to_ui_planning_operator(self):
        plan = Plan()
        appL = [{'application_name': 'app1', 'application_description': 'app1', 'component_name': '',
                 'OS': {'linux': {'Linux': ''}}, 'Lang': {}, 'App Server': {}, 'App': {'mongodb': {'MongoDB': ''}},
                 'Runtime': {}, 'Lib': {}, 'assessment_reason': '', 'KG Version': '1.0.2', 'VM': {}, 'Runlib': {},
                 'Technology': {}, 'Plugin': {}, 'HW': {}, 'Storage': {},
                 'Inferred': {'Lang': [], 'App': [], 'App Server': [], 'Runtime': [], 'OS': []},
                 'Recommended OS': 'Linux, Unix, Windows, macOS',
                 'Linux': {'Lang': [], 'App': ['MongoDB'], 'App Server': [], 'Runtime': []},
                 'Windows': {'Lang': [], 'App': [], 'App Server': [], 'Runtime': []}, 'RepackageOS': ['Linux'],
                 'valid_assessment': True, 'valid_planning': True, 'planning_reason': '', 'scope_images': {
                'MongoDB Enterprise Operator': {'Docker_URL': 'quay.io/mongodb/mongodb-enterprise-operator:1.12.0',
                                                'Status': None}},
                 'scope_images_confidence': {'mapping': {'MongoDB': 'MongoDB Enterprise Operator'},
                                             'image_confidence': 1.0, 'images_score': 60, 'cum_scores': 60,
                                             'custom_installations_needed': [], 'custom_images_needed': []}}]
        expected = {'Name': 'app1', 'Desc': 'app1', 'Cmpt': '', 'Valid': True,
                    'Ref Dockers': "1. {'MongoDB Enterprise Operator': 'quay.io/mongodb/mongodb-enterprise-operator:1.12.0'}",
                    'Confidence': 1.0, 'Reason': 'No additonal installations required.', 'Recommend': 'Containerize'}

        expected = OrderedDict(expected)
        expected = [expected]
        pAppL = plan.output_to_ui_planning(appL)
        self.assertTrue(pAppL == expected)
