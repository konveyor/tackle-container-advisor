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
import re
import configparser
import logging
import sqlite3
import os
from sqlite3 import Error
from sqlite3.dbapi2 import Cursor
from pathlib import Path



config_obj = configparser.ConfigParser()
config_obj.read("./config.ini")

os.chdir('..')

def cleanStrValue(value):
    """
    Clean input strings   

    :param value: input string
    :returns: value
    
    """
    if value:
        value = str(value).strip()
        value = value.replace(u'\u00a0', ' ')
        value = re.sub(r'[^\x00-\x7F]+', ' ', ' ' + str(value) + ' ').strip()
    else:
        value = ''
    return value





def load_class_type(conn):

    """Maps each entity to the corresponding type

    :param conn:  A connection to mysql
    :type conn:  <class 'sqlite3.Connection'>

    :returns: {'1': 'Lang', '2': 'Lib', '3': 'App Server', '4': 'Runtime', '5': 'App', '6': 'OS'}
    :rtype: dict

    
    """

    map_types = {}

    cursor    = conn.cursor()
    cursor.execute("SELECT * FROM  entity_types")
    entity_types = cursor.fetchall()

    for ent_type in entity_types:
        map_types[str(ent_type[0])] = ent_type [1]

    return map_types



def load_entity_names(db_connection):
    
    """
    Method to load entity names from "entities" table from mysql db 

    :param db_connection: A connection to mysql
    :type db_connection:  <class 'sqlite3.Connection'>

    :returns: A dictionary of entity_names
    :rtype: dict 

    """

    entity_names = {}
    cur = db_connection.cursor()
    cur.execute("SELECT * FROM entities")
    entities = cur.fetchall()
    for entity in entities:
        entity_names[str(entity[0])] = entity[1]
    
    return entity_names



def createClassTypeMapper(db_connection):
    
    """
    Method to extract Entities from sql db and create  mapping each entity to the  corresponding type ("APP, APP SERVER , RUNTIME , LANG , LIB, OS)

    :param db_connection: A connection to mysql
    :type db_connection:  <class 'sqlite3.Connection'>


    :returns: Saves entity_mentions  in config_obj["kg"]["class_type_mapper_raw"]
    :retype: None
    """

    entity_mentions = {}
    entity_mentions["kg_version"] = config_obj["db"]["version"]
    entity_mentions["mappings"] = {}

    types_ = load_class_type(db_connection)
    entity_names = load_entity_names(db_connection) 
    
    cursor = db_connection.cursor()
    cursor.execute("SELECT * FROM  entity_mentions")   
    mentions = cursor.fetchall()
    
    

    for mention in mentions:
        class_type = types_[str(mention[2])]
        index = str(mention[3])
        entity = entity_names[index]
        entity_mentions["mappings"][entity] = class_type
    
    path =  fr'aca_kg_utils/{config_obj["kg"]["ontologies"]}'  
    dst_pth = fr'aca_backend_api/{config_obj["kg"]["ontologies"]}'

    if not os.path.isdir(path):
        os.mkdir(path)
       
    if not os.path.isdir(dst_pth) :
        os.mkdir(dst_pth)

    with open(path + config_obj["kg"]["class_type_mapper"], 'w') as mapper:
        mapper.write(json.dumps(entity_mentions , indent= 2))



def create_db_connection(db_file):
    """
    Create Mysql db connection

    :param db_file: path to mysql file
    :type db_file:  .db file

    :returns: Connection to mysql db

    :rtype:  <class 'sqlite3.Connection'>

    """

    connection = None

    try:
        connection = sqlite3.connect(db_file)
    except Error as e:
        logging.error(f'{e}: Issue connecting to db. Please check whether the .db file exist in the {db_path} path')
        print(e)
    return connection



if __name__== '__main__':


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
        createClassTypeMapper(connection)
        
        
        
    
        


    



    


    


