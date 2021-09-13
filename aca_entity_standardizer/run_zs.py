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
import json
from sqlite3 import Error
from sqlite3.dbapi2 import Cursor, complete_statement
from pathlib import Path
from db import create_db_connection
from sim_applier import sim_applier
import requests

def run_entity_linking(data_to_qid, context='software'):
    """
    Runs entity linking on zero shot test set

    :param data_to_qid: Dictionary containing mapping of test mention to Wikidata qid
    :type data_to_qid: <class 'dict'> 
    :param context: Context to be applied to entity linking API
    :type context: string

    :returns: Returns a dictionary of test mention to predicted Wikidata qid
    """
    EL_URL  = "http://9.59.199.65:5002/json-example?"

    payload    = []
    id_to_data = {}
    for i, data in enumerate(data_to_qid):
        qid = data_to_qid[data]
        id_to_data[str(i)] = (data, qid)   
        payload.append({'id': i, 'mention': data, 'context_left': '', 'context_right': context})

    data_json = json.dumps(payload)
    headers = {'Content-type': 'application/json'}
    try:
        response = requests.post(EL_URL, data=data_json, headers=headers)
        candidates = response.json()
    except Exception as e:
        print("Error querying entity linking url", EL_URL, ":", e)

    el_qids = {}
    for i in candidates:
        mention = id_to_data[i][0]
        el_qids[mention] = el_qids.get(mention, [])
        cdata = eval(candidates[i]['top_k_entities'])
        for j, candidate in enumerate(cdata):
            qid = candidate[1]
            el_qids[mention].append(qid)

    return el_qids

def get_data_combinations(data):
    """
    Generates combinations from words in data

    :param data: A mention as a phrase of words e.g. 'Apache Tomcat HTTP Server'
    :type data: string 

    :returns: Returns a list of truncated phrases e.g ['Apache Tomcat HTTP Server', 'Apache Tomcat HTTP', 'Apache Tomcat', 'Apache']
    """

    # print(data)
    combinations = []
    fragments = data.split(' ')
    # print(fragments)
    combinations.append(' '.join(fragments))
    for i in range(1,len(fragments),1):
        combinations.append(' '.join(fragments[:-i]))
    # print(combinations)    
    return combinations

def run_wikidata_autocomplete(data_to_qid):
    """
    Runs wikidata autocomplete on zero shot test set

    :param data_to_qid: Dictionary containing mapping of test mention to Wikidata qid
    :type data_to_qid: <class 'dict'> 

    :returns: Returns a dictionary of test mention to predicted Wikidata qid
    """

    WD_URL="https://www.wikidata.org/w/api.php?action=wbsearchentities&language=en&format=json&search="
    # WD_URL="https://www.wikidata.org/w/api.php?action=wbsearchentities"
    wd_qids = {}

    params = json.dumps({'action':'wbsearchentities', 'language':'en', 'format':'json', 'search':'Microsoft'})
    headers = {'Content-type': 'application/json'}    
    for i, data in enumerate(data_to_qid):    
        correct_qid = data_to_qid[data]        
        qids = []
        combinations = get_data_combinations(data)
        for i, comb in enumerate(combinations):
            try:
                # response = requests.post(WD_URL, data=data_json, headers=headers)
                # print(requests.get(url, params).text)            
                response = requests.get(WD_URL+comb, headers=headers)
                candidates = response.json()
                if candidates['success'] != 1:
                    print("Failed wikidata query -> ", candidates)
                else:
                    for candidate in candidates['search']:
                        qids.append(candidate['id'])
            except Exception as e:
                print("Error querying wikidata url", WD_URL, ":", e)
                            
        wd_qids[data] = qids

    return wd_qids

def get_topk_accuracy(data_to_qid, alg_qids):
    """
    Print top-1, top-3, top-5, top-10, top-inf accuracy 

    :param data_to_qid: Dictionary containing mapping of test mention to correct Wikidata qid
    :type data_to_qid: <class 'dict'>
    :param alg_qids: Dictionary containing mapping of test mention to list of predicted Wikidata qids    
    :type alg_qids: <class 'dict'>

    :returns: Prints top-1, top-3, top-5, top-10, top-inf accuracy
    """

    total_mentions = len(data_to_qid)
    topk  = (0, 0, 0, 0, 0) # Top-1, top-3, top-5, top-10, top-inf
    for mention in data_to_qid:
        correct_qid = data_to_qid[mention]
        qids = alg_qids.get(mention, None)
        if not qids:
            continue
        for i, qid in enumerate(qids):
            if qid == correct_qid: 
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

    print("Top-1 = %.2f, top-3 = %.2f, top-5 = %.2f, top-10 = %.2f, top-inf = %d(%.2f)" 
            % (topk[0]/total_mentions, topk[1]/total_mentions, topk[2]/total_mentions, topk[3]/total_mentions, topk[4], topk[4]/total_mentions))


def run_zero_shot():
    zs_test_filename = os.path.join(config_obj['benchmark']['data_path'], 'zs_test.csv')        

    if not os.path.isfile(zs_test_filename):
        logging.error(f'{zs_test_filename} is not a file. Run "python benchmarks.py" to generate this test data file')
        print(f'{zs_test_filename} is not a file. Run "python benchmarks.py" to generate this test data file')
        exit()
    else:
        data_to_qid = {}
        try:
            zs_test_filename = os.path.join(config_obj['benchmark']['data_path'], 'zs_test.csv')        
            with open(zs_test_filename, 'r') as zero_shot:            
                test = [d.strip() for d in zero_shot.readlines()]
                for row in test:
                    (data, qid) = tuple(row.split('\t'))
                    data_to_qid[data] = qid
        except OSError as exception:
            logging.error(exception)
            exit()
        
        print("Testing on %d mentions" % len(data_to_qid))
        el_qids = run_entity_linking(data_to_qid, context='')
        print("EL with no ctx")
        get_topk_accuracy(data_to_qid, el_qids)
        wd_qids = run_wikidata_autocomplete(data_to_qid)
        print("WD autocomplete")
        get_topk_accuracy(data_to_qid, wd_qids)
        elctx_qids = run_entity_linking(data_to_qid)
        print("EL with ctx=software")
        get_topk_accuracy(data_to_qid, elctx_qids)

def run_few_shot(connection):
    fs_test_filename = os.path.join(config_obj['benchmark']['data_path'], 'fs_test.csv')
    
    if not os.path.isfile(fs_test_filename):
        logging.error(f'{fs_test_filename} is not a file. Run "python benchmarks.py" to generate this test data file')
        print(f'{fs_test_filename} is not a file. Run "python benchmarks.py" to generate this test data file')
        exit()
    else:
        entity_cursor = connection.cursor()

    entity_cursor.execute("SELECT * FROM entities")
    entity_to_eid  = {}
    for entity_tuple in entity_cursor.fetchall():
        entity_id, entity, entity_type_id, external_link = entity_tuple
        entity_to_eid[entity] = entity_id

    data_to_eid = {}
    try:
        with open(fs_test_filename, 'r') as few_shot:            
            test = [d.strip() for d in few_shot.readlines()]
            for row in test:
                (data, eid) = tuple(row.split('\t'))
                data_to_eid[data] = eid
    except OSError as exception:
        logging.error(exception)
        exit()

    mentions  = data_to_eid.keys()
    test_data = ",".join(mentions)

    model_path =config_obj["model"]["model_path"]         
    sim_app    =sim_applier(model_path)
    tech_sim_scores=sim_app.tech_stack_standardization(test_data)    
    num_correct=0
    for mention, entity in zip(mentions, tech_sim_scores):
        correct_eid   = data_to_eid.get(mention, None)     
        predicted_eid = entity_to_eid.get(entity[0], None)
        if not correct_eid:
            print("Mention", mention, "not found in data_to_eid")
        if correct_eid != predicted_eid:
            num_correct += 1
    print("Accuracy = ", num_correct/len(mentions))

config_obj = configparser.ConfigParser()
config_obj.read("./config.ini")

logging.basicConfig(filename='logging.log',level=logging.ERROR, filemode='w')

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
    run_zero_shot()
    run_few_shot(connection)