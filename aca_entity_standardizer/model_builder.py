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


import string
import pickle
import os
from sklearn.feature_extraction.text import TfidfVectorizer
from utils_nlp import  utils
from sim_utils import sim_utils
import configparser
import sqlite3
from sqlite3 import Error
import logging
from time import time

 
config_obj = configparser.ConfigParser()
config_obj.read("config.ini")

# os.chdir('..')
    
def buildModel(model_path, connection):

    """
    Build model for: vectorizer_name ,standardization_model , instances_names 


    :param model_path: Path to save models
    :type model_path: path
    :param connection: A connection to mysql
    :type  connection:  <class 'sqlite3.Connection'>


    :returns: Saves all models to pickle files

    """ 
        
    vectorizer_name = "standardization_vectorizer.pickle"
    standardization_model="standardization_model.pickle"
    instances_name="standardization_dict.pickle"

    all_instances   =  sim_utils.load_entities(connection)

    all_targets    =  sim_utils.text_collection_kg_without_tokenization4vector(all_instances)
   
    tfidf = TfidfVectorizer(token_pattern=r"(?u)\b\w+\b").fit(all_targets)
  
    
    tfs = tfidf.fit_transform(all_targets)

    pickle.dump(tfs, open(model_path+vectorizer_name, "wb"))
    pickle.dump(tfidf, open(model_path+standardization_model,"wb"))
    pickle.dump(all_instances, open(model_path+instances_name,"wb"))




def create_db_connection(db_file):

    """
    Create a connection  to Mysqlite3 databade

    :param db_file: Path to mysql file
    :type db_file:  .db file 
    
    
    :returns: Connection to mysql db
    :rtype:   <class 'sqlite3.Connection'>

    """

    connection = None
    try:
        connection = sqlite3.connect(db_file)

    except Error as e:
        logging.error(f'{e} cannot create connection to db. Check that the {db_file} is the correct file ')
        print(e)
        exit()

    return connection
         

if __name__ == "__main__":

    logging.basicConfig(filename='logging.log',level=logging.ERROR, filemode='w')

    db_ky = "db"
    db_pth = "db_path"
    model_ky = "model"
    model_pth = "model_path"

    try:
        db_path = config_obj[db_ky][db_pth]
    except KeyError as k:
        logging.error(f'{k} is not a  valid key in config.ini file. Also, Run "sh setup" from /tackle-advise-containerizeation folder to generate db files')
        print(f'{k} is not a valid key in config.ini file.Also, Run "sh setup" from /tackle-advise-containerizeation folder to generate db files')
        exit()

    db_path = config_obj[db_ky][db_pth]

    if not os.path.isfile(db_path):
        logging.error(f'{db_path} is not a file. Run "sh setup" from /tackle-advise-containerizeation folder to generate db files')
        print(f'{db_path} is not a file. Run "sh setup.sh" from /tackle-advise-containerizeation folder to generate db files')
        exit()

    
    
    if not os.path.isfile(db_path):
        logging.error(f'{db_path} does not exits. Make sure {db_path} contains a db file. Check config.ini file')
        print(f'{db_path} does not exits. Make sure {db_path} contains a db file. Check config.ini file ')
        exit()

    connect = create_db_connection(db_path)


    model_path = config_obj[model_ky][model_pth]


    if not os.path.isdir(model_path):
        os.mkdir(model_path)

    start = time()
    buildModel(model_path, connect)
    end   = time()
    print(f"TFIDF training took {end-start:.2f} seconds.")
    logging.info(f"TFIDF training took {end-start:.2f} seconds.")
