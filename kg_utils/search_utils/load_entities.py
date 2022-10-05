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


from sqlite3 import Error
import sqlite3

import configparser
import os
import re
import logging
from . import utils



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
        return entity.split('|*')[0].strip()

    elif match_less_greater_sign:

        if "|" in entity.split("<>")[1]:
            return entity.split("<>")[1].split("|")[-1].strip()
        return(entity.split("<>")[1].strip())

    elif match_abbreviation:
        if entity.startswith("("):  
            return entity.strip()
        elif ('|') in   entity.split("(")[0]:

            n_ent = entity.split("(")[0].split('|')[-1]
            return  n_ent.strip()
        else: 
            return entity.split("(")[0].strip()
    elif match_pipe_only and '|*' not in entity:

        num = entity.count("|")
        ent = ''
        if num > 1:
            ent = entity.split("|")[-1]
        else: 
            ent = entity.split('|')[1]
        return ent.strip()
    else: 
        return entity.strip()



def all_OS_from_db():
    """
    Load all entities of type OS
    """
    os_cursor = utils.get_table(table_name="entities")

    OS= {}

    for entity  in os_cursor.fetchall():
        if entity[2] == 6:
            os = filter_entity(entity[1])
            OS[str(entity[0])] = os

    os_cursor.close()

    return OS



def from_database(  entity_names = None, table_name="entities"):

    """
    Load entity names from the main database.

    Returns:
        list: A list containing tuple( entity_name , entity_type_id , entity_name_id)
    """
    if entity_names == None :
        print("No entities selected")
        exit()
    entities = []
    suggest_entities = []
    cursor = utils.get_table(table_name="entities")

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

    cursor.close()

    return entities ,  suggest_entities