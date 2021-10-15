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




def create_zero_shot_test(connection):
    """
    Create the test set for zero shot algorithms

    :param connection: A connection to mysql
    :type  connection:  <class 'sqlite3.Connection'>

    :returns: Saves test set to csv file
    """

    entity_cursor = connection.cursor()
    entity_cursor.execute("SELECT * FROM entities")
    eid_to_qid  = {}
    qid_to_data = {}
    data_to_qid = {}
    for entity_tuple in entity_cursor.fetchall():
        entity_id , entity, entity_type_id, external_link = entity_tuple
        external = eval(external_link)
        if not external:
            continue
        qid = external['qid']
        eid_to_qid[entity_id] = eid_to_qid.get(entity_id, qid)
        parts   = entity.split('|')
        mention = None
        i = 1
        while parts[-i] == '*': 
            if i >= len(parts):
                break
            i += 1
        mention = parts[-i]
        if not mention:
            continue
        mention = clean(mention)
        if not is_ascii(mention):
            logging.warning(f"Mention {mention} has non-ascii characters: {' '.join([c for c in mention if ord(c) >= 128])} {[hex(ord(c)) for c in mention if ord(c) >= 128]}")
        qid_to_data[qid]      = qid_to_data.get(qid, []) + [(mention, entity_id)]
        if mention in data_to_qid:
            if data_to_qid[mention] != qid:
                logging.error(f"Conflict: {mention} -> {qid} vs. {data_to_qid[mention]}")
            else:
                logging.warning(f"Duplicate: {mention} -> {qid}")
        else:
            data_to_qid[mention] = qid

    mention_cursor = connection.cursor()
    mention_cursor.execute("SELECT * FROM entity_mentions")    
    for mention_tuple in mention_cursor.fetchall():        
        mention_id, mention, entity_type_id, entity_id, source = mention_tuple        
        qid = eid_to_qid.get(entity_id, None)
        if not qid:
            continue
        mention = clean(mention)    
        if not is_ascii(mention):
            logging.warning(f"Mention {mention} has non-ascii characters: {' '.join([c for c in mention if ord(c) >= 128])} {[hex(ord(c)) for c in mention if ord(c) >= 128]}")
        qid_to_data[qid] = qid_to_data.get(qid, []) + [(mention, mention_id)]
        if mention in data_to_qid:
            if data_to_qid[mention] != qid:
                logging.error(f"Conflict: {mention} -> {qid} vs. {data_to_qid[mention]}")
            else:
                logging.warning(f"Duplicate: {mention} -> {qid}")
        else:
            data_to_qid[mention] = qid

    try:
        os.makedirs(config_obj['benchmark']['data_path'], exist_ok=True)
        zs_test_filename = os.path.join(config_obj['benchmark']['data_path'], 'zs_test.csv')
        num_test = 0
        with open(zs_test_filename, 'w') as zero_shot:
            for mention, qid in data_to_qid.items():
                zero_shot.write("%s\t%s\n" % (mention, qid))
                num_test += 1
    except OSError as exception:
        logging.error(exception)
        exit()
    print(f"---------------------------------------------")
    print(f"{len(eid_to_qid)} entities have qids.")
    print(f"{len(qid_to_data)} qids have data.")
    print(f"Zero shot benchmark has {num_test} mentions.")
    print(f"---------------------------------------------")

def get_data_histogram(y_data, max_eid):
    unique, counts = np.unique(y_data, return_counts=True)
    num_zero = 0
    for eid in range(max_eid):
        if eid not in unique:
            num_zero += 1
    unique, counts = np.unique(counts, return_counts=True)
    num_mens = [0] + list(unique)
    num_ents = [num_zero] + list(counts)
    data_hist = {}
    for mc, ec in zip(num_mens, num_ents):
        data_hist[mc] = ec    

    return data_hist

def create_few_shot_test(connection):
    """
    Create the train, test set for few shot algorithms

    :param connection: A connection to mysql
    :type  connection:  <class 'sqlite3.Connection'>

    :returns: Saves train, test set to csv file
    """
    eid_to_name = {}
    entity_cursor = connection.cursor()
    entity_cursor.execute("SELECT * FROM entities")    
    for entity_tuple in entity_cursor.fetchall():
        entity_id , entity, entity_type_id, external_link = entity_tuple
        eid_to_name[entity_id] = entity

    eid_to_data = {}
    mention_cursor = connection.cursor()
    mention_cursor.execute("SELECT * FROM entity_mentions")    
    for mention_tuple in mention_cursor.fetchall():        
        mention_id, mention, entity_type_id, entity_id, source = mention_tuple        
        eid_to_data[entity_id] = eid_to_data.get(entity_id, []) + [mention]

    data_to_eid = {}
    x_data      = []
    y_data      = []
    for eid in eid_to_data:
        mentions = eid_to_data[eid]
        for mention in mentions:
            mention = clean(mention)
            if not is_ascii(mention):
                logging.warning(f"Mention {mention} has non-ascii characters: {' '.join([c for c in mention if ord(c) >= 128])}, {[hex(ord(c)) for c in mention if ord(c) >= 128]}")
            if mention in data_to_eid:
                if data_to_eid[mention] != eid:
                    logging.error(f"Conflict: {mention} -> {eid} ({eid_to_name[eid]}) vs. {data_to_eid[mention]} ({eid_to_name[data_to_eid[mention]]})")
                else:
                    logging.warning(f"Duplicate: {mention} -> {eid}")
            else:
                data_to_eid[mention] = eid
                x_data.append(mention)
                y_data.append(eid)

    data_hist = get_data_histogram(y_data, len(eid_to_name))
    logging.info(f"Mention data histogram = {data_hist}")

    x_train, x_test, y_train, y_test = train_test_split(x_data, y_data, test_size=0.33, random_state=42)

    try:
        os.makedirs(config_obj['benchmark']['data_path'], exist_ok=True)
        fs_train_filename = os.path.join(config_obj['benchmark']['data_path'], 'fs_train.csv')        
        with open(fs_train_filename, 'w') as few_shot:
            for (x,y) in zip(x_train, y_train):
                few_shot.write("%s\t%d\n" % (x, y))
        fs_test_filename = os.path.join(config_obj['benchmark']['data_path'], 'fs_test.csv')        
        with open(fs_test_filename, 'w') as few_shot:
            for (x,y) in zip(x_test, y_test):
                few_shot.write("%s\t%d\n" % (x, y))
    except OSError as exception:
        logging.error(exception)
        exit()

    print(f"---------------------------------------------")
    ent_hist  = list(data_hist.values())
    print(f"{sum(ent_hist[1:])} entities have at least one mention.")
    print(f"Few shot benchmark train size = {len(x_train)}")
    print(f"Few shot benchmark test size = {len(x_test)}")
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
        # create_zero_shot_test(connection)
        # create_few_shot_test(connection)