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
        u'\xd8'  : u'',     # Latin Capital letter O with stroke
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
    for entity_tuple in entity_cursor.fetchall():
        entity_id , entity, entity_type_id, external_link = entity_tuple
        external = eval(external_link)
        if external:
            qid = external['qid']
            eid_to_qid[entity_id] = eid_to_qid.get(entity_id, qid)
            qid_to_data[qid]      = qid_to_data.get(qid, []) + [(entity, entity_id)]

    mention_cursor = connection.cursor()
    mention_cursor.execute("SELECT * FROM entity_mentions")    
    for mention_tuple in mention_cursor.fetchall():        
        mention_id, mention, entity_type_id, entity_id, source = mention_tuple        
        qid = eid_to_qid.get(entity_id, None)
        if qid:
            qid_to_data[qid].append((mention, mention_id))

    try:
        os.makedirs(config_obj['benchmark']['data_path'], exist_ok=True)
        zs_test_filename = os.path.join(config_obj['benchmark']['data_path'], 'zs_test.csv')
        with open(zs_test_filename, 'w') as zero_shot:
            for qid in qid_to_data:
                for d in qid_to_data[qid]:
                    mention    = d[0]
                    mention_id = d[1]
                    mention = clean(mention)
                    if not is_ascii(mention):
                        print("(W) Mention %d has non-ascii characters: %s" % 
                                        (mention_id, " ".join([c for c in mention if ord(c) >= 128])), [hex(ord(c)) for c in mention if ord(c) >= 128])
                    zero_shot.write("%s\t%s\n" % (mention, qid))
    except OSError as exception:
        logging.error(exception)
        exit()

    print(len(eid_to_qid), "entities have qids.")
    print(len(qid_to_data), "qids have data.")


def create_few_shot_test(connection):
    """
    Create the train, test set for few shot algorithms

    :param connection: A connection to mysql
    :type  connection:  <class 'sqlite3.Connection'>

    :returns: Saves train, test set to csv file
    """

    '''
    entity_cursor = connection.cursor()
    entity_cursor.execute("SELECT * FROM entities")
    eid_to_qid  = {}
    qid_to_data = {}
    for entity_tuple in entity_cursor.fetchall():
        entity_id , entity, entity_type_id, external_link = entity_tuple
        external = eval(external_link)
        if external:
            qid = external['qid']
            eid_to_qid[entity_id] = eid_to_qid.get(entity_id, qid)
            qid_to_data[qid]      = qid_to_data.get(qid, []) + [(entity, entity_id)]
    '''

    eid_to_data = {}
    mention_cursor = connection.cursor()
    mention_cursor.execute("SELECT * FROM entity_mentions")    
    for mention_tuple in mention_cursor.fetchall():        
        mention_id, mention, entity_type_id, entity_id, source = mention_tuple        
        mentions = eid_to_data.get(entity_id, [])
        mentions.append(mention)
        eid_to_data[entity_id] = mentions

    x_data = []
    y_data = []
    for eid in eid_to_data:
        mentions = eid_to_data[eid]
        for mention in mentions:
            mention = clean(mention)
            if not is_ascii(mention):
                print("(W) Mention %s has non-ascii characters: %s" % 
                    (mention, " ".join([c for c in mention if ord(c) >= 128])), [hex(ord(c)) for c in mention if ord(c) >= 128])
            x_data.append(mention)
            y_data.append(eid)
    
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

    print(len(eid_to_data), "entities have at least one mention.")


config_obj = configparser.ConfigParser()
config_obj.read("config.ini")

logging.basicConfig(filename='logging.log',level=logging.ERROR, filemode='w')

try:
    db_path = config_obj["db"]["db_path"]
except KeyError as k:
    logging.error(f'{k}  is not a key in your config.ini file.')
    print(f'{k} is not a key in your config.ini file.')
    exit()

if not os.path.isfile(db_path):
    logging.error(f'{db_path} is not a file. Run "sh setup" from /tackle-advise-containerizeation folder to generate db files')
    print(f'{db_path} is not a file. Run "sh setup.sh" from /tackle-advise-containerizeation folder to generate db files')
    exit()
else:
    connection = create_db_connection(db_path)
    create_zero_shot_test(connection)
    create_few_shot_test(connection)