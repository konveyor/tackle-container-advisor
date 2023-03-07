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
import sys
import shutil
import logging
import requests
import flask
import time
from datetime import datetime
import traceback
import configparser

from service.standardization import Standardization
from service.assessment import Assessment
from service.planning import Plan
from service.infer_tech import InferTech
from service.clustering import Clustering

class Functions:
    def __init__(self, catalog = "dockerhub"):
        """
        Init method for planner class
        Create instances for EntityDetection & Assessment classes
        Set default values for token based variables
        """
        self.inferTech  = InferTech()
        self.standardize= Standardization()
        self.assess     = Assessment()
        self.plan       = Plan(catalog=catalog)
        self.cluster = Clustering()

        config  = configparser.ConfigParser()
        common       = os.path.join("config", "common.ini")
        config.read(common)

        self.is_disable_access_token = None
        if 'is_disable_access_token' in config['RBAC']:
            self.is_disable_access_token = config['RBAC']['is_disable_access_token']
            
        USER_LEVEL = os.getenv('LOGGING_LEVEL', 'INFO')
        level = logging.getLevelName(USER_LEVEL)
        logger = logging.getLogger()
        logger.setLevel(level)
        ch = logger.handlers[0]
        formatter = logging.Formatter("[%(asctime)s] %(name)s:%(levelname)s in %(filename)s:%(lineno)s - %(message)s")
        ch.setFormatter(formatter)
        print(f"Effective logging level is {logging.getLevelName(logger.getEffectiveLevel())}")

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
            if self.is_enable_default_token and (self.is_enable_default_token.lower() == 'yes' or self.is_enable_default_token.lower() == 'true') and self.tca_default_token and accesstoken.lower() == self.tca_default_token.lower():
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

    def standardization(self,auth_url,headers,auth_headers,app_data):
        """
        Invokes detect_access_token for accesstoken validation and if it's valid, it will call
        entity_standardizer to get standardized name and type.
        """
        try:
            resp, code, is_valid = self.detect_access_token(auth_url,headers,auth_headers)
            if not is_valid:
                return resp, code
            output = self.standardize.entity_standarizer(app_data)
            return dict(status=201, message="Standardization completed successfully!", standardization=output), 201
        except Exception as e:
            logging.error(str(e))
            track = traceback.format_exc()
            return dict(status = 400,message = 'Input data format doesn\'t match the format expected by TCA'), 400

    def assessment(self,auth_url,headers,auth_headers,app_data):
        """
        Invokes detect_access_token for accesstoken validation and if it's valid, it will call
        compose_app for assessment and app_validation for validation the assessed application data
        and finally call output_to_ui_assessment to return the formatted assessment data
        """
        try:
            resp, code, is_valid = self.detect_access_token(auth_url,headers,auth_headers)
            if not is_valid:
                return resp, code

            appL = self.standardize.app_standardizer(app_data)

            appL = self.assess.app_validation(appL)

            # Generate output for UI
            output = self.assess.output_to_ui_assessment(appL)
            logging.info(f'{str(datetime.now())} output assessment num: {str(len(output))} ')
            return dict(status=201, message="Standardization completed successfully!", standardized_apps=output), 201
        except Exception as e:
            logging.error(str(e))
            track = traceback.format_exc()
            return dict(status = 400,message = 'Input data format doesn\'t match the format expected by TCA'), 400

    def planning(self, auth_url, headers, auth_headers, assessment_data, catalog):
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
            appL = self.inferTech.infer_missing_tech(appL)
            appL = self.plan.validate_app(appL)
            containerL = self.plan.map_to_docker(appL, catalog)
            output = self.plan.output_to_ui_planning(containerL)

            logging.info(f"output planning num: {str(len(output))}")
            return dict(status=201, message="Container recommendation generated!", containerization=output), 201

        except Exception as e:
            logging.error(str(e))
            track = traceback.format_exc()
            return dict(status=400, message='Input data format doesn\'t match the format expected by TCA'), 400

    def clustering(self, auth_url, headers, auth_headers, app_data):
        """
        Invokes detect_access_token for accesstoken validation and if it's valid, it will call
        output_to_ui_clustering to return the formatted assessment data
        """
        try:
            resp, code, is_valid = self.detect_access_token(auth_url, headers, auth_headers)
            if not is_valid:
                return resp, code

            # Generate output for UI
            clusters = self.cluster.output_to_ui_clustering(app_data)
            logging.info(f'{str(datetime.now())} output clustering num: {str(len(clusters))} ')
            return dict(status=201, message="Clustering completed successfully!", clusters=clusters), 201
        except Exception as e:
            logging.error(str(e))
            track = traceback.format_exc()
            return dict(status=400, message='Input data format doesn\'t match the format expected by TCA'), 400

def do_standardization(auth_url,headers,auth_headers,app_data):
    """
    Creates the instance for Planner Class and invoke containerization_plan method
    """
    controller = None
    if not controller:
        controller = Functions()
    resp, code = controller.standardization(auth_url,headers,auth_headers,app_data)

    return resp, code
    
    
def do_assessment(auth_url,headers,auth_headers,app_data):
    """
    Creates the instance for Planner Class and invoke containerization_plan method
    """
    controller = None
    if not controller:
        controller = Functions()
    resp, code = controller.assessment(auth_url,headers,auth_headers,app_data)

    return resp, code

def do_planning(auth_url, headers, auth_headers, assessment_data, catalog):
    """
    Creates the instance for Planner Class and invoke containerization_plan method
    """
    controller = None
    if not controller:
        controller = Functions(catalog=catalog)
    resp, code = controller.planning(auth_url, headers, auth_headers, assessment_data, catalog)

    return resp, code

def do_clustering(auth_url, headers, auth_headers, assessment_data):
    """
    Creates the instance for Clustering Class and invoke clustering method
    """
    controller = None
    if not controller:
        controller = Functions()
    resp, code = controller.clustering(auth_url, headers, auth_headers, assessment_data)

    return resp, code