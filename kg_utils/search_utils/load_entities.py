################################################################################
# Copyright IBM Corporation 2021, 2022
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
################################################################################


from curses import resetty
from hashlib import new
from openpyxl import load_workbook
from sqlite3 import Error
import sqlite3

import configparser
import os
import re
import logging


#config file
config = configparser.ConfigParser()
config_data = os.path.join("config/kg.ini")
config.read([config_data])


def create_db_connection(database_path):
    """
    Create connection to database

    Args:

        database_path (str): path to the database

    Returns:

        _type_: sqlite3 connection 

    """
    
    connection = None

    try:
        connection = sqlite3.connect(database_path)
    except Error as e:
        logging.error(f'{e}: Issue connecting to db. Please check whether the .db file exists.')

   
    return connection


def filter_entity(entity:str)-> str:
    """
    Remove pipes(|) or pipe stars (|*) or entity_prefix pipe (i.e Linux|ubuntu) from entity names

    Args:
        entity (str): entity to filter

    Returns:
        str: filtered entity
    """
    match_pipe_star = re.findall(r'\|\*', entity)
    match_less_greater_sign = re.findall(r'\<\>' , entity)
    match_abbreviation = re.findall(r'[\)]' , entity)
    match_pipe_only = re.findall(r'\|', entity)

    if match_pipe_star : 
        return entity.split('|*')[0]

    elif match_less_greater_sign:

        if "|" in entity.split("<>")[1]:
            return entity.split("<>")[1].split("|")[-1]
        return(entity.split("<>")[1])

    elif match_abbreviation:
        if entity.startswith("("):  
            return entity
        elif ('|') in   entity.split("(")[0]:

            n_ent = entity.split("(")[0].split('|')[-1]
            return  n_ent
        else: 
            return entity.split("(")[0]
    elif match_pipe_only and '|*' not in entity:

        num = entity.count("|")
        ent = ''
        if num > 1:
            ent = entity.split("|")[-1]
        else: 
            ent = entity.split('|')[1]
        return ent
    else: 
        return entity

def from_database(  entity_names = None, table_name="entities"):

    """
    Load entity names from the main database.

    Returns:
        list: A list containing tuple( entity_name , entity_type_id , entity_name_id)
    """
    if entity_names == None :
        print("No entities selected")
        exit()

    db_path    =  config["database"]["database_path"]
    
    connection =   create_db_connection(db_path)

    entities = []
    suggest_entities = []
    cursor = connection.cursor()
    
    cursor.execute("SELECT   *  FROM {} ".format(table_name))
    for entity  in cursor.fetchall():
    

        if entity_names == "all": 
            entity_name = filter_entity(entity[1]) 
            entities.append( (entity_name.strip(),entity[2] , entity[0]) )

        else: 

            for name in entity_names:
                
                if entity[1].lower() == name.lower():
                    
                    entity_name = filter_entity(entity[1])
                    entities.append( (entity_name.strip(),entity[2] , entity[0]) )

                elif name.lower() in entity[1].lower():
                    print(entity[1])
                    suggest_entities.append(entity[1])

                else: continue

    return entities ,  suggest_entities