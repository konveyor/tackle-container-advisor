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
from service.clustering import Clustering

class TestClustering(unittest.TestCase):

    def test_ui_to_input_assessment(self):
        cluster = Clustering()

        appL = [
            {
                "Name": "App 1",
                "Desc": "",
                "Cmpt": "",
                "OS": {"ZOS": {"standard_name": "MVS|z/OS", "detected_version": "NA_VERSION",
                               "latest_known_version": "NA_VERSION"}},
                "Lang": {"JavaScript": {"standard_name": "JavaScript|*", "detected_version": "NA_VERSION",
                                        "latest_known_version": "ES6"},
                         "PL/1": {"standard_name": "PL/I", "detected_version": "1", "latest_known_version": "1"}},
                "App Server": {}, "Dependent Apps": {}, "Runtime": {}, "Libs": {}, "Reason": "",
                "KG Version": "1.0.4"
            },
            {
                "Name": "App 2",
                "Desc": "",
                "Cmpt": "",
                "OS": {"Windows 2016": {"standard_name": "Windows|Windows Server", "detected_version": "2016",
                                        "latest_known_version": "2016"}},
                "Lang": {"JavaScript": {"standard_name": "JavaScript|*", "detected_version": "NA_VERSION",
                                        "latest_known_version": "ES6"},
                         "PL/1": {"standard_name": "PL/I", "detected_version": "1", "latest_known_version": "1"}},
                "App Server": {}, "Dependent Apps": {}, "Runtime": {}, "Libs": {},
                "Reason": "Reason 103: Unknown technologies detected: Standard",
                "KG Version": "1.0.4"
            },
            {
                "Name": "App 3",
                "Desc": "",
                "Cmpt": "",
                "OS": {"Windows": {"standard_name": "Windows|*", "detected_version": "NA_VERSION",
                                   "latest_known_version": "NA_VERSION"}},
                "Lang": {"ASP.net": {"standard_name": "Active Server Pages (ASP)", "detected_version": "NA_VERSION",
                                     "latest_known_version": "3"},
                         "C#": {"standard_name": "C#", "detected_version": "NA_VERSION",
                                "latest_known_version": "NA_VERSION"}},
                "App Server": {}, "Dependent Apps": {}, "Runtime": {}, "Libs": {}, "Reason": "",
                "KG Version": "1.0.4"
            },
            {
                "Name": "App 4",
                "Desc": "",
                "Cmpt": "",
                "OS": {"AIX": {"standard_name": "Unix|AIX", "detected_version": "NA_VERSION",
                               "latest_known_version": "NA_VERSION"},
                       "zOS": {"standard_name": "MVS|z/OS", "detected_version": "NA_VERSION",
                               "latest_known_version": "NA_VERSION"}},
                "Lang": {"Java": {"standard_name": "Java|*", "detected_version": "NA_VERSION",
                                  "latest_known_version": "21"}},
                "App Server": {}, "Dependent Apps": {}, "Runtime": {}, "Libs": {}, "Reason": "",
                "KG Version": "1.0.4"
            },
            {
                "Name": "App 5",
                "Desc": "",
                "Cmpt": "",
                "OS": {"zOS": {"standard_name": "MVS|z/OS", "detected_version": "NA_VERSION",
                               "latest_known_version": "NA_VERSION"}},
                "Lang": {"JavaScript": {"standard_name": "JavaScript|*", "detected_version": "NA_VERSION",
                                        "latest_known_version": "ES6"},
                         "PL1": {"standard_name": "PL/I", "detected_version": "1", "latest_known_version": "1"}},
                "App Server": {}, "Dependent Apps": {}, "Runtime": {}, "Libs": {}, "Reason": "",
                "KG Version": "1.0.4"
            }
        ]

        expected = [
            {
                "id": 0,
                "name": "unique_tech_stack_0",
                "type": "unique",
                "tech_stack": [
                    "PL/I",
                    "MVS|*",
                    "JavaScript|*"
                ],
                "num_elements": 2,
                "apps": [
                    {
                        "Name": "App 1",
                        "Desc": "", "Cmpt": "",
                        "OS": {"ZOS": {"standard_name": "MVS|z/OS", "detected_version": "NA_VERSION",
                                       "latest_known_version": "NA_VERSION"}},
                        "Lang": {"JavaScript": {"standard_name": "JavaScript|*", "detected_version": "NA_VERSION",
                                                "latest_known_version": "ES6"},
                                 "PL/1": {"standard_name": "PL/I", "detected_version": "1",
                                          "latest_known_version": "1"}},
                        "App Server": {}, "Dependent Apps": {}, "Runtime": {}, "Libs": {}, "Reason": "",
                        "KG Version": "1.0.4"
                    },
                    {
                        "Name": "App 5",
                        "Desc": "", "Cmpt": "",
                        "OS": {"zOS": {"standard_name": "MVS|z/OS", "detected_version": "NA_VERSION",
                                       "latest_known_version": "NA_VERSION"}},
                        "Lang": {"JavaScript": {"standard_name": "JavaScript|*", "detected_version": "NA_VERSION",
                                                "latest_known_version": "ES6"},
                                 "PL1": {"standard_name": "PL/I", "detected_version": "1",
                                         "latest_known_version": "1"}},
                        "App Server": {}, "Dependent Apps": {}, "Runtime": {}, "Libs": {}, "Reason": "",
                        "KG Version": "1.0.4"
                    }
                ]
            },
            {
                "id": 1,
                "name": "unique_tech_stack_1",
                "type": "unique",
                "tech_stack": [
                    "PL/I",
                    "Windows|*",
                    "JavaScript|*"
                ],
                "num_elements": 1,
                "apps": [
                    {
                        "Name": "App 2",
                        "Desc": "", "Cmpt": "",
                        "OS": {"Windows 2016": {"standard_name": "Windows|Windows Server", "detected_version": "2016",
                                                "latest_known_version": "2016"}},
                        "Lang": {"JavaScript": {"standard_name": "JavaScript|*", "detected_version": "NA_VERSION",
                                                "latest_known_version": "ES6"},
                                 "PL/1": {"standard_name": "PL/I", "detected_version": "1",
                                          "latest_known_version": "1"}},
                        "App Server": {}, "Dependent Apps": {}, "Runtime": {}, "Libs": {},
                        "Reason": "Reason 103: Unknown technologies detected: Standard",
                        "KG Version": "1.0.4"
                    }
                ]
            },
            {
                "id": 2,
                "name": "unique_tech_stack_2",
                "type": "unique",
                "tech_stack": [
                    "MVS|*",
                    "Unix|*",
                    "Java|*"
                ],
                "num_elements": 1,
                "apps": [
                    {
                        "Name": "App 4",
                        "Desc": "", "Cmpt": "",
                        "OS": {"AIX": {"standard_name": "Unix|AIX", "detected_version": "NA_VERSION",
                                       "latest_known_version": "NA_VERSION"},
                               "zOS": {"standard_name": "MVS|z/OS", "detected_version": "NA_VERSION",
                                       "latest_known_version": "NA_VERSION"}},
                        "Lang": {"Java": {"standard_name": "Java|*", "detected_version": "NA_VERSION",
                                          "latest_known_version": "21"}},
                        "App Server": {}, "Dependent Apps": {}, "Runtime": {}, "Libs": {}, "Reason": "",
                        "KG Version": "1.0.4"
                    }
                ]
            },
            {
                "id": 3,
                "name": "unique_tech_stack_3",
                "type": "unique",
                "tech_stack": [
                    "Windows|*",
                    "C#",
                    "Active Server Pages (ASP)"
                ],
                "num_elements": 1,
                "apps": [
                    {
                        "Name": "App 3",
                        "Desc": "", "Cmpt": "",
                        "OS": {"Windows": {"standard_name": "Windows|*", "detected_version": "NA_VERSION",
                                           "latest_known_version": "NA_VERSION"}},
                        "Lang": {
                            "ASP.net": {"standard_name": "Active Server Pages (ASP)", "detected_version": "NA_VERSION",
                                        "latest_known_version": "3"},
                            "C#": {"standard_name": "C#", "detected_version": "NA_VERSION",
                                   "latest_known_version": "NA_VERSION"}},
                        "App Server": {}, "Dependent Apps": {}, "Runtime": {}, "Libs": {}, "Reason": "",
                        "KG Version": "1.0.4"
                    }
                ]
            }
        ]

        pAppL = cluster.output_to_ui_clustering(appL)

        assert pAppL == expected
