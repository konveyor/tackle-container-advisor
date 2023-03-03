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

import re
import logging
import configparser
import os
import json

config = configparser.ConfigParser()
common = os.path.join("config", "common.ini")
kg     = os.path.join("config", "kg.ini")
config.read([common, kg])


class Utils:

    @staticmethod
    def preprocess_tech_stack_for_sim(tech_stack):
        '''
         preprocess_tech_stack_for_sim method takes the input string and removes any non aschii character
         present in that string.
        '''

        try:
            tech_stack = re.sub(r'[^\x00-\x7F]+', " ", " " + str(tech_stack) + " ").strip()
            return tech_stack

        except Exception as e:
            logging.error(str(e))

    @staticmethod
    def getEntityString(obj):
        ## obj: {snippet:{entity:version}}
        ## return: entity, entity
        if not obj:
            return ''
        tech = []
        for entityversion in obj.values():
            for x in entityversion.keys():
                if x:
                    tech.append(x)
        return ', '.join(filter(None, tech))

    # added to process json compatible format of entities
    @staticmethod
    def getStandardEntityString(obj):
        ## obj: {snippet:{entity:version}}
        ## return: entity, entity
        if not obj:
            return ''
        tech = []
        for x in obj.values():
            tech.append(x['standard_name'])
        return ', '.join(filter(None, tech))
    
    @staticmethod
    def mergeDicts(result, app_tech):
        """
        mergeDicts merges the nested dictionaries
        """
        try:
            if not result:
                result = {}
            if not app_tech:
                return result
            for snippet, obj in app_tech.items():
                if not obj:
                    continue
                for tech, version in obj.items():
                    if snippet not in result:
                        result[snippet] = {}
                    result[snippet][tech] = version
            return result

        except Exception as e:
            logging.error(str(e))
    @staticmethod
    def get_imageKG(catalogKG:str) ->dict:
        """
        Load image KG
        Args:
            catalogKG (str): Catalog name.

        Returns:
            dict: catalog KG.
        """
        imageKG = {} 
        imageKG_filepath = os.path.join(config['general']['kg_dir'], config['filenames'][catalogKG])
        if os.path.exists(imageKG_filepath):   
            with open(imageKG_filepath, 'r') as f:
                imageKG = json.load(f)     
        else:
            logging.error(f'imageKG[{imageKG_filepath}] is empty or not exists')
        return imageKG
    
    @staticmethod
    def get_baseOS(imageKG: dict,baseOSKG:str):
        """
        Load base OS.

        Args:
            imageKG (dict): image catalog KG.
            baseOSKG (str): file name.

        Returns:
            _type_: _description_
        """
        baseOSKG_filepath = os.path.join(config['general']['kg_dir'], config['filenames'][baseOSKG])
        osBaseImages = {}
        if os.path.exists(baseOSKG_filepath):
            with open(baseOSKG_filepath, 'r') as f:
                baseOSKG = json.load(f)

            for image_name in baseOSKG['Container Images']:
                osBaseImages[baseOSKG['Container Images'][image_name]['OS'][0]['Class']] = image_name
                imageKG['Container Images'][image_name] = baseOSKG['Container Images'][image_name]
        else:
            logging.error(f'baseOSKG[{baseOSKG_filepath}] is empty or not exists')
        return osBaseImages , imageKG
    
    @staticmethod
    def get_inverted_imageKG(inverted_catalogKG:str)-> dict:
        """
        Load inverted catalog KG
        Args:
            inverted_catalogKG (str): KG name

        Returns:
            dict: inverted indexes
        """
        inverted_imageKG = {}
        inverted_imageKG = os.path.join(config['general']['kg_dir'], config['filenames'][inverted_catalogKG])
        if os.path.exists(inverted_imageKG):
            with open(inverted_imageKG, 'r') as f:
                inverted_imageKG = json.load(f)
        else:
            logging.error(f'inverted_dockerimageKG[{inverted_imageKG}] is empty or not exists')
        return inverted_imageKG

    @staticmethod
    def get_COT() ->dict:
        """
          Load COTS KG.

        Returns:
            dict: COTS KG
        """
        COTSKG = {}
        COTSKG_filepath = os.path.join(config['general']['kg_dir'], config['filenames']['COTSKG'])
        if os.path.exists(COTSKG_filepath):
            with open(COTSKG_filepath, 'r') as f:
                COTSKG = json.load(f)
        else:
            logging.error(f'COTSKG[{COTSKG_filepath}] is empty or not exists')
        
        return COTSKG

     
       

        
        
 
        
    
    
   

