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

import json
import requests
import re
import configparser
import logging
import sqlite3
import os
from sqlite3 import Error
from sqlite3.dbapi2 import Cursor, complete_statement
from pathlib import Path
from db import create_db_connection

def find_match(old, candidates):
    old_qid = None
    if old:
        old_qid = old['qid']
    best    = None
    for candidate in candidates:
        qid = candidate[1]
        if qid == old_qid:
            best = candidate
            break

    if old_qid and not best:
        print("No match found for", old, "in", candidates)
        best = [old['name'], old['qid'], [], old['url'], old['score']]
        print(best)
        
    if best:
        new_link = {'name': best[0], 'qid': best[1],'types': best[2], 'url': best[3], 'score': best[4]}
    else:
        new_link = {}

    return new_link


def update_external_link(connection):
    EL_URL  = "http://9.59.199.65:5002/json-example?"
    entity_cursor = connection.cursor()
    entity_cursor.execute("SELECT * FROM entities")

    payload   = []
    old_entities = {}    
    for entity_tuple in entity_cursor.fetchall():
        entity_id, entity, entity_type_id, external_link = entity_tuple
        payload.append({'id': entity_id, 'mention': entity, 'context_left': '', 'context_right': 'software'})
        old_entities[entity_id] = (entity_id, entity, entity_type_id, external_link)

    data_json = json.dumps(payload)
    headers = {'Content-type': 'application/json'}
    try:
        response = requests.post(EL_URL, data=data_json, headers=headers)
        candidates = response.json()
    except Exception as e:
        print("Error querying entity linking url", EL_URL, ":", e)

    new_entities = {}
    for i in candidates:
        cdata = eval(candidates[i]['top_k_entities'])
        new_link = find_match(eval(old_entities[int(i)][3]), cdata)
        new_entities[i] = (old_entities[int(i)][0], old_entities[int(i)][1], old_entities[int(i)][2], new_link)

    for entity_id in new_entities:
        entity = new_entities[entity_id]
        print('INSERT INTO entities VALUES(%d, \'%s\', %d, \'%s\');' % (entity[0], entity[1], entity[2], repr(entity[3]).replace("'", "\'\'")))

config_obj = configparser.ConfigParser()
config_obj.read("./config.ini")

logging.basicConfig(filename='logging.log',level=logging.ERROR, filemode='w')
db_path = config_obj["db"]["db_path"]
if not os.path.isfile(db_path):
    logging.error(f'{db_path} is not a file. Run "sh setup" from /tackle-advise-containerizeation folder to generate db files')
    print(f'{db_path} is not a file. Run "sh setup.sh" from /tackle-advise-containerizeation folder to generate db files')
    exit()

try:
    db_path = config_obj["db"]["db_path"]
except KeyError as k:
    logging.error(f'{k}  is not a key in your config.ini file.')
    print(f'{k} is not a key in your config.ini file.')
    exit()


if not os.path.isfile(db_path):
    logging.error(f'{db_path} is not a valid file. Check your config.ini file for valid file under "db_path" key  ')
    print("{} is not a valid file. Check your config.ini file for valid file under 'db_path' key ".format(db_path))
else:
    connection = create_db_connection(db_path)
    update_external_link(connection)