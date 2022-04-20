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
import logging
from service.utils import Utils

import configparser

config = configparser.ConfigParser()
common = os.path.join("config", "common.ini")
kg     = os.path.join("config", "kg.ini")
config.read([common, kg])


class InferTech:
    def __init__(self):
        """
        Initialize and loads the class mapper and OS compatability KG json files
        """        
        class_type_mapper_filepath = os.path.join(config['general']['kg_dir'], config['filenames']['class_type_mapper'])

        if os.path.exists(class_type_mapper_filepath):
            with open(class_type_mapper_filepath, 'r') as f:
                self.__class_type_mapper = json.load(f)
        else:
            self.__class_type_mapper = {}
            logging.error(f'class_type_mapper[{class_type_mapper_filepath}] is empty or not exists')
        
        compatibilityOSKG_filepath = os.path.join(config['general']['kg_dir'], config['filenames']['compatibilityOSKG'])

        if os.path.exists(compatibilityOSKG_filepath):
            with open(compatibilityOSKG_filepath, 'r') as f:
                self.__compatibilityOSKG = json.load(f)
        else:
            self.__compatibilityOSKG = {}
            logging.error(f'compatibilityOSKG[{compatibilityOSKG_filepath}] is empty or not exists')    

    def __identify_parent_OS(self, child):
        """
        Identify the appropriate  parent operating System
        """
        child_class_variants = [child, child+'|*']
        candidate_OS = []
        for child_class in child_class_variants:
            if child_class in self.__compatibilityOSKG:
                candidate_OS.extend(self.__compatibilityOSKG[child_class])
        return candidate_OS


    def __reduce_to_base_OS(self, os_list):
        """
        Reduce the OS to base forms
        """
        final_os = []
        if os_list:
            for os in os_list:
                if '|' in os:
                    final_os.append(os.split('|')[0])
                else:
                    final_os.append(os)
        return list(set(final_os))

    ## Update the list of recommended OS
    def __update_recommended_OS(self, candidate_OS, recommended_OS):
        """
        Updates the list of recommended OS
        """
        if not recommended_OS or len(recommended_OS) == 0:
            return recommended_OS
        if not candidate_OS or len(candidate_OS) == 0:
            return []
        if not set(recommended_OS).intersection(set(candidate_OS)):
            reduced_candidate_OS = self.__reduce_to_base_OS(list(candidate_OS))
            if not set(recommended_OS).intersection(set(reduced_candidate_OS)):
                # recommended_OS = recommended_OS.union(set(candidate_OS))
                reduced_recommended_OS = self.__reduce_to_base_OS(list(recommended_OS))
                if not set(reduced_recommended_OS).intersection(set(reduced_candidate_OS)):
                    return []
                else:
                    return list(set(reduced_recommended_OS).intersection(set(reduced_candidate_OS)))
            else:
                recommended_OS = list(set(recommended_OS).intersection(set(reduced_candidate_OS)))
        else:
            recommended_OS = list(set(recommended_OS).intersection(set(candidate_OS)))
        return recommended_OS

    def __get_candidate_OS(self, app_tech):
        '''
        Calls identify_parent_os method to figure out the parent operating system for the given technology
        '''
        tech_list = app_tech.split(', ')
        candidate_OS = []
        for tech in tech_list:
            candidate_OS.extend(self.__identify_parent_OS(tech))
        return candidate_OS
    
    def __check_OS_compatible(self, candidate_OS, input_OS):
        """
        Checks the OS compatibility between input operating system and identified operating system for given tech.
        """
        if not candidate_OS or len(candidate_OS) == 0 or not input_OS or len(input_OS) == 0:
            return False
        if not set(candidate_OS).intersection(set(input_OS)):
            reduced_candidate_OS = self.__reduce_to_base_OS(list(candidate_OS))
            reduced_input_OS = self.__reduce_to_base_OS(input_OS)
            if set(reduced_candidate_OS).intersection(set(reduced_input_OS)):
                return True
            else:
                return False
        else:
            return True


    def infer_missing_tech(self, appL):
        """
        Infers the missing technology and checks OS compatibility
        """
        if len(self.__compatibilityOSKG) == 0 or len(self.__class_type_mapper) == 0:
            logging.error('infer_tech init failed')
            return appL
        if (not appL) or len(appL) == 0:
            return appL
        for app in appL:

            for x in set(self.__class_type_mapper['mappings'].values()):
                if x not in app:
                    app[x] = {}
            ## Missing technology inference

            app['Inferred'] = {'Lang':[],'App':[], 'App Server':[], 'Runtime':[], 'OS':[]}
            app['Recommended OS'] = ''

            ## Infer Language from Lib if language is missing
            ## If a lib supports multiple langages, we do not infer the language
            if app['Lib']:
                for snippet, obj in app['Lib'].items():
                    if not obj:
                        continue
                    for tech, version in obj.items():
                        if '|' in tech:
                            inferred_tech = tech.split('|')[0]
                            app_lang = Utils.getEntityString(app['Lang']).split(', ')
                            if inferred_tech not in app_lang:
                                if snippet not in app['Lang']:
                                    app['Lang'][snippet] = {}
                                app['Lang'][snippet][inferred_tech] = version
                                app['Inferred']['Lang'].append(inferred_tech)

            # Infer App from Plugin if App is missing
            ## If a plugin supports multiple Apps, we do not infer the App
            if 'Plugin' in app and app['Plugin']:
                for snippet, obj in app['Plugin'].items():
                    if not obj:
                        continue
                    for tech, version in obj.items():
                        if '|' in tech:
                            inferred_tech = tech.split('|')[0]
                            app_App = Utils.getEntityString(app['App']).split(', ')
                            if inferred_tech not in app_App:
                                if snippet not in app['App']:
                                    app['App'][snippet] = {}
                                app['App'][snippet][inferred_tech] = version
                                app['Inferred']['App'].append(inferred_tech)

            # Infer App Server and Runtime from Runlib
            ## If a runlib supports multiple App Servers or Runtimes, we do not infer them
            if app['Runlib']:
                for snippet, obj in app['Runlib'].items():
                    if not obj:
                        continue
                    for tech, version in obj.items():
                        if '|' in tech:
                            inferred_tech = tech.split('|')[0]
                            app_AppServer = Utils.getEntityString(app['App Server']).split(', ')
                            app_Runtime = Utils.getEntityString(app['Runtime']).split(', ')
                            if self.__class_type_mapper['mappings'].get(inferred_tech, 'NA') == 'App Server' and inferred_tech not in app_AppServer:
                                if snippet not in app['App Server']:
                                    app['App Server'][snippet] = {}
                                app['App Server'][snippet][inferred_tech] = version
                                app['Inferred']['App Server'].append(inferred_tech)
                            elif self.__class_type_mapper['mappings'].get(inferred_tech, 'NA') == 'Runtime' and inferred_tech not in app_Runtime:
                                if snippet not in app['Runtime']:
                                    app['Runtime'][snippet] = {}
                                app['Runtime'][snippet][inferred_tech] = version
                                app['Inferred']['Runtime'].append(inferred_tech)

            app['Linux'] = {'Lang':[],'App':[], 'App Server':[], 'Runtime':[]}
            app['Windows'] = {'Lang':[],'App':[], 'App Server':[], 'Runtime':[]}
            linux_compatability = False
            windows_compatability = False
            app['RepackageOS'] = []

            #### Infer OS
            recommended_OS = []
            incompatible_tech = []
            containerize_not_supported = []
            if (app['Lang'] or app['App'] or app['App Server'] or app['Runtime']):
                is_need_check_compatible = True
                app_OS = Utils.getEntityString(app['OS']).split(', ')
                if len(app_OS) == 0:
                    is_need_check_compatible = False

                child_types = ["App Server", "App", "Runtime","Lang"]
                is_init_recommended_OS = False
                for child_type in child_types:
                    if app[child_type]:
                        for child in Utils.getEntityString(app[child_type]).split(', '):
                            candidate_OS = self.__get_candidate_OS(child)
                            if not candidate_OS or len(candidate_OS) == 0:
                                logging.error(f'[{child}] can not find any OS in the knowledge graph')
                            else:
                                reduced_candidate_OS = self.__reduce_to_base_OS(candidate_OS)
                                if 'Linux' in reduced_candidate_OS:
                                    app['Linux'][child_type].append(child)
                                    linux_compatability = True
                                elif 'Windows' in reduced_candidate_OS:
                                    app['Windows'][child_type].append(child)
                                    windows_compatability = True
                                else:
                                    containerize_not_supported.append(child)
                                if not is_init_recommended_OS:
                                    recommended_OS = list(set(candidate_OS))
                                    is_init_recommended_OS = True
                                else:
                                    recommended_OS = self.__update_recommended_OS(candidate_OS, recommended_OS)
                                if is_need_check_compatible:
                                    if not self.__check_OS_compatible(candidate_OS, app_OS):
                                        incompatible_tech.append(child)

                if len(incompatible_tech) > 0:
                    app['InCompatible Tech'] = ', '.join(filter(None, incompatible_tech))
                
                if len(containerize_not_supported) > 0:
                    app['Containerize_Not_Supported Tech'] = ', '.join(filter(None, containerize_not_supported))
                
                if linux_compatability:
                    app['RepackageOS'].append('Linux')
                if windows_compatability:
                    app['RepackageOS'].append('Windows')

                reduced_recommended_OS = self.__reduce_to_base_OS(recommended_OS)
                reduced_recommended_OS = list(set(reduced_recommended_OS))
                
                ## No Input OS 
                if not is_need_check_compatible:
                    if len(recommended_OS) == 1:
                        app['Inferred']['OS'].append(recommended_OS[0])
                    else:
                        if reduced_recommended_OS:
                            if len(reduced_recommended_OS) == 1:
                                app['Inferred']['OS'].append(reduced_recommended_OS[0])
                app['Recommended OS'] = ', '.join(filter(None, sorted(reduced_recommended_OS)))
        return appL
