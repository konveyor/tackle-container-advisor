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
import numpy as np
from sqlite3 import Error
from sqlite3.dbapi2 import Cursor, complete_statement
from pathlib import Path
from db import create_db_connection
from sklearn.model_selection import train_test_split

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


def is_ascii(s):
    """
    Checks if 's' contains only ascii characters
    :param s: String to check for ascii characters
    :type  s: string

    :returns: Return True if string contains only ascii characters, else returns False
    """

    return all(ord(c) < 128 for c in s)


def create_train_test_sets(connection):
    """
    Create the train set using mentions from Wikipedia anchor text
    and test set using mentions from 'other' sources

    :param connection: A connection to mysql
    :type  connection:  <class 'sqlite3.Connection'>

    :returns: Saves train and test sets to csv files
    """
    eid_to_qid  = {}
    data_to_ids = {}
    total = 0
    no_external = 0
    no_mention  = 0
    no_qid   = 0

    entity_cursor = connection.cursor()
    entity_cursor.execute("SELECT * FROM entities")
    for entity_tuple in entity_cursor.fetchall():
        total += 1
        entity_id , entity, entity_type_id, external_link = entity_tuple
        external = eval(external_link)
        if not external:
            no_external += 1
            continue
        wiki_id = external['qid']
        eid_to_qid[entity_id] = eid_to_qid.get(entity_id, wiki_id)
        parts   = entity.split('|')
        mention = None
        i = 1
        while parts[-i] == '*': 
            if i >= len(parts):
                break
            i += 1
        mention = parts[-i]
        if not mention:
            no_mention += 1
            continue
        mention = clean(mention)
        if not is_ascii(mention):
            logging.warning(f"Mention {mention} has non-ascii characters: {' '.join([c for c in mention if ord(c) >= 128])} {[hex(ord(c)) for c in mention if ord(c) >= 128]}")
        if mention in data_to_ids:
            (eid, qid, src) = data_to_ids[mention]
            if eid != entity_id or qid != wiki_id:
                logging.error(f"Conflict: {mention} -> {eid} vs. {entity_id}, {qid} vs. {wiki_id}")
            else:
                logging.warning(f"Duplicate: {mention} -> {eid}, {qid}")
        else:
            data_to_ids[mention] = (entity_id, wiki_id, 'class')

    mention_cursor = connection.cursor()
    mention_cursor.execute("SELECT * FROM entity_mentions")    
    for mention_tuple in mention_cursor.fetchall():   
        total += 1     
        mention_id, mention, entity_type_id, entity_id, source = mention_tuple        
        wiki_id = eid_to_qid.get(entity_id, None)
        if not wiki_id:
            no_qid += 1
            continue
   
        mention = clean(mention)    
        if not is_ascii(mention):
            logging.warning(f"Mention {mention} has non-ascii characters: {' '.join([c for c in mention if ord(c) >= 128])} {[hex(ord(c)) for c in mention if ord(c) >= 128]}")
        if mention in data_to_ids:
            (eid, qid, src) = data_to_ids[mention]
            if eid != entity_id or qid != wiki_id:
                logging.error(f"Conflict: {mention} -> {eid} vs. {entity_id}, {qid} vs. {wiki_id}")
            else:
                logging.warning(f"Duplicate: {mention} -> {qid}")
        else:
            data_to_ids[mention] = (entity_id, wiki_id, source)

    try:
        os.makedirs(config_obj['benchmark']['data_path'], exist_ok=True)
        train_filename = os.path.join(config_obj['benchmark']['data_path'], 'train.csv')
        test_filename  = os.path.join(config_obj['benchmark']['data_path'], 'test.csv')
        num_train= 0
        num_test = 0
        with open(test_filename, 'w') as test, open(train_filename, 'w') as train:
            for mention, (eid, qid, src) in data_to_ids.items():
                if src == 'others':
                    if not qid:
                        continue
                    test.write("%s\t%d\t%s\n" % (mention, eid, qid))
                    num_test += 1
                else:
                    train.write("%s\t%d\n" % (mention, eid))
                    num_train += 1
    except OSError as exception:
        logging.error(exception)
        exit()
    print(f"---------------------------------------------")
    print(f"{len(eid_to_qid)} entities have qids.")
    print(f"{len(data_to_ids)} mentions collected.")
    print(f"{no_external} mentions have no external link.")
    print(f"{no_qid} mentions have no qid.")
    print(f"{no_mention} mentions are empty.")
    print(f"{num_train} mentions added to train set.")
    print(f"{num_test} mentions added to test set.")
    print(f"---------------------------------------------")

config_obj = configparser.ConfigParser()
config_obj.read("config.ini")

logging.basicConfig(filename='logging.log',level=logging.DEBUG, \
                    format="[%(levelname)s:%(filename)s:%(lineno)s - %(funcName)20s() ] %(message)s", filemode='w')

if __name__ == '__main__':
    try:
        db_path = config_obj["db"]["db_path"]
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
        create_train_test_sets(connection)