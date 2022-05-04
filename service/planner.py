# *****************************************************************
# Copyright IBM Corporation 2022
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
import time
from datetime import datetime
import traceback
import configparser

from service.containerize_assessment import Assessment
from service.infer_tech import InferTech
from service.containerize_planning import Plan
from entity_standardizer.tfidf import TFIDF
from service.version_detector import version_detector

class Planner:
    def __init__(self):
        """
        Init method for planner class
        Create instances for EntityDetection & Assessment classes
        Set default values for token based variables
        """
        self.inferTech = InferTech()
        self.assess = Assessment()
        self.plan = Plan()

        self.config  = configparser.ConfigParser()
        common       = os.path.join("config", "common.ini")
        kg           = os.path.join("config", "kg.ini")
        self.config.read([common, kg])

        self.is_disable_access_token = None
        if 'is_disable_access_token' in self.config['RBAC']:
            self.is_disable_access_token = self.config['RBAC']['is_disable_access_token']
            
        logger = logging.getLogger()
        ch = logger.handlers[0]
        formatter = logging.Formatter("[%(asctime)s] %(name)s:%(levelname)s in %(filename)s:%(lineno)s - %(message)s")
        ch.setFormatter(formatter)

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

    def version_standardizer(self, mention, entity):
        na_version = self.config['NA_VALUES']['NA_VERSION']
        vd = version_detector()
        version = vd.get_version_strings(mention.lower())
        std_version = vd.get_standardized_version(vd, entity, version)
        final_version = (version,std_version)
        if std_version != na_version:
            logging.info(f"Mention = {mention}, Entity = {entity}, Version = {version}, Std. version = {std_version}")
        return final_version

    def app_standardizer(self, app_data):
        """
        compose_app methods takes app_data as input, extracts mentions for entity standardization and
        version detection
        """
        __class_type_mapper = {}

        __tca_input_mapper = {
                                "application_name": "application_name",
                                "application_description": "application_description",
                                "component_name": "component_name",
                                "operating_system": "tech_stack",
                                "programming_languages": "tech_stack",
                                "middleware": "tech_stack",
                                "database": "tech_stack",
                                "integration_services_and_additional_softwares": "tech_stack",
                                "technology_summary": "tech_stack"
                            }
        
        class_type_mapper_filepath = os.path.join(self.config['general']['kg_dir'], self.config['filenames']['class_type_mapper'])
        if os.path.exists(class_type_mapper_filepath):
            with open(class_type_mapper_filepath, 'r') as f:
                __class_type_mapper = json.load(f)            
        else:
            __class_type_mapper = {}
            logging.error(f'class_type_mapper[{class_type_mapper_filepath}] is empty or not exists')
        
        HIGH_THRESHOLD=float(self.config['Thresholds']['HIGH_THRESHOLD'])
        MEDIUM_THRESHOLD=float(self.config['Thresholds']['MEDIUM_THRESHOLD'])

        if len(__tca_input_mapper) == 0 or len(__class_type_mapper) == 0:
            logging.error('ontologies init failed')
            return app_data
        
        if (not app_data)  or len(app_data) == 0:
            return app_data
        
        general_term_key = 'Technology'

        mentions  = []
        id_to_app = {}
        for idx, app in enumerate(app_data):
            id_to_app[idx] = app
            for header in app:
                if __tca_input_mapper.get(header, 'NA') == 'tech_stack' and app[header] and str(app[header]).lower() not in ['na', 'null', 'string', 'none']:
                    num_mentions = len(mentions)
                    mentions.append({"app_id": idx, "mention_id": num_mentions, "mention": str(app[header])})

            app["KG Version"] = __class_type_mapper['kg_version']
            for x in set(__class_type_mapper['mappings'].values()):
                app[x] = {}

        headers = {'Accept': 'application/json', 'Content-Type': 'application/json'}
        resp = requests.post("http://localhost:8000/entity-standardizer", data=json.dumps(mentions), headers=headers)
        if resp.status_code != 201:
            logging.error(f"Response code {resp.status_code} received from entity-standardizer.")
        else:
            mentions = resp.json()["result"]
            for mention_data in mentions:
                mention_id  = mention_data["mention_id"]
                mention     = mention_data["mention"]
                app_id      = mention_data["app_id"]
                entity_names= mention_data["entity_names"]
                entity_types= mention_data["entity_types"]
                conf_scores = mention_data["confidence"]
                versions    = mention_data["versions"]
                app         = id_to_app[app_id]
                low_medium_confidence = app.get('low_medium_confidence', {})
                unknown               = app.get('unknown', [])

                if len(entity_names) > 1:
                    ##low medium confidence
                    obj = {}
                    for entity, version, score in zip(entity_names, versions, conf_scores):
                        if __class_type_mapper['mappings'][entity] == general_term_key:
                            ## Technology
                            if mention not in app[general_term_key]:
                                app[general_term_key][mention] = {}
                            app[general_term_key][mention][entity] = version
                        elif score >= HIGH_THRESHOLD:
                            # logging.error(f'snippet confidence wrong:{s} category:{category} confidence:{str(sim)}')
                            # continue
                            # only keep first one
                            if mention not in app[__class_type_mapper['mappings'][entity]]:
                                app[__class_type_mapper['mappings'][entity]][mention] = {}
                                app[__class_type_mapper['mappings'][entity]][mention][entity] = version
                                break
                        else:
                            obj[entity] = version
                    if obj:
                        low_medium_confidence[mention] = obj
                elif len(entity_names) == 1:
                    entity = entity_names[0]
                    score  = conf_scores[0]
                    version= versions[0]
                    if __class_type_mapper['mappings'][entity] == general_term_key:
                        ## Technology
                        if mention not in app[general_term_key]:
                            app[general_term_key][mention] = {}
                        app[general_term_key][mention][entity] = version
                    else:
                        if score >= HIGH_THRESHOLD:
                            if mention not in app[__class_type_mapper['mappings'][entity]]:
                                app[__class_type_mapper['mappings'][entity]][mention] = {}
                            app[__class_type_mapper['mappings'][entity]][mention][entity] = version
                        else:
                            # low or medium confidence
                            if mention not in low_medium_confidence:
                                low_medium_confidence[mention] = {}
                            low_medium_confidence[mention][entity] = version
                elif len(entity_names) == 0:
                    unknown.append(mention)
                if low_medium_confidence:
                    app['low_medium_confidence'] = low_medium_confidence
                if unknown:
                    app['unknown'] = unknown
        return app_data

    def entity_standardizer(self,auth_url,headers,auth_headers,app_data):
        """
        Invokes detect_access_token for accesstoken validation and if it's valid, it will call
        entity_standardizer to get standardized name and type.
        """
        try:
            resp, code, is_valid = self.detect_access_token(auth_url,headers,auth_headers)
            if not is_valid:
                return resp, code
            mentions = {}  # Holds all mentions as pointers to unique mention
            menhash  = {}  # Maps mention string to unique mention id
            uniques  = {}  # Holds unique mentions
            appid    = {}  # Holds mapping of mention_id -> app_id 
            for mention_data in app_data:        
                app_id     = mention_data.get("app_id", None)    
                mention_id = mention_data.get("mention_id", None)
                mention_name = mention_data.get("mention", "")
                if mention_name.lower() not in ['na', 'null', 'string', 'none']:
                    appid[mention_id] = app_id
                    if mention_name in menhash:
                        mentions[mention_id] = uniques[menhash[mention_name]]
                    else:
                        ulen                  = len(uniques)
                        menhash[mention_name] = ulen                        
                        uniques[ulen] = {"mention": mention_name}
                        mentions[mention_id] = uniques[ulen]
        except Exception as e:
            logging.error(str(e))
            track = traceback.format_exc()
            return dict(status = 400,message = 'Input data format doesn\'t match the format expected by TCA'), 400

        if not uniques:
            dict(status=201, message="Entity standardization completed successfully!", result=list(mentions.values())), 201

        try:
            kg_dir = self.config["general"]["kg_dir"]
            entities_json = self.config["tca"]["entities"]
            high_threshold= float(self.config["Thresholds"]["HIGH_THRESHOLD"])
            medium_threshold= float(self.config["Thresholds"]["MEDIUM_THRESHOLD"])
            na_category=self.config['NA_VALUES']['NA_CATEGORY']
            na_version = self.config['NA_VALUES']['NA_VERSION']
        except KeyError as k:
            logging.error(f'{k} is not a key in your common.ini file.')
            return dict(status = 500,message = 'TCA application error'), 500

        # Check that kg contains entities file
        entity_file_name = os.path.join(kg_dir, entities_json)
        if not os.path.isfile(entity_file_name):
            logging.error(f"Entities json file {entity_file_name} does not exist. Run kg generator to create this file.")
            return dict(status = 500,message = 'TCA application error'), 500

        # Get mapping of entity id to entity names
        with open(entity_file_name, 'r', encoding='utf-8') as entity_file:
            entities = json.load(entity_file)
        entity_data = {}
        for idx, entity in entities["data"].items():
            entity_name = entity["entity_name"] 
            tca_id      = entity["entity_id"]
            entity_type_name = entity["entity_type_name"]
            entity_data[tca_id] = (entity_name, entity_type_name)

        infer_data = {"label_type": "int", "label": "entity_id", "data_type": "strings", "data": uniques}
        
        tfidf            = TFIDF("deploy")
        tfidf_start      = time.time()
        tfidf_data       = tfidf.infer(infer_data)
        tfidf_end        = time.time()
        tfidf_time       = (tfidf_end-tfidf_start)
        entities         = {}
        mention_data     = tfidf_data.get("data", {})

        for idx, mention in mention_data.items():
            mention_name= mention.get("mention", "")
            predictions = mention.get("predictions", [])
            if not predictions:            
                logging.info(f"No predictions for {mention}")
                continue
            entity_names= [entity_data[p[0]][0] for p in predictions if p[1] > medium_threshold]
            entity_types= [entity_data[p[0]][1] for p in predictions if p[1] > medium_threshold]
            conf_scores = [round(p[1],2) for p in predictions if p[1] > medium_threshold]
            mention["entity_names"] = entity_names
            versions    = []
            for entity in entity_names:
                version  = self.version_standardizer(mention_name, entity)
                if version[1] == na_version:
                    versions.append('')
                else:
                    versions.append(version[1])
            mention["entity_types"] = entity_types
            mention["confidence"]   = conf_scores
            mention["versions"]     = versions
            del mention["predictions"]
        
        import copy
        for idx in mentions:
            mentions[idx] = copy.deepcopy(mentions[idx])
            mentions[idx]["mention_id"] = idx
            if appid[idx] is not None:
                mentions[idx]["app_id"] = appid[idx]
        return dict(status=201, message="Entity standardization completed successfully!", result=list(mentions.values())), 201

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
            
            # appL = self.compose_app(app_data)
            appL = self.app_standardizer(app_data)
            appL = self.assess.app_validation(appL)
            # Generate output for UI
            assessment = self.assess.output_to_ui_assessment(appL)
            logging.info(f'{str(datetime.now())} output assessment num: {str(len(assessment))} ')
            return dict(status=201, message="Assessment completed successfully!", assessment=assessment), 201
        except Exception as e:
            logging.error(str(e))
            track = traceback.format_exc()
            return dict(status = 400,message = 'Input data format doesn\'t match the format expected by TCA'), 400

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
            appL = self.inferTech.infer_missing_tech(appL)
            appL = self.plan.validate_app(appL)
            containerL = self.plan.map_to_docker(appL, catalog)
            planning = self.plan.output_to_ui_planning(containerL)

            logging.info(f"output planning num: {str(len(planning))}")
            return dict(status=201, message="Container recommendation generated!", containerization=planning), 201

        except Exception as e:
            logging.error(str(e))
            track = traceback.format_exc()
            return dict(status=400, message='Input data format doesn\'t match the format expected by TCA'), 400

def do_standardization(auth_url,headers,auth_headers,app_data):
    """
    Creates the instance for Planner Class and invoke containerization_plan method
    """
    # global controller
    controller = None
    if not controller:
        controller = Planner()
    resp, code = controller.entity_standardizer(auth_url,headers,auth_headers,app_data)

    return resp, code
    
    
def do_assessment(auth_url,headers,auth_headers,app_data):
    """
    Creates the instance for Planner Class and invoke containerization_plan method
    """
    # global controller
    controller = None
    if not controller:
        controller = Planner()
    resp, code = controller.containerization_assessment(auth_url,headers,auth_headers,app_data)

    return resp, code

def do_plan(auth_url,headers,auth_headers,assessment_data,catalog):
    """
    Creates the instance for Planner Class and invoke containerization_plan method
    """
    # global controller
    controller = None
    if not controller:
        controller = Planner()
    resp, code = controller.containerization_plan(auth_url,headers,auth_headers,assessment_data,catalog)

    return resp, code