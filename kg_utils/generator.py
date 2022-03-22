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
import os
import sys
import json
import logging
import sqlite3
import time
from sqlite3 import Error
from sqlite3.dbapi2 import Cursor, complete_statement
from SPARQLWrapper import SPARQLWrapper, JSON

class KG():
    def __init__(self, app_name):
        super().__init__()
        import configparser
        self.app_name  = app_name
        self.config    = configparser.ConfigParser()        
        common         = os.path.join("config", "common.ini")
        kg             = os.path.join("config", "kg.ini")
        self.config.read([common, kg])
        self.connection= None 
        logging.basicConfig(filename=self.app_name+".log",level=logging.DEBUG, \
                        format="[%(levelname)s:%(filename)s:%(lineno)s - %(funcName)20s() ] %(message)s", filemode='w')

    def get_db(self, db_path):
        """
        Create a connection  to Mysqlite3 databade
        
        :param db_path: Path to mysql file
        :type db_path:  .db file 
        
    
        :returns: Connection to mysql db
        :rtype:   <class 'sqlite3.Connection'>

        """
        if not os.path.isfile(db_path):
            logging.error(f'{db_path} is not a file. Run "sh setup.sh" to generate db files')
            print(f'{db_path} is not a file. Run "sh setup.sh" to generate db files')
            exit()
        else:
            try:
                self.connection = sqlite3.connect(db_path)
            except Error as e:
                logging.error(f'{e} cannot create connection to db. Check that the {db_path} is the correct file ')
                print(e)
                exit()

    def get_entities(self):
        entity_types_cursor = self.connection.cursor()
        entity_types_cursor.execute("SELECT * FROM entity_types")
        entity_types = {}
        for entity_types_tuple in entity_types_cursor.fetchall():
            entity_type_id   = entity_types_tuple[0]
            entity_type_name = entity_types_tuple[1]
            entity_types[entity_type_id] = entity_type_name
        
        entity_cursor = self.connection.cursor()
        entity_cursor.execute("SELECT * FROM entities")
        entities      = {"version": self.config["general"]["version"]}
        data          = {}
        idx           = 0
        for entity_tuple in entity_cursor.fetchall():
            entity_data = {}
            entity_data["entity_id"]        = entity_tuple[0]
            entity_data["entity_name"]      = entity_tuple[1]
            entity_data["entity_type_id"]   = entity_tuple[2]
            entity_data["entity_type_name"] = entity_types[entity_tuple[2]]
            entity_data["external_link"]    = entity_tuple[3]
            data[idx] = entity_data 
            idx += 1
            
        entities["data"] = data
        
        return entities
        
    def get_mentions(self):
        entity_cursor = self.connection.cursor()
        entity_cursor.execute("SELECT * FROM entities")
        entities      = {}
        for entity_tuple in entity_cursor.fetchall():
            entities[entity_tuple[0]] = entity_tuple[1]
        
        mention_cursor = self.connection.cursor()
        mention_cursor.execute("SELECT * FROM entity_mentions")    
        mentions       = {"version": self.config["general"]["version"]}
        mapping        = {}
        for mention_tuple in mention_cursor.fetchall():   
            mention_id, mention, entity_type_id, entity_id, source = mention_tuple        
            mention_data = mapping.get(entity_id, {})
            mention_list = mention_data.get(source, [])
            mention_list.append(mention)
            mention_data[source] = mention_list
            mapping[entity_id] = mention_data

        idx  = 0
        data = {}
        for entity_id, mention_data in mapping.items():
            data[idx] = {}
            data[idx]["entity_id"] = entity_id
            mention_data["standardized"] = entities[entity_id]
            data[idx]["mentions"] = mention_data
            idx += 1

        mentions["data"] = data
        return mentions

    def generate_tca(self):
        try:
            kg_dir  = self.config["general"]["kg_dir"]
            db_dir  = self.config["general"]["db_dir"]
            version = self.config["general"]["version"]
            ent_name= self.config["tca"]["entities"]
            men_name= self.config["tca"]["mentions"]            
        except KeyError as k:
            logging.error(f'{k} is not a key in your kg.ini file.')
            print(f'{k} is not a key in your kg.ini file.')
            exit()

        db_path = os.path.join(db_dir, version+".db")
        self.get_db(db_path)

        os.makedirs(kg_dir, exist_ok=True)
        entities = self.get_entities()
        entities_file_name = os.path.join(kg_dir, ent_name)
        with open(entities_file_name, 'w', encoding='utf-8') as entities_file:
            json.dump(entities, entities_file, indent=4)
        mentions = self.get_mentions()
        mentions_file_name = os.path.join(kg_dir, men_name)
        with open(mentions_file_name, 'w', encoding='utf-8') as mentions_file:
            json.dump(mentions, mentions_file, indent=4)

    def create_query(self, qid_type):
        query = """SELECT ?qid ?label WHERE
        {
        ?qid wdt:P31 wd:"""+qid_type+""".
        ?qid rdfs:label ?label
        FILTER(langMatches(lang(?label), \"EN\"))
        } LIMIT 100000"""
        
        return query

            
    def get_results(self, query):
        try:
            query_url       = self.config["wikidata"]["query_url"]
        except KeyError as k:
            logging.error(f'{k} is not a key in your kg.ini file.')
            print(f'{k} is not a key in your kg.ini file.')
            exit()

        # get_wikidata_types()
        user_agent = "External techstack data/%s.%s" % (sys.version_info[0], sys.version_info[1])
        # TODO adjust user agent; see https://w.wiki/CX6
        sparql = SPARQLWrapper(query_url, agent=user_agent)
        sparql.setQuery(query)
        sparql.setReturnFormat(JSON)
        return sparql.query().convert()

            
    def generate_wikidata(self):
        try:
            kg_dir          = self.config["general"]["kg_dir"]
            allow_file_name = self.config["wikidata"]["allowed_types"]
            block_file_name = self.config["wikidata"]["blocked_types"]
            base_url        = self.config["wikidata"]["base_url"]
            query_url       = self.config["wikidata"]["query_url"]
            ent_name        = self.config["wikidata"]["entities"]
            men_name        = self.config["wikidata"]["mentions"]            
        except KeyError as k:
            logging.error(f'{k} is not a key in your kg.ini file.')
            print(f'{k} is not a key in your kg.ini file.')
            exit()

        kg_dir = os.path.join(self.app_name, self.config["general"]["kg_dir"])
        os.makedirs(kg_dir, exist_ok=True)        

        # Read allowed and blocked type files
        try:
            with open(allow_file_name, 'r') as allow:
                allowed_types = json.load(allow)
            with open(block_file_name, 'r') as block:
                blocked_types = json.load(block)
        except Exception as e:
            logging.error("Error reading allowed/blocked types:", e)
            print("Error reading allowed/blocked types:", e)
            
        qid_to_entity = {}
        # types = dict(allowed_types, **blocked_types);
        types = dict(allowed_types)
        for qid_type in types:
            print("Getting entities for", qid_type)
            query = self.create_query(qid_type)
            results = self.get_results(query)
            time.sleep(3)
            for result in results['results']['bindings']:
                qid   = result['qid']['value'].replace(base_url, "")
                label = result['label']['value'] 
                if qid in qid_to_entity:
                    label = qid_to_entity.get(qid, None)
                labels.append(label)
                qid_to_entity[qid] = labels            
                
        entities_file_name = os.path.join(kg_dir, ent_name)
        with open(entities_file_name, 'w', encoding='utf-8') as entities_file:
            json.dump(entities, entities_file, indent=4)
        '''
        mentions_file_name = os.path.join(kg_dir, men_name)
        with open(mentions_file_name, 'w', encoding='utf-8') as mentions_file:
            json.dump(mentions, mentions_file, indent=4)
        '''
        
    def generate(self, task_name):
        if task_name == "tca":
            self.generate_tca()
        elif task_name == "wikidata":
            self.generate_wikidata()
                    
                
if __name__ == "__main__":
    kg = KG("entity_standardizer")
    kg.generate("tca")
    # kg.generate("wikidata")
