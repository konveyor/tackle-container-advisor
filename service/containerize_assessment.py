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

import os
import json
from collections import OrderedDict
import logging
import codecs
from service.utils import Utils


import configparser

config = configparser.ConfigParser()
common = os.path.join("config", "common.ini")
kg     = os.path.join("config", "kg.ini")
config.read([common, kg])

class Assessment():
    """
    This class for containerize Assessment
    """

    def __init__(self, logger=False):
        """
            Init method for Assessment Class
            Setting up the logging level as info and opens logfile in write mode to capture the logs in text file
         """
        logging.basicConfig(level=logging.INFO)
        if logger == True:
            self.logfile = codecs.open('assessment.log','w',encoding='utf-8')


    def app_validation(self, appL):
        """
        app_validation method takes assessed input data and check if any low/medium confidence entities or
        general technology or unknown technology entities are present. If it's present, it will be added in assessment reason.
        """

        try:
            for app in appL:
                app['valid_assessment'] = True
                app['assessment_reason'] = []

                # Tech confidence
                if 'low_medium_confidence' in app and app['low_medium_confidence']:
                    app['assessment_reason'].append(config['Reason_Codes']['confidence_reason']+ ' ' + json.dumps(app['low_medium_confidence']))

                # General technology items
                if 'Technology' in app and app['Technology']:
                    app['assessment_reason'].append(config['Reason_Codes']['general_technology_reason'] + ' ' + json.dumps(app['Technology']))

                # Unknown technology items
                if 'unknown' in app and app['unknown']:
                    app['assessment_reason'].append(config['Reason_Codes']['unknown_technology_reason'] + ' ' + ', '.join(filter(None, app['unknown'])))

                app['assessment_reason'] = '\n'.join(app['assessment_reason'])

            return appL

        except Exception as e:
            logging.error(str(e))



    def output_to_ui_assessment(self, appL):
        """
        output_to_ui assessment methods takes the final assessed data as input and formats it & keeps
         only required fields and returns it as output assessment response

        """
        pAppL = []

        try :
            for app in appL:
                # Order dictionry to fix the order of columns in the output
                pApp = OrderedDict()

                # Raw Fields
                pApp['Name'] = ''
                if 'application_name' in app:
                    pApp['Name'] = app["application_name"]
                pApp['Desc'] = ''
                if 'application_description' in app:
                    pApp['Desc'] = app["application_description"]
                pApp['Cmpt'] = ''
                if 'component_name' in app:
                    pApp['Cmpt'] = app["component_name"]

                # Curated
                pApp['OS'] = app["OS"]
                pApp['Lang'] = app["Lang"]
                pApp["App Server"] = app["App Server"]
                pApp["Dependent Apps"] = app["App"]
                pApp["Runtime"] = app["Runtime"]
                pApp["Libs"] = app["Lib"]

                try :
                    pApp["KG Version"] = app["KG Version"]
                except :
                    pApp["KG Version"] = 'Not Available'

                pApp['Reason'] = app["assessment_reason"]

                pAppL.append(pApp)

            return pAppL

        except Exception as e:
            logging.error(str(e))
    
