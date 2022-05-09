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
import time
import logging
import configparser

from entity_standardizer.tfidf import TFIDF
from service.version_detector import version_detector


class Standardization():
    """
    This class for entity, version, and app standardization
    """

    def __init__(self):
        """
            Init method for Standardization Class
        """
        config = configparser.ConfigParser()
        common = os.path.join("config", "common.ini")
        kg     = os.path.join("config", "kg.ini")
        config.read([common, kg])

        try:
            kg_dir                = config["general"]["kg_dir"]
            entities_json         = config["tca"]["entities"]
            self.high_threshold   = float(config["Thresholds"]["HIGH_THRESHOLD"])
            self.medium_threshold = float(config["Thresholds"]["MEDIUM_THRESHOLD"])
            na_category           = config['NA_VALUES']['NA_CATEGORY']
            self.na_version       = config['NA_VALUES']['NA_VERSION']
            class_type_mapper     = config['filenames']['class_type_mapper']
        except KeyError as k:
            logging.error(f'{k} is not a key in your common.ini or kg.ini file.')

        self.__class_type_mapper = {}

        self.__tca_input_mapper = {
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
        
        class_type_mapper_filepath = os.path.join(kg_dir, class_type_mapper)
        if os.path.exists(class_type_mapper_filepath):
            with open(class_type_mapper_filepath, 'r') as f:
                self.__class_type_mapper = json.load(f)            
        else:
            self.__class_type_mapper = {}
            logging.error(f'class_type_mapper[{class_type_mapper_filepath}] is empty or not exists')

        if len(self.__tca_input_mapper) == 0 or len(self.__class_type_mapper) == 0:
            logging.error('ontologies init failed')

        # Check that kg contains entities file
        entity_file_name = os.path.join(kg_dir, entities_json)
        if not os.path.isfile(entity_file_name):
            logging.error(f"Entities json file {entity_file_name} does not exist. Run kg generator to create this file.")

        # Get mapping of entity id to entity names
        with open(entity_file_name, 'r', encoding='utf-8') as entity_file:
            entities = json.load(entity_file)
        
        self.__entity_data = {}
        for idx, entity in entities["data"].items():
            entity_name = entity["entity_name"] 
            tca_id      = entity["entity_id"]
            entity_type_name = entity["entity_type_name"]
            self.__entity_data[tca_id] = (entity_name, entity_type_name)

    def entity_standardizer(self, mention_data):
        """
        Invokes detect_access_token for accesstoken validation and if it's valid, it will call
        entity_standardizer to get standardized name and type.
        """
        try:
            mentions = {}  # Holds all mentions as pointers to unique mention
            menhash  = {}  # Maps mention string to unique mention id
            uniques  = {}  # Holds unique mentions
            appid    = {}  # Holds mapping of mention_id -> app_id 
            for mention in mention_data:        
                app_id     = mention.get("app_id", None)    
                mention_id = mention.get("mention_id", None)
                mention_name = mention.get("mention", "")
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
            entity_names= [self.__entity_data[p[0]][0] for p in predictions if p[1] > self.medium_threshold]
            entity_types= [self.__entity_data[p[0]][1] for p in predictions if p[1] > self.medium_threshold]
            conf_scores = [round(p[1],2) for p in predictions if p[1] > self.medium_threshold]
            mention["entity_names"] = entity_names
            versions    = []
            for entity, score in zip(entity_names, conf_scores):
                version  = self.version_standardizer(mention_name, [entity, score])
                versions.append(version)
                # if version[1] == self.na_version:
                #    versions.append('')
                # else:
                #    versions.append(version[1])
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

        return list(mentions.values())

    def version_standardizer(self, mention, entity):
        vd = version_detector()
        version = vd.get_version_strings(mention.lower())
        std_version = vd.get_standardized_version(vd, entity, version)
        final_version = (version,std_version)
        if std_version != self.na_version:
            logging.debug(f"Mention = {mention}, Entity = {entity}, Version = {version}, Std. version = {std_version}")
        return final_version

    
    def app_standardizer(self, app_data):
        """
        app_standardizer methods takes app_data as input, extracts mentions for entity and
        version standardization followed by assessment of high, low, medium confidence and
        unknown technology data predictions
        """                
        if (not app_data)  or len(app_data) == 0:
            return app_data
        
        general_term_key = 'Technology'

        mentions  = []
        id_to_app = {}
        for idx, app in enumerate(app_data):
            id_to_app[idx] = app
            for header in app:
                if self.__tca_input_mapper.get(header, 'NA') == 'tech_stack' and app[header] and str(app[header]).lower() not in ['na', 'null', 'string', 'none']:
                    num_mentions = len(mentions)
                    mentions.append({"app_id": idx, "mention_id": num_mentions, "mention": str(app[header])})

            app["KG Version"] = self.__class_type_mapper['kg_version']
            for x in set(self.__class_type_mapper['mappings'].values()):
                app[x] = {}

        std_mentions = self.entity_standardizer(mentions)
        for mention_data in std_mentions:
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
                    if self.__class_type_mapper['mappings'][entity] == general_term_key:
                        ## Technology
                        if mention not in app[general_term_key]:
                            app[general_term_key][mention] = {}
                        app[general_term_key][mention][entity] = version
                    elif score >= self.high_threshold:
                        # logging.error(f'snippet confidence wrong:{s} category:{category} confidence:{str(sim)}')
                        # continue
                        # only keep first one
                        if mention not in app[self.__class_type_mapper['mappings'][entity]]:
                            app[self.__class_type_mapper['mappings'][entity]][mention] = {}
                            app[self.__class_type_mapper['mappings'][entity]][mention][entity] = version
                            break
                    else:
                        obj[entity] = version
                if obj:
                    low_medium_confidence[mention] = obj
            elif len(entity_names) == 1:
                entity = entity_names[0]
                score  = conf_scores[0]
                version= versions[0]
                if self.__class_type_mapper['mappings'][entity] == general_term_key:
                    ## Technology
                    if mention not in app[general_term_key]:
                        app[general_term_key][mention] = {}
                    app[general_term_key][mention][entity] = version
                else:
                    if score >= self.high_threshold:
                        if mention not in app[self.__class_type_mapper['mappings'][entity]]:
                            app[self.__class_type_mapper['mappings'][entity]][mention] = {}
                        app[self.__class_type_mapper['mappings'][entity]][mention][entity] = version
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
