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
    # from .db import create_db_connection
    from .sim_applier import sim_applier
    
    try:
        kg_dir = config["general"]["kg_dir"]
        entities_json = config["tca"]["entities"]
        mentions_json = config["tca"]["mentions"]
    except KeyError as k:
        logging.error(f'{k} is not a key in your common.ini file.')
        print(f'{k} is not a key in your common.ini file.')
        exit()
    
    entity_file_name = os.path.join(kg_dir, entities_json)
    if not os.path.isfile(entity_file_name):
        logging.error(f"Entities json file {entity_file_name} does not exist. Run kg generator to create this file.")
        print(f"Entities json file {entity_file_name} does not exist. Run kg generator to create this file.")
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
        mentions[mention] = idx
        
    model_dir  = config["general"]["model_dir"]
    name       = config["task"]["name"]
    model_path = os.path.join(model_dir, name)
    os.makedirs(model_path, exist_ok=True)
    run_train  = True
    for fname in os.listdir(model_path):
        if fname.endswith('.pickle'):
            run_train = False
            break            
    if run_train:
        logging.info(f"TFIDF model not found in {config['general']['model_dir']}. Will run training to generate model.")
        print(f"TFIDF model not found in {config['general']['model_dir']}. Will run training to generate model.")
        train(config)
    
    sim_app    = sim_applier(config)
    tf_eids    = {}

    for mention, idx in mentions.items():
        #preprocessed = utils.preprocess(mention)
        #if not preprocessed:
        # preprocessed.append("")
        tech_sim_scores=sim_app.tech_stack_standardization(mention.lower())
        json_data["data"][idx]["predictions"] = json_data["data"][idx].get("predictions", [])
        if tech_sim_scores:
            for item in tech_sim_scores:
                entity  = item[0]
                score   = item[1]
                predicted_eid    = entity_to_eid.get(entity, None)
                json_data["data"][idx]["predictions"].append((predicted_eid, score))
    
    return tf_eids

def train(config):
    # from .db import create_db_connection
    from sklearn.feature_extraction.text import TfidfVectorizer
    from .sim_utils import sim_utils
    
    try:
        kg_dir = config["general"]["kg_dir"]
        entities_json = config["tca"]["entities"]
    except KeyError as k:
        logging.error(f'{k} is not a key in your common.ini file.')
        print(f'{k} is not a key in your common.ini file.')
        exit()

    entity_file_name = os.path.join(kg_dir, entities_json)
    if not os.path.isfile(entity_file_name):
        logging.error(f"Entities json file {entity_file_name} does not exist. Run kg generator to create this file.")
        print(f"Entities json file {entity_file_name} does not exist. Run kg generator to create this file.")
        exit()
            
    with open(entity_file_name, 'r', encoding='utf-8') as entity_file:
        entities = json.load(entity_file)

    entity_names = {}
    for idx, entity_data in entities["data"].items():
        entity_name = entity_data["entity_name"] 
        tca_id      = entity_data["entity_id"]
        entity_names[str(tca_id)] = entity_name
            
    vectorizer_name      ="standardization_vectorizer.pickle"
    standardization_model="standardization_model.pickle"
    instances_name       ="standardization_dict.pickle"

    data_dir     = config["general"]["data_dir"]
    model_dir    = config["general"]["model_dir"]
    name         = config["task"]["name"]    
    all_instances= []
    train_file_name = os.path.join(data_dir, name, "train.json")
    if not os.path.isfile(train_file_name):
        logging.error(f'{train_file_name} is not a file. Run "benchmarks.py" to generate this training file')
        print(f'{train_file_name} is not a file. Run "benchmarks.py" to generate this train data file')
        exit()

    data_to_eid = {}
    try:
        with open(train_file_name, 'r', encoding='utf-8') as train_file:
            json_data = json.load(train_file)
            data      = json_data["data"]
            for idx, item in data.items():
                for mention in item["mentions"]:
                    data_to_eid[mention] = item["label"]
    except OSError as exception:
        logging.error(exception)
        exit()
        
    for mention in data_to_eid:
        eid    = data_to_eid[mention]
        entity = entity_names[str(eid)]
        
        if [entity, mention, mention] in all_instances:
            print("duplicate:",[entity, mention])
            continue
        
        all_instances.append([entity, mention, mention])
        all_targets     =  sim_utils.text_collection_kg_without_tokenization4vector(all_instances)
        tfidf           =  TfidfVectorizer(token_pattern=r"(?u)\b\w+\b").fit(all_targets)    
        tfs             =  tfidf.fit_transform(all_targets)

    model_path = os.path.join(model_dir, name)
    pickle.dump(tfs, open(os.path.join(model_path,vectorizer_name), "wb"))
    pickle.dump(tfidf, open(os.path.join(model_path,standardization_model),"wb"))
    pickle.dump(all_instances, open(os.path.join(model_path,instances_name),"wb"))

