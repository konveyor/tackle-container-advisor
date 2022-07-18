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

import os
import json
from collections import OrderedDict
import logging
from service.utils import Utils

import configparser

config = configparser.ConfigParser()
common = os.path.join("config", "common.ini")
kg = os.path.join("config", "kg.ini")
config.read([common, kg])


class Clustering():
    """
    This class for containerize Clustering
    """

    def __init__(self):
        """
            Init method for Clustering Class
            Setting up the logging level as info and opens logfile in write mode to capture the logs in text file
         """

    def output_to_ui_assessment(self, appL):
        """
        output_to_ui assessment methods takes the final assessed data as input and formats it & keeps
         only required fields and returns it as output assessment response

        """
        pAppL = []
        print('ok here!')
        try :
            for app in appL:



                # Order dictionry to fix the order of columns in the output
                pApp = OrderedDict()


                # Raw Fields
                pApp['Name'] = ''
                if 'Name' in app:
                    pApp['application_name'] = app["Name"]

                pApp['application_description'] = ''
                if 'Desc' in app:
                    pApp['application_description'] = app["Desc"]

                pApp['component_name'] = ''
                if 'Cmpt' in app:
                    pApp['component_name'] = app["Cmpt"]


                # Curated
                pApp['OS'] = eval(app["OS"])
                pApp['Lang'] = eval(app["Lang"])
                pApp["App Server"] = eval(app["App Server"])
                pApp["App"] = eval(app["Dependent Apps"])
                pApp["Runtime"] = eval(app["Runtime"])
                pApp["Lib"] = eval(app["Libs"])

                pApp['assessment_reason'] = app['Reason']

                try :
                    pApp["KG Version"] = app["KG Version"]
                except :
                    pApp["KG Version"] = 'Not Available'


                pAppL.append(pApp)

            return pAppL

        except Exception as e:
            logging.error(str(e))


    def output_to_ui_clustering(self, appL):
        """
        output_to_ui clustering methods takes the final assessed data as input and formats it & keeps
         only required fields and returns it as output assessment response

        """
        pAppL = []
        for app in appL:

            print(app)

            # Order dictionry to fix the order of columns in the output
            pApp = OrderedDict()

            # Raw Data
            pApp['Name'] = ''
            if 'application_name' in app:
                pApp['Name'] = app["application_name"]
            pApp['Desc'] = ''
            if 'application_description' in app:
                pApp['Desc'] = app["application_description"]
            pApp['Cmpt'] = ''
            if 'component_name' in app:
                pApp['Cmpt'] = app["component_name"]

            # AI Insights
            pApp["Ref Dockers"] = ""
            pApp["Confidence"] = 0

            # pAppL['Clusters'].append(pApp)
            pAppL.append(pApp)

        return pAppL
