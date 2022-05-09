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

from collections import defaultdict
import os
import csv
import re
import sqlite3
from sqlite3 import Error

from .utils_nlp import utils 

class sim_utils:

    
    @staticmethod
    def load_class_type(db_connection):
        
        """
        Load class types from the "entity_types" table"
        
        
        :param db_connection: Connection to mysqlite database
        :type db_connection: <class 'sqlite3.Connection'>


        :returns: A dictionary of class types. i.e  {'1': 'Lang', '2': 'Lib', '3': 'App Server', '4': 'Runtime', '5': 'App', '6': 'OS'}
        :rtype: dict

        
        """
    
        map_types = {}
        cursor    = db_connection.cursor()
        cursor.execute("SELECT * FROM  entity_types")
        entity_types = cursor.fetchall()

        for ent_type in entity_types:
            map_types[str(ent_type[0])] = ent_type [1]

        return map_types


    @staticmethod
    def load_entity_names (db_connection):
        """ 
        Retrieve entity names from mysql db
        
        :param db_connection: connection to mysqlite database
        :type db_connection:  <class 'sqlite3.Connection'>

        :returns:  entity names, a dictionary of all instances where  keys are indexes and values  represent entity names
        :rtype: dict


        """

        entity_names = {}
        cur = db_connection.cursor()
        cur.execute("SELECT * FROM entities")
        entities = cur.fetchall()
        for entity in entities:
            entity_names[str(entity[0])] = entity[1]
        
        return entity_names



    
    @staticmethod
    def load_entities(db_connection):
        """
        Loads instances from db
        
        
        :param db_connection: connection to mysql database
        :type db_connection:  <class 'sqlite3.Connection'>


        :returns:  mention_data representing instances required to train the models. Example: [['Ansible', 'ansible', 'ansible'], ['Apache ActiveMQ', 'Apache ActiveMQ', 'Apache ActiveMQ'] , ...]
        :rtype: list
        """

        class_types = sim_utils.load_class_type(db_connection)

        entity_names = sim_utils.load_entity_names(db_connection) 
        mention_data= []
        cur = db_connection.cursor()
        cur.execute("SELECT * FROM entity_mentions")
        mentions = cur.fetchall()

        for entity_mention in mentions:
            index = str(entity_mention[3])
            entity_class = entity_names[index]
            class_type = class_types[str(entity_mention[2])]

            if [entity_class, entity_mention[1] , entity_mention[1]] in mention_data:
                print("duplicate:",[entity_class, entity_mention[1]])
                continue

            mention_data.append([entity_class, entity_mention[1] , entity_mention[1]])
        

        return mention_data

    
   
    @staticmethod
    def text_collection_kg(all_instances):
        """
        Collets text from each instance
        
        
        :param all_intances: Instances for building the model'
        :type all_instances: list

        :returns: Collected texts from each instance
        :rtype: list

        """
        texts = []
        for each_instance in all_instances:
            cat, variants,keywords=each_instance
            cat_name=cat.split("|")
            if len(cat_name)>1:
                subcat=cat_name[len(cat_name)-1]
            else:
                subcat=cat_name[0]
            text_entry=variants+" "+keywords +" "+ subcat+" "+cat_name[0]  # model0 0.94 accuracy0.81 best
            text=utils.my_tokenization0(text_entry.strip().lower())
            texts.append(text)
        threshold=0
        texts=utils.remove_low_frequency_token(texts,threshold)
        return texts
        
    @staticmethod
    def text_collection_kg_without_tokenization(all_instances):
        """
        Tokenize each instance
        
        :param all_instances: list containing all instances
        :type all_instances: list

        :return texts: token for  each instance
        :rtype: list

        """
        texts = []
    
        for each_instance in all_instances:
            cat, variants,keywords=each_instance
            cat_name=cat.split("|")
            if len(cat_name)>1:
                subcat=cat_name[len(cat_name)-1]
            else:
                subcat=cat_name[0]

            text_entry=keywords # test spacy model0 0.94 accuracy0.81 best
            text=utils.my_tokenization0_str(text_entry.strip().lower())
            texts.append([text])
         
        threshold=0
        texts=utils.remove_low_frequency_token(texts,threshold)
        return texts


    @staticmethod
    def text_collection_kg_without_tokenization4vector(all_instances):
        """
        Collect instances without tokenization

        :param all_instances: list of list containing all instances
        :type all_instances: list
        
        :returns: A collection of texts from each instance
        :rtype: dict
            
        """
    
        texts ={}
        id=0
        for each_instance in all_instances:
            cat, variants,keywords=each_instance
            cat_name=cat.split("|")
            if len(cat_name)>1:
                subcat=cat_name[len(cat_name)-1]
            else:
                subcat=cat_name[0]
            text_entry=variants+" "+keywords +" "+ subcat+" "+cat_name[0]  # model0 0.94 accuracy0.81 best
            texts[text_entry]=text_entry 
            id+=1
        return texts
 


