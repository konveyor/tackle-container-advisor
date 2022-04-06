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
import logging
import codecs


from service.utils import Utils
from entity_standardizer.tfidf import utils
from service.standardizer import standardizer

import configparser

config = configparser.ConfigParser()
common = os.path.join("config", "common.ini")
kg     = os.path.join("config", "kg.ini")
config.read([common, kg])

class EntityDetection:


    def __init__(self, logger=False):
        """
        Init method for EntityDetection class.
        Initializes the tca_input_mapper with predefined set of key and values and loads class_type_mapper by reading
        class_type_mapper.json in ontologies folder.
        Also, sets the default values for category, version, high & low thresholds
        """
        logging.basicConfig(level=logging.INFO)

        # self.version_detector = version_detector()

        #self.cipher_obj = AESCipher()
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
        
        class_type_mapper_filepath = os.path.join(config['general']['kg_dir'], config['filenames']['class_type_mapper'])
        if os.path.exists(class_type_mapper_filepath):
            with open(class_type_mapper_filepath, 'r') as f:
                self.__class_type_mapper = json.load(f)
            
        else:
            self.__class_type_mapper = {}
            logging.error(f'class_type_mapper[{class_type_mapper_filepath}] is empty or not exists')
        
        # self.__sim = sim_applier()

        self.NA_CATEGORY=config['NA_VALUES']['NA_CATEGORY']
        self.NA_VERSION = config['NA_VALUES']['NA_VERSION']

        self.HIGH_THRESHOLD=float(config['Thresholds']['HIGH_THRESHOLD'])
        self.MEDIUM_THRESHOLD=float(config['Thresholds']['MEDIUM_THRESHOLD'])


    def entity_detector(self,tech_stack):
        """
        entity_detector methods takes the input entity, preprocess it and detects its standardized form and version with
        confidence score
        """
        '''
        try:
            strs = utils.preprocess(tech_stack)  # utils.split_subtext(tech_stack)
            id_ = 0
            # Return all unique matches
            entities = []  # set()
            for s in strs:
                s = s.strip()

                entity_scores = self.__sim.tech_stack_standardization(s.lower())
                version = self.version_detector.get_version_strings(s.lower())
                std_version = self.version_detector.get_standardized_version(self.version_detector, entity_scores[0], version)
                final_version = (version,std_version)
                entities.append([s, entity_scores, final_version])

            print("Original entities = ", entities)
            # return entities        
        except Exception as e:
            logging.error(str(e))
        '''
        mentions = utils.preprocess(tech_stack)        
        entities = standardizer(mentions)
        
        return entities

    def compose_app(self,app_data):
        """
        Checks if the ontologies and model objects are loaded properly and preprocess the input tech stack.
        Call entity_detection method to get the respective standardized form with version and confidence score.
        Using the confidence score, low or medium confidence scored entities are separated out. Using class_type_mapper,
        general and unknown technologies are added separately in assessment data.

        """
        if len(self.__tca_input_mapper) == 0 or len(self.__class_type_mapper) == 0:
            logging.error('ontologies init failed')
            return app_data
        
        # if (not self.__sim.all_instances) or len(self.__sim.all_instances) == 0:
        # logging.error('apply_sim init failed')
        # return app_data

        if (not app_data)  or len(app_data) == 0:
            return app_data
        
        general_term_key = 'Technology'

        try:
            for app in app_data:
                tech_stack = ''
                for header in app:
                    if self.__tca_input_mapper.get(header, 'NA') == 'tech_stack' and app[header] and str(
                            app[header]).lower() not in ['na', 'null', 'string', 'none']:
                        if tech_stack:
                            tech_stack = tech_stack + ', ' + str(app[header])
                        else:
                            tech_stack = str(app[header])
                if not tech_stack:
                    continue
                tech_stack = Utils.preprocess_tech_stack_for_sim(tech_stack)
                entities = self.entity_detector(tech_stack)
                if not entities or len(entities) == 0:
                    continue

                app["KG Version"] = self.__class_type_mapper['kg_version']

                for x in set(self.__class_type_mapper['mappings'].values()):
                    app[x] = {}


                low_medium_confidence = {}
                unknown = []
                for element in entities:
                    s, entity_scores, version = element
                    if version == self.NA_VERSION:
                        version = ''
                    if len(entity_scores) > 1:
                        ##low medium confidence
                        obj = {}
                        for category, sim in entity_scores:
                            if category == self.NA_CATEGORY:
                                logging.error(f'snippet category wrong:{s}')
                                continue
                            if self.__class_type_mapper['mappings'][category] == general_term_key:
                                ## Technology
                                if s not in app[general_term_key]:
                                    app[general_term_key][s] = {}
                                app[general_term_key][s][category] = version
                            elif sim >= self.HIGH_THRESHOLD:
                                # logging.error(f'snippet confidence wrong:{s} category:{category} confidence:{str(sim)}')
                                # continue
                                # only keep first one
                                if s not in app[self.__class_type_mapper['mappings'][category]]:
                                    app[self.__class_type_mapper['mappings'][category]][s] = {}
                                app[self.__class_type_mapper['mappings'][category]][s][category] = version
                                break
                            else:
                                obj[category] = version
                        if obj:
                            low_medium_confidence[s] = obj
                    elif len(entity_scores) == 1:
                        category, sim = entity_scores[0]
                        if category == self.NA_CATEGORY:
                            unknown.append(s)
                        elif self.__class_type_mapper['mappings'][category] == general_term_key:
                            ## Technology
                            if s not in app[general_term_key]:
                                app[general_term_key][s] = {}
                            app[general_term_key][s][category] = version
                        else:
                            if sim >= self.HIGH_THRESHOLD:
                                if s not in app[self.__class_type_mapper['mappings'][category]]:
                                    app[self.__class_type_mapper['mappings'][category]][s] = {}
                                app[self.__class_type_mapper['mappings'][category]][s][category] = version
                            else:
                                # low or medium confidence
                                if s not in low_medium_confidence:
                                    low_medium_confidence[s] = {}
                                low_medium_confidence[s][category] = version
                if low_medium_confidence:
                    app['low_medium_confidence'] = low_medium_confidence
                if unknown:
                    app['unknown'] = unknown
            return app_data

        except Exception as e:
            logging.error(str(e))


    def get_tca_input_mapper(self):
        """ Fetches the tca_input_mapper predefined values which act as sample input"""
        return self.__tca_input_mapper



