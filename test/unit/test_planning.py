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
from kg_utils.test_check import Test_check

class TestPlan(unittest.TestCase):

    def test_ui_to_input_assessment(self):
        plan = Plan()
        assessment_data = [
            {
                "Name": "App Name 0114",
                "Desc": "App Desc 0114",
                "Cmpt": "Comp 1",
                "OS": {"Rhel": {"standard_name": "Linux|Red Hat Enterprise Linux"}},
                "Lang": {"Java": {"standard_name": "Java|*"}},
                "App Server": {"WebSphere Application Server": {"standard_name": "Websphere Application Server (WAS)"}},
                "Dependent Apps": {
                    "db2 10.0": {"standard_name": "DB2", "detected_version": "10.0", "latest_known_version": ""},
                    "Redis": {"standard_name": "Redis"},
                    "jenkins": {"standard_name": "Jenkins"}},
                "Runtime": {},
                "Libs": {"angularJs": {"standard_name": "JavaScript|AngularJS"},
                         "express.js": {"standard_name": "JavaScript|Express.js"}},
                "KG Version": "1.0.1",
                "Reason": ""
            }]
        expected = [{'application_name': 'App Name 0114', 'application_description': 'App Desc 0114',
                     'component_name': 'Comp 1', 'OS': {"Rhel": {"standard_name": "Linux|Red Hat Enterprise Linux"}},
                     'Lang': {"Java": {"standard_name": "Java|*"}}, 'App Server': {
                "WebSphere Application Server": {"standard_name": "Websphere Application Server (WAS)"}}, 'App': {
                "db2 10.0": {"standard_name": "DB2", "detected_version": "10.0", "latest_known_version": ""},
                "Redis": {"standard_name": "Redis"}, "jenkins": {"standard_name": "Jenkins"}}, 'Runtime': {},
                     'Lib': {"angularJs": {"standard_name": "JavaScript|AngularJS"},
                             "express.js": {"standard_name": "JavaScript|Express.js"}}, 'assessment_reason': '',
                     'KG Version': '1.0.1'}]

        appL = plan.ui_to_input_assessment(assessment_data)
        assert Test_check.checkEqual(Test_check,expected,appL)

    def test_validate_app(self):
        plan = Plan()
        appL = [{'application_name': 'App Name 0114', 'application_description': 'App Desc 0114',
                 'component_name': 'Comp 1', 'OS': {"Rhel": {"standard_name": "Linux|Red Hat Enterprise Linux"}},
                 'Lang': {"Java": {"standard_name": "Java|*"}}, 'App Server': {
                "WebSphere Application Server": {"standard_name": "Websphere Application Server (WAS)"}},
                 'App': {"db2 10.0": {"standard_name": "DB2", "detected_version": "10.0", "latest_known_version": ""},
                         "Redis": {"standard_name": "Redis"}, "jenkins": {"standard_name": "Jenkins"}}, 'Runtime': {},
                 'Lib': {"angularJs": {"standard_name": "JavaScript|AngularJS"},
                         "express.js": {"standard_name": "JavaScript|Express.js"}}, 'assessment_reason': '',
                 'KG Version': '1.0.1'}]
        expected = [{'application_name': 'App Name 0114', 'application_description': 'App Desc 0114',
                     'component_name': 'Comp 1', 'OS': {"Rhel": {"standard_name": "Linux|Red Hat Enterprise Linux"}},
                     'Lang': {"Java": {"standard_name": "Java|*"}}, 'App Server': {
                "WebSphere Application Server": {"standard_name": "Websphere Application Server (WAS)"}}, 'App': {
                "db2 10.0": {"standard_name": "DB2", "detected_version": "10.0", "latest_known_version": ""},
                "Redis": {"standard_name": "Redis"}, "jenkins": {"standard_name": "Jenkins"}}, 'Runtime': {},
                     'Lib': {"angularJs": {"standard_name": "JavaScript|AngularJS"},
                             "express.js": {"standard_name": "JavaScript|Express.js"}}, 'assessment_reason': '',
                     'KG Version': '1.0.1', 'valid_assessment': True}]

        appL = plan.validate_app(appL)
        assert Test_check.checkEqual(Test_check,appL,expected)

    def test_infer_missing_tech(self):
        inferTech = InferTech()
        appL = [{'application_name': 'App Name 0114', 'application_description': 'App Desc 0114',
                 'component_name': 'Comp 1', 'OS': {"Rhel": {"standard_name": "Linux|Red Hat Enterprise Linux"}},
                 'Lang': {"Java": {"standard_name": "Java|*"}}, 'App Server': {
                "WebSphere Application Server": {"standard_name": "Websphere Application Server (WAS)"}},
                 'App': {"db2 10.0": {"standard_name": "DB2", "detected_version": "10.0", "latest_known_version": ""},
                         "Redis": {"standard_name": "Redis"}, "jenkins": {"standard_name": "Jenkins"}}, 'Runtime': {},
                 'Lib': {"angularJs": {"standard_name": "JavaScript|AngularJS"},
                         "express.js": {"standard_name": "JavaScript|Express.js"}}, 'assessment_reason': '',
                 'KG Version': '1.0.1', 'valid_assessment': True}]
        expected = [{'application_name': 'App Name 0114', 'application_description': 'App Desc 0114',
                     'component_name': 'Comp 1', 'OS': {"Rhel": {"standard_name": "Linux|Red Hat Enterprise Linux"}},
                     'Lang': {"Java": {"standard_name": "Java|*"},
                              'angularJs': {"standard_name": "JavaScript|*", "detected_version": "NA_VERSION",
                                            "latest_known_version": "NA_VERSION"}}, 'App Server': {
                "WebSphere Application Server": {"standard_name": "Websphere Application Server (WAS)"}}, 'App': {
                "db2 10.0": {"standard_name": "DB2", "detected_version": "10.0", "latest_known_version": ""},
                "Redis": {"standard_name": "Redis"}, "jenkins": {"standard_name": "Jenkins"}}, 'Runtime': {},
                     'Lib': {'angularJs': {"standard_name": "JavaScript|AngularJS"},
                             'express.js': {"standard_name": "JavaScript|Express.js"}}, 'assessment_reason': '',
                     'KG Version': '1.0.1', 'valid_assessment': True, 'VM': {}, 'Technology': {}, 'Storage': {},
                     'Plugin': {}, 'Runlib': {}, 'HW': {},
                     'Inferred': {'Lang': ['JavaScript|*'], 'App': [], 'App Server': [], 'Runtime': [], 'OS': []},
                     'Recommended OS': 'Linux',
                     'Linux': {'Lang': ['Java|*', 'JavaScript|*'], 'App': ['DB2', 'Redis', 'Jenkins'],
                               'App Server': ['Websphere Application Server (WAS)'], 'Runtime': []},
                     'Windows': {'Lang': [], 'App': [], 'App Server': [], 'Runtime': []}, 'RepackageOS': ['Linux']}]

        appL = inferTech.infer_missing_tech(appL)
        assert Test_check.checkEqual(Test_check,expected,appL)


    def test_map_to_docker(self):
        plan = Plan(catalog="dockerhub")
        appL = [{'application_name': 'App Name 0114', 'application_description': 'App Desc 0114',
                 'component_name': 'Comp 1', 'OS': {"RHEL": {"standard_name": "Linux|Red Hat Enterprise Linux"}},
                 'Lang': {"Java": {"standard_name": "Java|*"},
                          'angularJs': {"standard_name": "JavaScript", "detected_version": "NA_VERSION",
                                        "latest_known_version": "NA_VERSION"}}, 'App Server': {
                "WebSphere Application Server": {"standard_name": "Websphere Application Server (WAS)"}},
                 'App': {"db2 10.0": {"standard_name": "DB2", "detected_version": "10.0", "latest_known_version": ""},
                         "Redis": {"standard_name": "Redis"}, "jenkins": {"standard_name": "Jenkins"}}, 'Runtime': {},
                 'Lib': {'angularJs': {"standard_name": "JavaScript|AngularJS"},
                         'express.js': {"standard_name": "JavaScript|Express.js"}}, 'assessment_reason': '',
                 'KG Version': '1.0.1', 'valid_assessment': True, 'VM': {}, 'Technology': {}, 'Storage': {},
                 'Plugin': {}, 'Runlib': {}, 'HW': {},
                 'Inferred': {'Lang': ['JavaScript|*'], 'App': [], 'App Server': [], 'Runtime': [], 'OS': []},
                 'Recommended OS': 'Linux',
                 'Linux': {'Lang': ['Java|*', 'JavaScript|*'], 'App': ['DB2', 'Redis', 'Jenkins'],
                           'App Server': ['Websphere Application Server (WAS)'], 'Runtime': []},
                 'Windows': {'Lang': [], 'App': [], 'App Server': [], 'Runtime': []}, 'RepackageOS': ['Linux']}]
        expected = [{'application_name': 'App Name 0114', 'application_description': 'App Desc 0114',
                     'component_name': 'Comp 1', 'OS': {'RHEL': {"standard_name": "Linux|Red Hat Enterprise Linux"}},
                     'Lang': {'Java': {"standard_name": "Java|*"},
                              'angularJs': {"standard_name": "JavaScript", "detected_version": "NA_VERSION",
                                            "latest_known_version": "NA_VERSION"}}, 'App Server': {
                'WebSphere Application Server': {"standard_name": "Websphere Application Server (WAS)"}}, 'App': {
                'db2 10.0': {"standard_name": "DB2", "detected_version": "10.0", "latest_known_version": ""},
                'Redis': {"standard_name": "Redis"}, 'jenkins': {"standard_name": "Jenkins"}}, 'Runtime': {},
                     'Lib': {'angularJs': {"standard_name": "JavaScript|AngularJS"},
                             'express.js': {"standard_name": "JavaScript|Express.js"}}, 'assessment_reason': '',
                     'KG Version': '1.0.1', 'valid_assessment': True, 'VM': {}, 'Runlib': {}, 'Plugin': {},
                     'Technology': {}, 'HW': {}, 'Storage': {},
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

        # add correction in case difference is for lower case vs upper case
        if appL != expected:
            new_key_assign = {}
            for k in expected[0]['scope_images'].keys():
                new_key_assign[k] = k.lower()
            expected[0]['scope_images'] = dict(
                [(new_key_assign.get(key), value) for key, value in expected[0]['scope_images'].items()])
            new_value_assign = {}
            for k in expected[0]['scope_images_confidence']['mapping'].values():
                new_value_assign[k] = k.lower()
            expected[0]['scope_images_confidence']['mapping'] = dict([(key, new_value_assign.get(value)) for key, value in
                                                                      expected[0]['scope_images_confidence'][
                                                                          'mapping'].items()])

        self.assertTrue(Test_check.checkEqual(Test_check,expected,appL))



    def test_output_to_ui_planning(self):
        plan = Plan()
        appL = [{'application_name': 'App Name 0114', 'application_description': 'App Desc 0114',
                 'component_name': 'Comp 1', 'OS': {'RHEL': {"standard_name": "Linux|Red Hat Enterprise Linux"}},
                 'Lang': {'Java': {"standard_name": "Java|*"},
                          'angularJs': {"standard_name": "JavaScript", "detected_version": "NA_VERSION",
                                        "latest_known_version": "NA_VERSION"}}, 'App Server': {
                'WebSphere Application Server': {"standard_name": "Websphere Application Server (WAS)"}},
                 'App': {'db2 10.0': {"standard_name": "DB2", "detected_version": "10.0", "latest_known_version": ""},
                         'Redis': {"standard_name": "Redis"}, 'jenkins': {"standard_name": "Jenkins"}}, 'Runtime': {},
                 'Lib': {'angularJs': {"standard_name": "JavaScript|AngularJS"},
                         'express.js': {"standard_name": "JavaScript|Express.js"}}, 'assessment_reason': '',
                 'KG Version': '1.0.1', 'valid_assessment': True, 'VM': {}, 'Runlib': {}, 'Plugin': {},
                 'Technology': {}, 'HW': {}, 'Storage': {},
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

        expected = {
            'Name': 'App Name 0114',
            'Desc': 'App Desc 0114',
            'Cmpt': 'Comp 1',
            'Valid': True,
            'Ref Dockers': [{'name': 'websphere-traditional', 'status': '',
                             'url': 'https://hub.docker.com/r/ibmcom/websphere-traditional/'},
                            {'name': 'db2', 'status': 'Verified Publisher',
                             'url': 'https://hub.docker.com/r/ibmcom/db2'},
                            {'name': 'redis_Linux', 'status': 'Official Image',
                             'url': 'https://hub.docker.com/_/redis/'}, {'name': 'jenkins', 'status': 'Official Image',
                                                                         'url': 'https://hub.docker.com/_/jenkins/'}],
            'Confidence': 0.93,
            'Reason': 'Additional Installations in container image 1,2,3,4: JavaScript|*',
            'Recommend': 'Containerize',
        }

        expected = OrderedDict(expected)
        expected = [expected]
        pAppL = plan.output_to_ui_planning(appL)
        self.assertTrue(Test_check.checkEqual(Test_check,expected,pAppL))

    def test_map_to_docker_openshift(self):
        plan = Plan(catalog="openshift")
        appL = [{'application_name': 'App Name 0114', 'application_description': 'App Desc 0114',
                 'component_name': 'Comp 1', 'OS': {"RHEL": {"standard_name": "Linux|Red Hat Enterprise Linux"}},
                 'Lang': {"Java": {"standard_name": "Java|*"},
                          'angularJs': {"standard_name": "JavaScript|*", "detected_version": "NA_VERSION",
                                        "latest_known_version": "NA_VERSION"}}, 'App Server': {
                "WebSphere Application Server": {"standard_name": "Websphere Application Server (WAS)"}},
                 'App': {"db2 10.0": {"standard_name": "DB2", "detected_version": "10.0", "latest_known_version": ""},
                         "Redis": {"standard_name": "Redis"}, "jenkins": {"standard_name": "Jenkins"}}, 'Runtime': {},
                 'Lib': {'angularJs': {"standard_name": "JavaScript|AngularJS"},
                         'express.js': {"standard_name": "JavaScript|Express.js"}}, 'assessment_reason': '',
                 'KG Version': '1.0.1', 'valid_assessment': True, 'VM': {}, 'Technology': {}, 'Storage': {},
                 'Plugin': {}, 'Runlib': {}, 'HW': {},
                 'Inferred': {'Lang': ['JavaScript|*'], 'App': [], 'App Server': [], 'Runtime': [], 'OS': []},
                 'Recommended OS': 'Linux',
                 'Linux': {'Lang': ['Java|*', 'JavaScript|*'], 'App': ['DB2', 'Redis', 'Jenkins'],
                           'App Server': ['Websphere Application Server (WAS)'], 'Runtime': []},
                 'Windows': {'Lang': [], 'App': [], 'App Server': [], 'Runtime': []}, 'RepackageOS': ['Linux']}]
        expected = [{'application_name': 'App Name 0114', 'application_description': 'App Desc 0114',
                     'component_name': 'Comp 1', 'OS': {'RHEL': {"standard_name": "Linux|Red Hat Enterprise Linux"}},
                     'Lang': {'Java': {"standard_name": "Java|*"},
                              'angularJs': {"standard_name": "JavaScript|*", "detected_version": "NA_VERSION",
                                            "latest_known_version": "NA_VERSION"}}, 'App Server': {
                'WebSphere Application Server': {"standard_name": "Websphere Application Server (WAS)"}}, 'App': {
                'db2 10.0': {"standard_name": "DB2", "detected_version": "10.0", "latest_known_version": ""},
                'Redis': {"standard_name": "Redis"}, 'jenkins': {"standard_name": "Jenkins"}}, 'Runtime': {},
                     'Lib': {'angularJs': {"standard_name": "JavaScript|AngularJS"},
                             'express.js': {"standard_name": "JavaScript|Express.js"}}, 'assessment_reason': '',
                     'KG Version': '1.0.1', 'valid_assessment': True, 'VM': {}, 'Runlib': {}, 'Plugin': {},
                     'Technology': {}, 'HW': {}, 'Storage': {},
                     'Inferred': {'Lang': ['JavaScript|*'], 'App': [], 'App Server': [], 'Runtime': [], 'OS': []},
                     'Recommended OS': 'Linux',
                     'Linux': {'Lang': ['Java|*', 'JavaScript|*'], 'App': ['DB2', 'Redis', 'Jenkins'],
                               'App Server': ['Websphere Application Server (WAS)'], 'Runtime': []},
                     'Windows': {'Lang': [], 'App': [], 'App Server': [], 'Runtime': []}, 'RepackageOS': ['Linux'],
                     'valid_planning': True, 'planning_reason': '', 'scope_images': {'websphere-traditional': {
                'Docker_URL': 'https://catalog.redhat.com/software/containers/r/ibmcom/websphere-traditional/5d77b2e4702c566f4cbf438b',
                'Status': None}, 'db2': {
                'Docker_URL': 'https://catalog.redhat.com/software/containers/ibm/ibm-db2z-ui/5d8bd4bf69aea310b5373e17',
                'Status': None}, 'redis_Linux': {
                'Docker_URL': 'https://catalog.redhat.com/software/containers/rhel8/redis-5/5c401b0cbed8bd75a2c4c287',
                'Status': None}, 'jenkins': {
                'Docker_URL': 'https://catalog.redhat.com/software/containers/openshift3/jenkins-2-rhel7/581d2f4500e5d05639b6517b',
                'Status': None}}, 'scope_images_confidence': {
                'mapping': {'Websphere Application Server (WAS)': 'websphere-traditional', 'DB2': 'db2',
                            'Redis': 'redis_Linux', 'Jenkins': 'jenkins'}, 'image_confidence': 0.929,
                'images_score': 130, 'cum_scores': 140, 'custom_installations_needed': ['JavaScript|*'],
                'custom_images_needed': []}}]

        appL = plan.map_to_docker(appL, catalog='openshift')

        # add correction in case difference is for lower case vs upper case
        if appL != expected:
            new_key_assign = {}
            for k in expected[0]['scope_images'].keys():
                new_key_assign[k] = k.lower()
            expected[0]['scope_images'] = dict(
                [(new_key_assign.get(key), value) for key, value in expected[0]['scope_images'].items()])
            new_value_assign = {}
            for k in expected[0]['scope_images_confidence']['mapping'].values():
                new_value_assign[k] = k.lower()
            expected[0]['scope_images_confidence']['mapping'] = dict(
                [(key, new_value_assign.get(value)) for key, value in
                 expected[0]['scope_images_confidence'][
                     'mapping'].items()])

        self.assertTrue(Test_check.checkEqual(Test_check,expected,appL))

    def test_output_to_ui_planning_openshift(self):
        plan = Plan(catalog="openshift")
        appL = [{'application_name': 'App Name 0114', 'application_description': 'App Desc 0114',
                 'component_name': 'Comp 1', 'OS': {'RHEL': {"standard_name": "Linux|Red Hat Enterprise Linux"}},
                 'Lang': {'Java': {"standard_name": "Java|*"},
                          'angularJs': {"standard_name": "JavaScript|*", "detected_version": "NA_VERSION",
                                        "latest_known_version": "NA_VERSION"}}, 'App Server': {
                'WebSphere Application Server': {"standard_name": "Websphere Application Server (WAS)"}},
                 'App': {'db2 10.0': {"standard_name": "DB2", "detected_version": "10.0", "latest_known_version": ""},
                         'Redis': {"standard_name": "Redis"}, 'jenkins': {"standard_name": "Jenkins"}}, 'Runtime': {},
                 'Lib': {'angularJs': {"standard_name": "JavaScript|AngularJS"},
                         'express.js': {"standard_name": "JavaScript|Express.js"}}, 'assessment_reason': '',
                 'KG Version': '1.0.1', 'valid_assessment': True, 'VM': {}, 'Runlib': {}, 'Plugin': {},
                 'Technology': {}, 'HW': {}, 'Storage': {},
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
        expected = {
            'Name': 'App Name 0114',
            'Desc': 'App Desc 0114',
            'Cmpt': 'Comp 1',
            'Valid': True,
            'Ref Dockers': [{'name': 'websphere-traditional', 'status': '',
                             'url': 'https://catalog.redhat.com/software/containers/r/ibmcom/websphere-traditional/5d77b2e4702c566f4cbf438b'},
                            {'name': 'db2', 'status': '',
                             'url': 'https://catalog.redhat.com/software/containers/ibm/ibm-db2z-ui/5d8bd4bf69aea310b5373e17'},
                            {'name': 'redis_Linux', 'status': '',
                             'url': 'https://catalog.redhat.com/software/containers/rhel8/redis-5/5c401b0cbed8bd75a2c4c287'},
                            {'name': 'jenkins', 'status': '',
                             'url': 'https://catalog.redhat.com/software/containers/openshift3/jenkins-2-rhel7/581d2f4500e5d05639b6517b'}],
            'Confidence': 0.93,
            'Reason': 'Additional Installations in container image 1,2,3,4: JavaScript|*',
            'Recommend': 'Containerize'
        }

        expected = OrderedDict(expected)
        expected = [expected]
        pAppL = plan.output_to_ui_planning(appL)
        self.assertTrue(Test_check.checkEqual(Test_check,expected,pAppL))

    def test_map_to_docker_operator(self):
        plan = Plan(catalog="operators")
        appL = [{'application_name': 'app1', 'application_description': 'app1', 'component_name': '',
                 'OS': {'linux': {"standard_name": "Linux|*"}}, 'Lang': {}, 'App Server': {},
                 'App': {'mongodb': {"standard_name": "MongoDB"}}, 'Runtime': {}, 'Lib': {}, 'assessment_reason': '',
                 'KG Version': '1.0.2', 'VM': {}, 'Runlib': {}, 'Technology': {}, 'Plugin': {}, 'HW': {}, 'Storage': {},
                 'Inferred': {'Lang': [], 'App': [], 'App Server': [], 'Runtime': [], 'OS': []},
                 'Recommended OS': 'Linux, Unix, Windows, macOS',
                 'Linux': {'Lang': [], 'App': ['MongoDB'], 'App Server': [], 'Runtime': []},
                 'Windows': {'Lang': [], 'App': [], 'App Server': [], 'Runtime': []}, 'RepackageOS': ['Linux'],
                 'valid_assessment': True}]
        expected = [{'application_name': 'app1', 'application_description': 'app1', 'component_name': '',
                     'OS': {'linux': {"standard_name": "Linux|*"}}, 'Lang': {}, 'App Server': {},
                     'App': {'mongodb': {"standard_name": "MongoDB"}}, 'Runtime': {}, 'Lib': {},
                     'assessment_reason': '', 'KG Version': '1.0.2', 'VM': {}, 'Runlib': {}, 'Technology': {},
                     'Plugin': {}, 'HW': {}, 'Storage': {},
                     'Inferred': {'Lang': [], 'App': [], 'App Server': [], 'Runtime': [], 'OS': []},
                     'Recommended OS': 'Linux, Unix, Windows, macOS',
                     'Linux': {'Lang': [], 'App': ['MongoDB'], 'App Server': [], 'Runtime': []},
                     'Windows': {'Lang': [], 'App': [], 'App Server': [], 'Runtime': []}, 'RepackageOS': ['Linux'],
                     'valid_assessment': True, 'valid_planning': True, 'planning_reason': '', 'scope_images': {
                'MongoDB Enterprise Operator': {'Docker_URL': 'quay.io/mongodb/mongodb-enterprise-operator',
                                                'Status': None}},
                     'scope_images_confidence': {'mapping': {'MongoDB': 'MongoDB Enterprise Operator'},
                                                 'image_confidence': 1.0, 'images_score': 60, 'cum_scores': 60,
                                                 'custom_installations_needed': [], 'custom_images_needed': []}}]

        appL = plan.map_to_docker(appL, catalog='operators')

        # add correction in case difference is for lower case vs upper case and operator version number
        if appL != expected:
            new_key_assign = {}
            for k in expected[0]['scope_images'].keys():
                new_key_assign[k] = k.lower()
            expected[0]['scope_images'] = dict(
                [(new_key_assign.get(key), value) for key, value in expected[0]['scope_images'].items()])
            new_value_assign = {}
            for k in expected[0]['scope_images_confidence']['mapping'].values():
                new_value_assign[k] = k.lower()
            expected[0]['scope_images_confidence']['mapping'] = dict([(key, new_value_assign.get(value)) for key, value in
                                                                      expected[0]['scope_images_confidence'][
                                                                          'mapping'].items()])

        self.assertTrue(Test_check.checkEqual(Test_check,expected,appL))

    def test_output_to_ui_planning_operator(self):
        plan = Plan(catalog="operators")
        appL = [{'application_name': 'app1', 'application_description': 'app1', 'component_name': '',
                 'OS': {'linux': {"standard_name": "Linux|*"}}, 'Lang': {}, 'App Server': {},
                 'App': {'mongodb': {"standard_name": "MongoDB"}}, 'Runtime': {}, 'Lib': {}, 'assessment_reason': '',
                 'KG Version': '1.0.2', 'VM': {}, 'Runlib': {}, 'Technology': {}, 'Plugin': {}, 'HW': {}, 'Storage': {},
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
        expected = {'Name': 'app1', 'Desc': 'app1', 'Cmpt': '', 'Valid': True, 'Ref Dockers': [
            {'name': 'MongoDB Enterprise Operator', 'status': '',
             'url': 'quay.io/mongodb/mongodb-enterprise-operator:NA'}], 'Confidence': 1.0,
                    'Reason': 'No additonal installations required.', 'Recommend': 'Containerize'}

        expected = OrderedDict(expected)
        expected = [expected]
        pAppL = plan.output_to_ui_planning(appL)
        self.assertTrue(Test_check.checkEqual(Test_check,expected,pAppL))