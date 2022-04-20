import os
import json
import logging
import pickle
from time import time

def predict(config, json_data):
    """
    Runs tfidf model on test set

    :param data_to_ids: Dictionary containing mapping of test mention to tuple of (entity id, Wikidata qid)
    :type data_to_qid: <class 'dict'> 

    :returns: Returns a dictionary of test mention to list of predicted entity ids
    """ 
    from .sim_applier import sim_applier
    
    try:
        kg_dir        = config["general"]["kg_dir"]
        entities_json = config["tca"]["entities"]
        mentions_json = config["tca"]["mentions"]
        model_dir     = config["general"]["model_dir"]
        name          = config["task"]["name"]
    except KeyError as k:
        logging.error(f'{k} is not a key in your common.ini file.')
        exit()
    
    entity_file_name = os.path.join(kg_dir, entities_json)
    if not os.path.isfile(entity_file_name):
        logging.error(f"Entities json file {entity_file_name} does not exist. Run kg generator to create this file.")
        exit()

    with open(entity_file_name, 'r', encoding='utf-8') as entity_file:
        entities = json.load(entity_file)

    entity_to_eid   = {}
    for idx, entity_data in entities["data"].items():
        entity_name = entity_data["entity_name"] 
        tca_id      = entity_data["entity_id"]
        entity_to_eid[entity_name] = tca_id

    mentions   = {}
    for idx in json_data["data"]:
        mention = json_data["data"][idx]["mention"]        
        mentions[idx] = mention
        
    model_path = os.path.join(model_dir, name)
    os.makedirs(model_path, exist_ok=True)
    run_train  = True
    for fname in os.listdir(model_path):
        if fname.endswith('.pickle'):
            run_train = False
            break            
    if run_train:
        train(config)
    
    sim_app    = sim_applier(config)
    tf_eids    = {}
    logging.info(f"Number of tfidf mentions = {len(mentions)}")
    for idx, mention in mentions.items():
        tech_sim_scores=sim_app.tech_stack_standardization(mention.lower())
        json_data["data"][idx]["predictions"] = json_data["data"][idx].get("predictions", [])
        if tech_sim_scores:
            for item in tech_sim_scores:
                entity  = item[0]
                score   = item[1]
                if entity == 'NA_CATEGORY':
                    predicted_eid = 0
                else:
                    predicted_eid    = entity_to_eid.get(entity, None)
                json_data["data"][idx]["predictions"].append((predicted_eid, score))
    
    return tf_eids

def train(config):
    from sklearn.feature_extraction.text import TfidfVectorizer
    from .sim_utils import sim_utils

    start = time()
    try:
        kg_dir        = config["general"]["kg_dir"]
        entities_json = config["tca"]["entities"]
        model_name    = config["train"]["model_name"]
        tfidf_name    = config["train"]["tfidf_name"]
        instances_name= config["train"]["instances_name"]        
    except KeyError as k:
        logging.error(f'{k} is not a key in your common.ini file.')
        exit()

    entity_file_name = os.path.join(kg_dir, entities_json)
    if not os.path.isfile(entity_file_name):
        logging.error(f"Entities json file {entity_file_name} does not exist. Run kg generator to create this file.")
        exit()
            
    with open(entity_file_name, 'r', encoding='utf-8') as entity_file:
        entities = json.load(entity_file)

    # Gather entity_names to entity id mapping
    entity_names = {}
    for idx, entity_data in entities["data"].items():
        entity_name = entity_data["entity_name"] 
        tca_id      = entity_data["entity_id"]
        entity_names[str(tca_id)] = entity_name

    # Gather training data
    data_dir     = config["general"]["data_dir"]
    model_dir    = config["general"]["model_dir"]
    name         = config["task"]["name"]    
    train_file_name = os.path.join(data_dir, name, "train.json")
    if not os.path.isfile(train_file_name):
        logging.error(f'{train_file_name} is not a file. Run "benchmarks.py" to generate this training file')
        exit()
    
    data_to_eid = {}
    try:
        with open(train_file_name, 'r', encoding='utf-8') as train_file:
            json_data = json.load(train_file)
            data      = json_data["data"]
            label       = json_data.get("label", "label")
            for idx, item in data.items():
                for mention in item["mentions"]:
                    data_to_eid[mention] = item[label]
    except OSError as exception:
        logging.error(exception)
        exit()

    # Convert training data format
    all_instances= []
    for mention in data_to_eid:
        eid    = data_to_eid[mention]
        entity = entity_names[str(eid)]
        
        if [entity, mention, mention] in all_instances:
            logging.warning("duplicate:",[entity, mention])
            continue
        
        all_instances.append([entity, mention, mention])
        
        
    all_targets     =  sim_utils.text_collection_kg_without_tokenization4vector(all_instances)
    tfidf           =  TfidfVectorizer(token_pattern=r"(?u)\b\w+\b").fit(all_targets)    
    tfs             =  tfidf.fit_transform(all_targets)

    model_path = os.path.join(model_dir, name)
    with open(os.path.join(model_path,model_name), "wb") as model_file:
        pickle.dump(tfs, model_file)
    with open(os.path.join(model_path,tfidf_name),"wb") as tfidf_file:
        pickle.dump(tfidf, tfidf_file)
    with open(os.path.join(model_path,instances_name),"wb") as instances_file:
        pickle.dump(all_instances, instances_file)
    end = time()
