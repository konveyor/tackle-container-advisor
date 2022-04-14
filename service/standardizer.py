import os
import json
import time
import configparser
import logging
from entity_standardizer.tfidf import TFIDF
from service.version_detector import version_detector


def version_standardizer(mention, top_entity_prediction):
    vd = version_detector()
    version = vd.get_version_strings(mention.lower())
    std_version = vd.get_standardized_version(vd, top_entity_prediction, version)
    final_version = (version,std_version)
    return final_version
    
    
def entity_standardizer(mentions):
    logger = logging.getLogger('standardizer')
    logger.setLevel(logging.INFO)
    config    = configparser.ConfigParser()
    common    = os.path.join("config", "common.ini")
    kg        = os.path.join("config", "kg.ini")
    config.read([common, kg])
    try:
        kg_dir = config["general"]["kg_dir"]
        entities_json = config["tca"]["entities"]
    except KeyError as k:
        logger.error(f'{k} is not a key in your common.ini file.')
        exit()

    # Check that kg contains entities file
    entity_file_name = os.path.join(kg_dir, entities_json)
    if not os.path.isfile(entity_file_name):
        logger.error(f"Entities json file {entity_file_name} does not exist. Run kg generator to create this file.")
        exit()

    # Get mapping of entity id to entity names
    with open(entity_file_name, 'r', encoding='utf-8') as entity_file:
        entities = json.load(entity_file)
    entity_names = {}
    entity_names[0] = 'NA_CATEGORY'
    for idx, entity_data in entities["data"].items():
        entity_name = entity_data["entity_name"] 
        tca_id      = entity_data["entity_id"]
        entity_names[tca_id] = entity_name

    # Convert mention data to inference format for entity standardizer
    mention_data = {}
    for idx, mention in enumerate(mentions):
        mention_data[idx] = {}
        mention_data[idx]["mention"] = mention.strip()
    infer_data = {"label_type": "int", "label": "entity_id", "data_type": "strings", "data": mention_data}
    tfidf            = TFIDF("deploy")
    tfidf_start      = time.time()
    infer_data       = tfidf.infer(infer_data)
    tfidf_end        = time.time()
    tfidf_time       = (tfidf_end-tfidf_start)
    entities         = {}
    mention_data = infer_data.get("data", {})    
    for idx, entry in mention_data.items():
        mention     = entry.get("mention", None)
        predictions = entry.get("predictions", [])
        predictions = [[entity_names[p[0]], p[1]] for p in predictions]
        if not predictions:            
            print(f"No predictions for {mention}")
            logger.error(f"No predictions for {mention}")
            continue
        entities[mention] = predictions    

    return entities


def standardizer(mentions):
    entities = entity_standardizer(mentions)
    standardized = []
    for mention, entity_list in entities.items():
        top_prediction = entity_list[0]        
        final_version  = version_standardizer(mention, top_prediction)
        standardized.append([mention, entity_list, final_version])

    return standardized
                                    
