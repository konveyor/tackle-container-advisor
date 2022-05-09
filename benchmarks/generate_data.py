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

import configparser
import logging
import os
import json
import numpy as np

def clean(mention):
    """
    Remove/Replace non-ascii characters 
    :param mention: String to remove/replace non-ascii characters from
    :type  mention: string

    :returns: Return cleaned string with non-ascii characters removed/replaced
    """

    charmap = {
        u'\xd8'  : u'0',     # Latin Capital letter O with stroke
        u'\uff03': u'\x23', # Full-width number sign
        u'\u266f': u'\x23', # Music Sharp Sign
        u'\u2160': u'\x49', # Roman Numeral One
        u'\u042f': u'\x52', # Cyrillic Capital Letter Ya
        u'\u2013': u'\x2d', # En Dash
        u'\xae'  : u''      # Registered Sign
    }

    for c in charmap:
        mention = mention.replace(c, charmap[c])

    return mention

def split(entity):
    parts   = entity.split('|')
    mention = None
    i = 1
    while parts[-i] == '*': 
        if i >= len(parts):
            break
        i += 1
    mention = parts[-i]
    if not mention:
        return None
    else:
        return clean(mention)
        
def is_ascii(s):
    """
    Checks if 's' contains only ascii characters
    :param s: String to check for ascii characters
    :type  s: string

    :returns: Return True if string contains only ascii characters, else returns False
    """

    return all(ord(c) < 128 for c in s)

def get_benchmark_data(config, all_train=False):
    """
    Create train and inference data using entities and mentions json files from KG
    If all_train is True - All mentions used for training
    else Inference data uses mentions from 'others' source and 
    train data uses mentions from rest of the sources

    :returns: Returns dictionary containing train and inference data
    """
    try:
        kg_dir   = config["general"]["kg_dir"]
        ent_json = config["tca"]["entities"]
        men_json = config["tca"]["mentions"]
    except KeyError as k:
        logging.error(f'{k}  is not a key in your common.ini file.')
        exit()
    
    entity_file_name = os.path.join(kg_dir, ent_json)
    if not os.path.exists(entity_file_name):
        logging.error(f"Entities json file {entity_file_name} does not exist. Run kg generator to create this file.")
        exit()

    mentions_file_name = os.path.join(kg_dir, men_json)
    if not os.path.exists(mentions_file_name):
        logging.error(f"Mentions json file {mentions_file_name} does not exist. Run kg generator to create this file.")
        exit()
        
    with open(entity_file_name, 'r', encoding='utf-8') as entity_file:
        entities = json.load(entity_file)
    with open(mentions_file_name, 'r', encoding='utf-8') as mentions_file:
        mentions = json.load(mentions_file)

    train_data = {}
    inf_data   = {}
    inf_idx    = 0
    for idx, mentions_data in mentions["data"].items():
        train_data[idx] = {}
        entity_id = mentions_data["entity_id"]        
        mentions  = mentions_data["mentions"]
        for source, mention_list in mentions.items():
            if source == "others":
                if all_train:
                    for mention in mention_list:
                        train_data[idx]["mentions"] = train_data[idx].get("mentions", [])
                        train_data[idx]["mentions"] += [clean(mention) for mention in mention_list]
                    train_data[idx]["entity_id"] = entity_id
                else:
                    for mention in mention_list:
                        inf_data[inf_idx] = {}
                        inf_data[inf_idx]["mention"] = clean(mention)
                        inf_data[inf_idx]["entity_id"]  = entity_id
                        inf_idx += 1
            else:
                train_data[idx]["mentions"] = train_data[idx].get("mentions", [])
                if source == "standardized":
                    mention = split(mention_list)
                    if mention is not None:
                        train_data[idx]["mentions"].append(mention)
                else:
                    train_data[idx]["mentions"] += [clean(mention) for mention in mention_list]
                    
                train_data[idx]["entity_id"] = entity_id

    return train_data, inf_data

def create_deploy_benchmark(config, train_data, inf_data):
    """
    Create benckmark train and infer json files with entity id as label
    
    :returns: Creates train.json and infer.json inside config["data_dir"]/tca
    """
    try:
        data_dir = config["general"]["data_dir"]
    except KeyError as k:
        logging.error(f'{k}  is not a key in your common.ini file.')
        exit()
        
    data_dir = config["general"]["data_dir"]
    name     = "deploy"
    os.makedirs(os.path.join(data_dir, name), exist_ok=True)
    json_data = {"label_type": "int", "label": "entity_id", "data_type": "strings", "data": train_data}
    with open(os.path.join(data_dir, name, 'train.json'), 'w', encoding='utf-8') as json_file:
        json.dump(json_data, json_file, indent=4)


def create_tca_benchmark(config, train_data, inf_data):
    """
    Create benckmark train and infer json files with entity id as label
    
    :returns: Creates train.json and infer.json inside config["data_dir"]/tca
    """
    try:
        data_dir = config["general"]["data_dir"]
    except KeyError as k:
        logging.error(f'{k}  is not a key in your common.ini file.')
        exit()
        
    data_dir = config["general"]["data_dir"]
    name     = "tca"
    os.makedirs(os.path.join(data_dir, name), exist_ok=True)
    json_data = {"label_type": "int", "label": "entity_id", "data_type": "strings", "data": inf_data}
    with open(os.path.join(data_dir, name, 'infer.json'), 'w', encoding='utf-8') as json_file:
        json.dump(json_data, json_file, indent=4)

    json_data = {"label_type": "int", "label": "entity_id", "data_type": "strings", "data": train_data}
    with open(os.path.join(data_dir, name, 'train.json'), 'w', encoding='utf-8') as json_file:
        json.dump(json_data, json_file, indent=4)


def create_wikidata_benchmark(config, train_data, inf_data):
    """
    Create benckmark train and infer json files with wikidata qid as label
    
    :returns: Creates infer.json inside config["data_dir"]/wikidata
    """
    try:
        kg_dir   = config["general"]["kg_dir"]
        data_dir = config["general"]["data_dir"]
        ent_json = config["tca"]["entities"]
    except KeyError as k:
        logging.error(f'{k}  is not a key in your common.ini file.')
        exit()
        
    entity_file_name = os.path.join(kg_dir, ent_json)
    if not os.path.exists(entity_file_name):
        logging.error(f"Entities json file {entity_file_name} does not exist. Run kg generator to create this file.")
        exit()    

    with open(entity_file_name, 'r', encoding='utf-8') as entity_file:
        entities = json.load(entity_file)
        
    no_external = 0
    eid_to_qid  = {}    
    for idx, entity_data in entities["data"].items():
        tca_id = entity_data["entity_id"]
        external  = eval(entity_data["external_link"])
        if not external:
            no_external += 1
            continue
        wd_qid = external['qid']
        if wd_qid == '' or wd_qid == 'None' or wd_qid == None:
            continue
        eid_to_qid[tca_id] = wd_qid

    for idx, data in inf_data.items():
        entity_id = data["entity_id"]
        if entity_id in eid_to_qid:
            wd_qid = eid_to_qid[entity_id]
            data["qid"]  = wd_qid
        else:
            wd_qid = None
        del data["entity_id"]    
        
    data_dir = config["general"]["data_dir"]
    name     = "wikidata"
    os.makedirs(os.path.join(data_dir, name), exist_ok=True)
    json_data = {"label_type": "string", "label": "qid", "data_type": "strings", "data": inf_data}
    with open(os.path.join(data_dir, name, 'infer.json'), 'w', encoding='utf-8') as json_file:
        json.dump(json_data, json_file, indent=4)
    '''
    json_data = {"label_type": "string", "label": "qid", "data_type": "strings", "data": train_data}
    with open(os.path.join(data_dir, name, 'train.json'), 'w', encoding='utf-8') as json_file:
        json.dump(json_data, json_file, indent=4)
    '''
        
if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO, format="[%(asctime)s] %(name)s:%(levelname)s in %(filename)s:%(lineno)s - %(message)s", filemode='w')
    config   = configparser.ConfigParser()
    common   = os.path.join("config", "common.ini")
    kg       = os.path.join("config", "kg.ini")
    config.read([common, kg])
    train_data, inf_data = get_benchmark_data(config, all_train=False)
    create_tca_benchmark(config, train_data, inf_data)
    create_wikidata_benchmark(config, train_data, inf_data)
    train_data, inf_data = get_benchmark_data(config, all_train=True)
    create_deploy_benchmark(config, train_data, inf_data)
