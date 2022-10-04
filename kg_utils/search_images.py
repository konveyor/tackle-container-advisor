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


import sys
sys.path.append("./kg_utils")
import json
import logging
import os
import configparser
import argparse
import json

from textwrap import indent
from dotenv import load_dotenv ,find_dotenv
from search_utils  import load_entities , utils , save_to_csv , dockerhub , quay , operator


def save_to_kb(results: list) -> None:
    """
    Save search results as a JSON file to \kb directory 
    Args:
        results (dict): dictionary containing search results from Dockerhub , Quay , and Operatorhub.io
    """
   
    with open("kg_utils/image_search_kg/images.json", "w" , encoding="utf-8") as images_file:
        images_file.write(json.dumps(results, indent=2))

    
def search(entities: list) ->list:
    """
    list of all entities
    Args:
        entities (list): All entities
    """

    search_result = []
    for _, entity in enumerate(entities):

        entity_name =  entity[0]
        entity_type =  entity[1]
        entity_id   =  entity[2]

        if entity_name=='':
            continue
       
        entity_dict = {entity_name: [] , "entity_type": entity_type, "entity_id": entity_id}

        print({"entity_name": entity_name , "entity_type": entity_type, "entity_id": entity_id})

    
        dockerhub_images = { 'dockerhub_exact_images':[] , 'dockerhub_top_images': []}
        quay_images = { 'quay_exact_images':[] , 'quay_top_images': []}
        operator_images = {"operators": []}
        


        exact_docker_image  = docker_.search_dockerhub_images(entity_name)[0]
        top_docker_images   = docker_.search_dockerhub_images(entity_name)[1]
        exact_quay_image    = quay.search_images(entity_name)[0]
        top_quay_images     = quay.search_images(entity_name)[1]
        operatorhub_images  = operator_.community_operators(entity_name)


        for operator_image in operatorhub_images:
            operator_images["operators"].append(operator_image)

        for exact in exact_docker_image: 
            dockerhub_images['dockerhub_exact_images'].append(exact)
        
        for top_im in top_docker_images:
            dockerhub_images['dockerhub_top_images'].append(top_im)

        for q_exact in exact_quay_image: 
            quay_images['quay_exact_images'].append(q_exact)
        
        for q_top_im in top_quay_images:
            quay_images['quay_top_images'].append(q_top_im)

        entity_dict[entity_name] =[dockerhub_images, quay_images , operator_images]

        search_result.append(entity_dict)
    
    return search_result
   


def cmdline_args():

    """
    input arguments 
    
    Keyword arguments: None
    argument -- None
    Return: A parser containing input arguments
    """
    
        
    p = argparse.ArgumentParser(prog="search_images" , usage="Search container images  from dockerhub , Quay.io , and Artifacthub.io")

    p.add_argument("-e", "--entity", type = str , help="Enter entity name(s) from the database . i.e :  -e nginx,tomcat,ubuntu  or -e all  ( to search all entities). \
        Also enclose entities with double words in a quote. For example:  -e  'ibm i',db2,'Apache Kafka'  ")

    p.add_argument("-db", "--database_path" , type = str, help="path containing the latest tackle containerization  advisor database")

    return(p.parse_args())


def get_entities():

    """
    load entities from database
    Keyword arguments: None
    argument -- None 
    Return: list of valid  entities  from db 
    """
    
    print("Enter entity(ies) from the entity_name table to search for matching container images\n")

    try:
        args = cmdline_args()  
    except:
        print('Try $python    -e <entity_names>    -db <database_path"> or type $python  src/search_images.py --help')
        exit()

    if args.entity == 'all':
  
        entities , suggest_entities    =load_entities.from_database(entity_names='all')

    elif args.entity != 'all':

        entity_names= args.entity.split(",") 

        entities , suggest_entities    = load_entities.from_database( entity_names = entity_names)
       
     
    else:
        print('Try $python    -e <entity_names>    -db <database_path"> or type $python  src/search_images.py --help')
        exit() 

    if entities == [] and args.entity !='all' :
        print("No entity names found for {}. Enter a valid entity from the database.\n".format(args.entity))
    
        
    if len(suggest_entities) != 0: 
    
        print("Some entities from {} could not be found. Did you mean the following entity(ies) \n".format( args.entity.split(',')))
        for ent in suggest_entities:
            print("{} \n".format(ent))

        print("Enter a valid entity from the entities table")
        exit()

    return entities
    
      

if __name__ == "__main__":
    
    entities  = get_entities()
    docker_   = dockerhub.DockerHubSearch()
    quay      = quay.Quay()
    operator_ = operator.Operators()
    results   = search(entities)
   
    save_to_kb(results)
    save_to_csv.docker_images()
    save_to_csv.operator_images()
    save_to_csv.openshift_images()