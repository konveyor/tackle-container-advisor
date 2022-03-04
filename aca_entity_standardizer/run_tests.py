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

import configparser
import logging
import sqlite3
import os
import pickle
import json
import urllib.parse as uparse
import multiprocessing
from sqlite3 import Error
from sqlite3.dbapi2 import Cursor, complete_statement
# from pathlib import Path
from db import create_db_connection
from sim_applier import sim_applier
from sklearn.feature_extraction.text import TfidfVectorizer
from sim_applier import sim_applier
from sim_utils import sim_utils
import requests
from time import time

def get_data_combinations(data):
    """
    Generate phrases from words in data

    :param data: A list of mention words e.g. ['Apache', 'Tomcat', 'HTTP', 'Server']
    :type data: list 

    # :returns: Returns a list of truncated phrases e.g ['Tomcat HTTP Server', 'HTTP Server', ... 'Apache Tomcat HTTP', 'Apache Tomcat', ...]
    :returns: Returns a list of truncated phrases e.g ['Apache Tomcat HTTP', 'Apache Tomcat', ... , 'Tomcat HTTP Server', 'HTTP Server', ...]

    """
    combinations = []
    combinations.append(' '.join(data))
    for i in range(1,len(data),1):
        combinations.append(' '.join(data[:-i]))
    for i in range(1,len(data),1):
        combinations.append(' '.join(data[i:]))
    return combinations


def invoke_wikidata_api(data):
    """
    Invokes wikidata autocomplete on data

    :param data: String to query Wikidata API for qids
    :type data: string 

    :returns: Returns a list of qids
    """
    qids    = []
    headers = {'Content-type': 'application/json'}    
    WD_URL  = config_obj['url']['wd_url']
    try:
        response = requests.get(WD_URL+uparse.quote(data), headers=headers)
        candidates = response.json()
        if candidates['success'] != 1:
            logging.error(f"Failed wikidata query -> {candidates}")
        else:
            for candidate in candidates['search']:
                qids.append(candidate['id'])
    except Exception as e:
        logging.error(f"Error querying wikidata url {WD_URL} : {e}")

    return qids

def get_wikidata_qids(data):
    """
    Gets wikidata qids for data

    :param data: Mention for which to get Wikidata qids
    :type data: string 

    :returns: Returns a dictionary of data to predicted qids
    """
    wd_qids = {}

    # Get qids for exact phrase
    qids  = []
    qids += invoke_wikidata_api(data)    
    # print("Len of qids after exact = ", len(qids))

    fragments    = data.split(' ')
    # Get valid fragments
    data_to_qids = {}
    for i, frag in enumerate(fragments):
        frqids = invoke_wikidata_api(frag)            
        if frqids:
            data_to_qids[frag] = frqids           

    # Get qids for combinations of all fragments
    combinations = get_data_combinations(fragments)
    for i, comb in enumerate(combinations):
        qids += invoke_wikidata_api(comb)        
    # print("Len of qids after all combos = ", len(qids))

    # Get qids for combinations of sorted valid fragments
    data_to_qids = {k: v for k, v in sorted(data_to_qids.items(), key=lambda item: len(item[1]))}
    valid_data   = [d for d in data_to_qids]
    combinations = get_data_combinations(valid_data)
    for i, comb in enumerate(combinations):
        qids += invoke_wikidata_api(comb)        
    # print("Len of qids after sorted fragment combos = ", len(qids))

    if not qids:           
        logging.info(f"No qids for {data}")                    
    
    wd_qids[data] = qids
    return wd_qids

def run_wikidata_autocomplete(data_to_ids):
    """
    Runs wikidata autocomplete on test set

    :param data_to_ids: Dictionary containing mapping of test mention to tuple of (entity id, Wikidata qid)
    :type data_to_qid: <class 'dict'> 

    :returns: Returns a dictionary of test mention to list of predicted Wikidata qids
    """
    pool             = multiprocessing.Pool(2*os.cpu_count())
    wd_results       = pool.map(get_wikidata_qids, data_to_ids.keys())
    pool.close()

    wd_qids = {k:v for item in wd_results for k,v in item.items()}

    return wd_qids        

def run_tfidf(data_to_ids, connection):
    """
    Runs tfidf model on test set

    :param data_to_ids: Dictionary containing mapping of test mention to tuple of (entity id, Wikidata qid)
    :type data_to_qid: <class 'dict'> 

    :returns: Returns a dictionary of test mention to list of predicted entity ids
    """ 

    vectorizer_name      ="standardization_vectorizer.pickle"
    standardization_model="standardization_model.pickle"
    instances_name       ="standardization_dict.pickle"

    entity_names = sim_utils.load_entity_names(connection) 
    all_instances= []
    train_filename = os.path.join(config_obj['benchmark']['data_path'], 'train.csv')
    if not os.path.isfile(train_filename):
        logging.error(f'{train_filename} is not a file. Run "python benchmarks.py" to generate this train data file')
        print(f'{train_filename} is not a file. Run "python benchmarks.py" to generate this train data file')
        exit()
    else:
        data_to_eid = {}
        try:
            train_filename = os.path.join(config_obj['benchmark']['data_path'], 'train.csv')        
            with open(train_filename, 'r') as train_file:            
                train = [d.strip() for d in train_file.readlines()]
                for row in train:
                    (mention, eid) = tuple(row.split('\t'))
                    data_to_eid[mention] = eid
        except OSError as exception:
            logging.error(exception)
            exit()
        
        for mention in data_to_eid:
            eid    = data_to_eid[mention]
            entity = entity_names[eid]

            if [entity, mention, mention] in all_instances:
                print("duplicate:",[entity, mention])
                continue

            all_instances.append([entity, mention , mention])
  
    all_targets     =  sim_utils.text_collection_kg_without_tokenization4vector(all_instances)
    tfidf           =  TfidfVectorizer(token_pattern=r"(?u)\b\w+\b").fit(all_targets)    
    tfs             =  tfidf.fit_transform(all_targets)

    model_path = config_obj["model"]["model_path"]
    pickle.dump(tfs, open(model_path+vectorizer_name, "wb"))
    pickle.dump(tfidf, open(model_path+standardization_model,"wb"))
    pickle.dump(all_instances, open(model_path+instances_name,"wb"))

    entity_cursor = connection.cursor()   
    entity_cursor.execute("SELECT * FROM entities")
    entity_to_eid  = {}
    for entity_tuple in entity_cursor.fetchall():
        entity_id, entity, entity_type_id, external_link = entity_tuple
        entity_to_eid[entity] = entity_id


    mentions   = list(data_to_ids.keys())        
    sim_app    = sim_applier(model_path)      
    start      = time()
    tf_eids    = {}
    for mention in mentions:
        tech_sim_scores=sim_app.tech_stack_standardization(mention)
        if tech_sim_scores:
            entity  = tech_sim_scores[0][0]
            score   = tech_sim_scores[0][1]
            predicted_eid    = entity_to_eid.get(entity, None)
            tf_eids[mention] = [predicted_eid]
        else:
            tf_eids[mention] = []
    end        = time()
    return tf_eids


def get_topk_accuracy(data_to_ids, alg_ids, is_qid=True):
    """
    Print top-1, top-3, top-5, top-10, top-inf accuracy 

    :param data_to_qid: Dictionary containing mapping of test mention to tuple of (entity id, Wikidata qid)
    :type data_to_ids: <class 'dict'>
    :param alg_ids: Dictionary containing mapping of test mention to list of predicted Wikidata qids or list of predicted entity ids   
    :type alg_ids: <class 'dict'>
    :param is_qid: Specifies if alg_ids contains predicted qids or predicted entity ids  
    :type is_qid: Boolean

    :returns: Prints top-1, top-3, top-5, top-10, top-inf accuracy
    """

    total_mentions = len(data_to_ids)
    topk  = (0, 0, 0, 0, 0) # Top-1, top-3, top-5, top-10, top-inf
    for mention in data_to_ids:
        (entity_id, wiki_id) = data_to_ids[mention]
        ids = alg_ids.get(mention, None)
        if not ids:
            continue
        for i, eid in enumerate(ids):
            if (not is_qid and eid == entity_id) or (is_qid and eid == wiki_id): 
                topk = (topk[0],topk[1],topk[2],topk[3],topk[4]+1)
                if i <= 0:
                    topk = (topk[0]+1,topk[1],topk[2],topk[3],topk[4]) 
                if i <= 2:
                    topk = (topk[0],topk[1]+1,topk[2],topk[3],topk[4])
                if i <= 4:
                    topk = (topk[0],topk[1],topk[2]+1,topk[3],topk[4])
                if i <= 9:
                    topk = (topk[0],topk[1],topk[2],topk[3]+1,topk[4])
                break

    return topk

def print_gh_markdown(wd_topk, tf_topk, total_mentions):
    print("<p><table>")
    print("<thead>")
    print("<tr><th>Method</th><th>top-1</th><th>top-3</th><th>top-5</th><th>top-10</th><th>top-inf(count)</th></tr>")
    print("</thead>")
    print("<tbody>")
    print(f"<tr><td>WD api</td><td>{wd_topk[0]/total_mentions:.2f}</td><td>{wd_topk[1]/total_mentions:.2f}</td><td>{wd_topk[2]/total_mentions:.2f}</td><td>{wd_topk[3]/total_mentions:.2f}</td><td>{wd_topk[4]/total_mentions:.2f} ({wd_topk[4]})</td></tr>")
    print(f"<tr><td>TFIDF</td><td>{tf_topk[0]/total_mentions:.2f}</td><td>{tf_topk[1]/total_mentions:.2f}</td><td>{tf_topk[2]/total_mentions:.2f}</td><td>{tf_topk[3]/total_mentions:.2f}</td><td>{tf_topk[4]/total_mentions:.2f} ({tf_topk[4]})</td></tr>")
    print("</tbody>")
    print("</table></p>")

def run_baselines(connection):
    """
    Run baseline techniques

    :param connection: A connection to mysql
    :type  connection:  <class 'sqlite3.Connection'>

    :returns: Prints top-k accuracy for tf-idf and wiki autocomplete api approaches 
    """
    test_filename = os.path.join(config_obj['benchmark']['data_path'], 'test.csv')        

    if not os.path.isfile(test_filename):
        logging.error(f'{test_filename} is not a file. Run "python benchmarks.py" to generate this test data file')
        print(f'{test_filename} is not a file. Run "python benchmarks.py" to generate this test data file')
        exit()
    else:
        data_to_ids = {}
        try:
            test_filename = os.path.join(config_obj['benchmark']['data_path'], 'test.csv')        
            with open(test_filename, 'r') as test_file:            
                test = [d.strip() for d in test_file.readlines()]
                for row in test:
                    (mention, eid, qid) = tuple(row.split('\t'))
                    data_to_ids[mention] = (int(eid), qid)
        except OSError as exception:
            logging.error(exception)
            exit()
        
        total_mentions = len(data_to_ids)                                
        
        wd_start= time()
        wd_qids = run_wikidata_autocomplete(data_to_ids)
        wd_end  = time()
        wd_topk = get_topk_accuracy(data_to_ids, wd_qids)        
        # wd_topk = (0, 0, 0, 0, 0)
        
        tf_start= time()
        tf_eids = run_tfidf(data_to_ids, connection)
        tf_end  = time()
        tf_topk = get_topk_accuracy(data_to_ids, tf_eids, is_qid=False)

        print(f'WD api with no ctx took {(wd_end-wd_start):.2f} seconds.')
        print(f'TFIDF model took {(tf_end-tf_start):.2f} seconds.')
        print_gh_markdown(wd_topk, tf_topk, total_mentions)

config_obj = configparser.ConfigParser()
config_obj.read("./config.ini")

logging.basicConfig(filename='logging.log',level=logging.DEBUG, \
                    format="[%(levelname)s:%(filename)s:%(lineno)s - %(funcName)20s() ] %(message)s", filemode='w')

if __name__ == '__main__':
    try:
        db_path = config_obj["db"]["db_path"]
    except KeyError as k:
        logging.error(f'{k}  is not a key in your config.ini file.')
        print(f'{k} is not a key in your config.ini file.')
        exit()

    try:
        data_path = config_obj["benchmark"]["data_path"]
    except KeyError as k:
        logging.error(f'{k}  is not a key in your config.ini file.')
        print(f'{k} is not a key in your config.ini file.')
        exit()    

    if not os.path.isfile(db_path):
        logging.error(f'{db_path} is not a file. Run "sh setup" from /tackle-container-advisor folder to generate db files')
        print(f'{db_path} is not a file. Run "sh setup.sh" from /tackle-container-advisor folder to generate db files')
        exit()
    else:
        connection = create_db_connection(db_path)
        run_baselines(connection)