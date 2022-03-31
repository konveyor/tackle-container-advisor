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
import sys
import shutil
import logging
import requests
import flask
from datetime import datetime
import traceback

from service.entity_detection import EntityDetection
from service.containerize_assessment import Assessment
from service.infer_tech import InferTech
from service.containerize_planning import Plan
import configparser
from service.multiprocessing_mapreduce import SimpleMapReduce


config = configparser.ConfigParser()
common = os.path.join("config", "common.ini")
kg     = os.path.join("config", "kg.ini")
config.read([common, kg])

controller = None



class Planner:
    def __init__(self):
        """
        Init method for planner class
        Create instances for EntityDetection & Assessment classes
        Set default values for token based variables
        """
        self.entity_detection = EntityDetection()
        self.inferTech = InferTech()
        self.assess = Assessment()
        self.plan = Plan()
        # logging.warn(f'auth_url: {auth_url}')

        self.is_disable_access_token = None
        if 'is_disable_access_token' in config['RBAC']:
            self.is_disable_access_token = config['RBAC']['is_disable_access_token']

    def detect_access_token(self,auth_url,headers,auth_headers):
        """
        detect_access_token checks if the access_token is enabled or disabled. If it's enabled, it will validate
        the accesstoken in auth_headers in RBAC
        """
        is_valid = False
        if self.is_disable_access_token and (self.is_disable_access_token.lower() == 'yes' or self.is_disable_access_token.lower() == 'true'):
            is_valid = True
        if not is_valid:
            if (not auth_url) or (not auth_url.startswith('http')):
                return dict(status = 500,message = 'Internal Server Error, missing or wrong config of RBAC access token validation url'), 500, is_valid
            accesstoken = None
            if 'Accesstoken' in headers:
                accesstoken = headers['Accesstoken']
            if not accesstoken and 'accesstoken' in headers:
                accesstoken = headers['accesstoken']
            if not accesstoken:
                return dict(status = 401, message = 'Unauthorized, missing or invalid access token'), 401, is_valid
            req_headers = auth_headers.copy()
            req_headers['accesstoken'] = accesstoken
            if self.is_enable_default_token and (self.is_enable_default_token.lower() == 'yes' or self.is_enable_default_token.lower() == 'true') and self.aca_default_token and accesstoken.lower() == self.aca_default_token.lower():
                is_valid = True
        if not is_valid:
            try:
                auth_response = requests.get(auth_url, headers = req_headers, verify=False)
                if auth_response.status_code == requests.codes.ok: #pylint: disable=no-member
                    try:
                        auth_response_json = auth_response.json()
                        if auth_response_json and auth_response_json['isAuthorized'] == 'Y':
                            is_valid = True
                        else:
                            logging.warn(f'access token response json: {json.dumps(auth_response_json)}')
                    except ValueError:
                        logging.error(f'access token response error: {auth_response}')
            except Exception as e:
                print(e)

        if not is_valid:
            return dict(status = 401, message = 'Unauthorized, missing or invalid access token'), 401, is_valid
        
        return dict(), 201, is_valid


    def compose_app(self, app_data):
        """
        compose_app methods takes app_data as input and split into batch with batch size 20000 and invoke compose_app
        method in entity_detection class to start the assessment process
        """
        try:
            threhold = 20000
            num = round(len(app_data)/threhold + 0.5)
            if num > 1:
                logging.warn(f'{str(datetime.now())} input app num: {str(len(app_data))} and split into {str(num)}')
            else:
                logging.warn(f'{str(datetime.now())} input app num: {str(len(app_data))}')
            appL = []
            for x in range(1, num+1):
                if num > 1:
                    logging.warn(f'split round: {str(x)}')
                begin = threhold * (x-1)
                end = threhold * x
                if end > len(app_data):
                    end = len(app_data)

                appl = app_data[slice(begin, end)]
                if config['Performance']['multiprocessing_enabled'] == "YES":
                    print("MULTIPROCESSING ENABLED==YES")
                    mapper = SimpleMapReduce(self.map_apps, self.reduce_apps)
                    appl = mapper(appl)
                    appl = self.multiprocessing_to_single_app_data(appl)

                else:
                    print("MULTIPROCESSING ENABLED==NO")
                    appl = self.entity_detection.compose_app(appl)
                
                print("appL = ", appL)
                appL.extend(appl)
            
            return appL
        except Exception as e:
            logging.error(str(e))
            raise e

    def containerization_assessment(self,auth_url,headers,auth_headers,app_data):
        """
        Invokes detect_access_token for accesstoken validation and if it's valid, it will call
        compose_app for assessment and app_validation for validation the assessed application data
        and finally call output_to_ui_assessment to return the formatted assessment data
        """
        try:
            resp, code, is_valid = self.detect_access_token(auth_url,headers,auth_headers)
            if not is_valid:
                return resp, code

            
            appL = self.compose_app(app_data)
            appL = self.assess.app_validation(appL)

            # Generate output for UI
            assessment = self.assess.output_to_ui_assessment(appL)

            logging.warn(f'{str(datetime.now())} output assessment num: {str(len(assessment))} ')
            return dict(status=201, message="Assessment completed successfully!", assessment=assessment), 201


        except Exception as e:
            # print(e)
            logging.error(str(e))
            track = traceback.format_exc()
            print(track)
            return dict(status = 400,message = 'Input data format doesn\'t match the format expected by ACA'), 400

    def containerization_plan(self, auth_url, headers, auth_headers, assessment_data,catalog):
        """
        Invokes detect_access_token for accesstoken validation and if it's valid, it will call
        compose_app for assessment and app_validation for validation the assessed application data
        and finally call output_to_ui_assessment to return the formatted assessment data
        """
        try:
            resp, code, is_valid = self.detect_access_token(auth_url, headers, auth_headers)
            if not is_valid:
                return resp, code


            appL = self.plan.ui_to_input_assessment(assessment_data)
            print(str(appL))
            appL = self.inferTech.infer_missing_tech(appL)
            print(str(appL))
            appL = self.plan.validate_app(appL)
            containerL = self.plan.map_to_docker(appL, catalog)
            planning = self.plan.output_to_ui_planning(containerL)

            logging.warn(f'{str(datetime.now())} output planning num: {str(len(planning))}')
            return dict(status=201, message="Container recommendation generated!", containerization=planning), 201

        except Exception as e:
            logging.error(str(e))
            track = traceback.format_exc()
            print(track)
            return dict(status=400, message='Input data format doesn\'t match the format expected by ACA'), 400


    def map_apps(self, app_data):

        """
        Creates a mapper from the input app_data for multiprocessing. Processes the data and send it to the reducer.
        """

        apps = []
        index = 0
        app_data = self.entity_detection.compose_app([app_data])
        apps.append((json.dumps(app_data),1))
        index+=1
        return apps
    
    def reduce_apps(self, apps):
        """
        Creates a reducer to merge all processed data together to generate one final output.
        """
        key, total = apps
        return (key, sum(total))
        #return apps
            
    def multiprocessing_to_single_app_data(self, app_data):
        """
        Preprocess the data from the reducer to generate the data required for processing next steps in TCA.
        """
        apps = []
        for app in app_data:
            app_str=json.loads(app[0])
            apps.append(app_str[0])
        
        return apps

    
    
def do_assessment(auth_url,headers,auth_headers,app_data):
    """
    Creates the instance for Planner Class and invoke containerization_plan method
    """
    global controller
    if not controller:
        controller = Planner()
    resp, code = controller.containerization_assessment(auth_url,headers,auth_headers,app_data)

    return resp, code

def do_plan(auth_url,headers,auth_headers,assessment_data,catalog):
    """
    Creates the instance for Planner Class and invoke containerization_plan method
    """
    global controller
    if not controller:
        controller = Planner()
    resp, code = controller.containerization_plan(auth_url,headers,auth_headers,assessment_data,catalog)

    return resp, code


def get_supported_metamodels():
    """
        Creates the instance for Planner Class and get the keys for aca_input_mapper in entity_detection class
    """
    global controller
    if not controller:
        controller = Planner()
    return controller.entity_detection.get_aca_input_mapper().keys()
