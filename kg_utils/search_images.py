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
#from tkinter import image_names
sys.path.append("/app")

import argparse
from audioop import tomono
from encodings import search_function
from search_utils import load_entities , dockerhub_api , utils , save_to_csv
import json
import requests
import json
import itertools
import operator
import logging
import re  
import os
import docker
import configparser
import time

#config file
config = configparser.ConfigParser()
config_data = os.path.join("/app/config/kg.ini")
config.read([config_data])

#loggger
logger = logging.getLogger('search')
logger.setLevel(logging.INFO)


#search sessions
operator_session = requests.Session()
quay_session = requests.Session()


#load list of verified and official publishers
with open("image_search_kg/verified_publisher_names.json", "r", encoding="utf-8") as verified_file:
    verified_publishers = json.load(verified_file)

class Operators():

    def __init__(self):

        self.api = "https://artifacthub.io/api/v1/" 
        self.package_query = "packages/search?org=operator-framework&repo=community-operators&ts_query_web=&limit=60&offset="
    

    def remove_tags(self, image_link:str)-> str:
        """_summary_

        Args:
            image_link (str): _description_

        Returns:
            str: _description_
        """
        if '@' in image_link:
            img_link = image_link.split('@')[0]
            return img_link
        else: return image_link

    def community_op_images_repos(self, operator_name: str) -> list:
        """
        
        Searches  for community operators from https://artifacthub.io/

        Args:
            operator_name (str): entity name

        Returns:
            (lst): A list containing all matching operators 
        """
        container_images = []
        request_session = requests.session()
        search_query = self.api + "packages/olm/community-operators/"  + operator_name
        response_ = request_session.get(url= search_query)

        try:

            image_urls = json.loads(response_.text)["containers_images"]
            for imgs in image_urls:

                if "quay.io" in imgs['image'] or "docker.io" in imgs['image'] or 'registry.hub.docker' in imgs['image']: 
                    img_link = self.remove_tags(imgs['image'])
                    container_images.append(img_link) 

        except KeyError:
            print("No container images registry found")

        return container_images
            
        
    def community_op_git_repos(self, operator_name: str):

        """

        Args:
            operator_name (str): entity name

        Returns:
            (lst): A list containing all repos for a given operator_name 
        """

        operator_repository = None
        
        request_session = requests.session()
        search_query = self.api + "packages/olm/community-operators/"  + operator_name
        response_ = request_session.get(url= search_query)
        
        try:

            links = json.loads(response_.text)["links"]  # source , GitHub , etc ...
           
            for link_data in links:
                for _ , val in link_data.items():
                    if val == "source" or val == "GitHub":
                        operator_repository = link_data["url"]
        except KeyError:
            print("No  source urls found")
        
        return operator_repository

    def community_operators(self, entity: str):

        """
        summary_line: Search community  operators from https://artifacthub.io/packages/olm/community-operators/
        
        Keyword arguments:
        entity (str) -- An entity name from from the database
        Return: list of all matching operators 
        """
        

        api = "https://artifacthub.io/api/v1/" 
        package_query = "packages/search?org=operator-framework&repo=community-operators&ts_query_web="

        operators = []
        sess = requests.session()
        endpoint = api + package_query+"{}".format(entity)
        res = sess.get(url=endpoint)
        operator = json.loads(res.text)['packages']
        if len(operator) > 0 :

            for op in operator: 
                update_dict = {"git_repos": None , "container_images": None}
                git_repos = self.community_op_git_repos(op["name"])
                container_images = self.community_op_images_repos(op["name"])
                update_dict["git_repos"] = git_repos
                update_dict["container_images"] = container_images

                
                op.update(update_dict)

                operators.append(op)

        return operators


class Quay:

    def __init__(self) -> None:

        self.quay_api = "https://quay.io/api/v1/"
        self.session = requests.Session()


    def popular_images(self, quay_images:dict, top:int):
        """
        Get popular Quay images 

        Args:
            quay_images (dict): List of Quay images 
            top (int): Threshold = 5 

        Returns:
            (list): Popular images 
        """
        
        popular_quay_images  = []

        if len(list(quay_images.keys())) > 0:
            sorted_results = dict(
                sorted(quay_images.items(), key=operator.itemgetter(1), reverse=True)
            )

            popular_images = dict(itertools.islice(sorted_results.items(), top ))
            popular_quay_images.append(popular_images)
    
        return popular_quay_images


    def exact_image(self, results:list , entity_name:str)->list:
        """
        retrieve exact image

        Args:
            results (list): list of all images obtained by searching the search term (entity_name) from Quay.io
            entity_name (str):Search term

        Returns:
            (list):list of exact matches from Quay.io
        """


        exact = []
        image_template = {"name": "" , "url": "" , "popularity": 0}

        for img in results:
            if (
                   utils.is_exact_match(img['name'], entity_name)
                ):

                    image = image_template.copy()
                    image["name"] = img["name"]
                    image["url"] = "https://quay.io"+img['href']
                    image["popularity"] = img["popularity"]


                    exact.append(image)

        return exact


    def top_images(self,popular_quay_images, results ):

        """
        Select top images based on popularity

        Returns:
            (list): list of top images
        """


        top_image = []

        image_template = {"name": "" , "url": "" , "popularity": 0}

        if len(popular_quay_images) != 0:

            for img  in results:

                if img['href'] in  list(popular_quay_images[0].keys()):
                    image = image_template.copy()
                    image["name"] = img["name"]
                    image["url"] = "https://quay.io"+img['href']
                    image["popularity"] = img["popularity"]

                    top_image.append(image)

        return top_image
            

    def recommend_images(self, results:list, quay_images: dict, entity_name:str) -> tuple:
        """
        Recommended container images 
        Args:
            results (list): list of all relavent container images from Quay.io
            quay_images (dict): Quay image hrefs as keys and popularity as values 
            entity_name (str): entity name from the database 

        Returns:
            (tuple): Exact Quay image(s) and top image(s) found 
        """

        top = int(config["quay"]["top_popular_images"])
        exact_quay_image = []
        popular_quay_images = []
        top_images = []

        popular_quay_images = self.popular_images(quay_images, top)
        exact_quay_image    = self.exact_image( results, entity_name)
        top_images          =  self.top_images(popular_quay_images, results)


        return (exact_quay_image , top_images)



    def search_images(self, entity: str) -> tuple:
        """ 
        
        Search container images from Quay.io

        Args:
            entity (str): Entity name from the database

        Returns:
            tuple: Exact matches and top matches
        """
       
        if not isinstance(entity, str):
            exit()

        max_pages = 2
        images = {}
        page_increment = 1
        results = []
        search_endpoint = self.quay_api + "find/repositories"

        for page in range(max_pages):

            url = search_endpoint + "?includeUsage=true&query={}&page={}".format(
                entity, page + page_increment
            )
            r = self.session.get(url)
            data = json.loads(r.text)
            result = data["results"]
            results += result


        for repo in results:

            images[repo["href"]] = repo["popularity"]
          

        exact   = self.recommend_images(results, images, entity)[0]
        top     = self.recommend_images(results, images, entity)[1]
        return (exact , top)


class DockerHubSearch():

    def __init__(self):

        logging.basicConfig( filename="report.log", filemode="w", level=logging.DEBUG)
        self.client = docker.from_env()
        self.low_level_api = docker.APIClient(base_url='unix://var/run/docker.sock')

    def docker_href(self, image_name: str) -> str:
        """

        Args:
            image_name (str): image's name

        Returns:
            str: href for image_name
        """
        href = ""

        if "/" in image_name:
            href = "https://hub.docker.com/r/" + image_name

        else:
            href = "https://hub.docker.com/_/" + image_name

        return href

    def verified_official_images(self, images:list):
        """
        Retrieve all verified and  official images.

        Args:
            images (list): Search results from dockerhub

        Returns:
            (list): list of verified and official images
        """

        verified_official_images = []
        for image in images:

            # search official_images
            if image["is_official"]:
                verified_official_images.append(image)
            # search verified publishers
            elif "/" in image["name"]:
                if (
                    image["name"].split("/")[0]
                    in verified_publishers["verified_publishers"]
                ):
                    verified_official_images.append(image)
            else:
                continue
        return verified_official_images

    def exact_image(
        self, entity_name: str, verified_and_official_images: list
    ):
        """
        find exact image match

        Args:
            entity_name (str): search term 
            verified_and_official_images (list): list of verified and official images

        Returns:
            (list): A list containing exact DockerHub match
        """

        exact_image = []
        image_names = []
        images = [image["name"] for image in verified_and_official_images]

        for img in images:
            if "/" in img:
                image_names.append(img.split("/")[1])
            else:
                image_names.append(img)

        for index, img in enumerate(verified_and_official_images):

            if  utils.is_exact_match(image_names[index], entity_name):
                exact_image.append(img)
               
            else:
                continue

        return exact_image

    def top_images(self, entity_name: str, verified_official_images: list):
        """
        Get top relevant DockerHub images. select top 40%()

        Args:
            entity_name (str): search term 
            verified_official_images (list): list of verified and official images

        Returns:
            (list):A list containing top relevant DockerHub images
        """
        

        top = int(config["dockerhub"]["top_relevant"])/100.0

        top_images = []
        image_names = []
        query = entity_name

        if len(verified_official_images) == 0:
            return top_images

        images = [image["name"] for image in verified_official_images]

        for img in images:
            if "/" in img:
                image_names.append(img.split("/")[1])
            else:
                image_names.append(img)

        topscore_lines, line_score =utils.line_similarity(image_names, query)

        for index in list(topscore_lines):
            if line_score[index] > top:
                top_images.append(verified_official_images[index])

        return top_images

    def get_os_architectures(self, images: list ) -> list:

        """"
        sumary_line: Using docker_api_utils, retrieve os arch for each image
        
        Keyword arguments:
        images(list) -- list of images from Dockerhub
        Return: 
         
        """
        image_lst = []

        if len(images) == 0: 
            return image_lst

        for image in images:

            arch_list = [] 
            if image['Official image']:
                user = 'library'
                repository = image["name"]
            else:
                user = image["name"].split("/")[0]
                repository = image["name"].split("/")[1]

            image_info = docker_api.tags(user = user, repository= repository)
            
            try:
                os_info = next(image_info)["images"]
            except:

                arch_list.append({
                                 "Class": "null" ,
                                 "Architecture": "null",
                                "Variants": "null",
                                "Versions": "null",
                                "Type": "null",
                                "Subtype": ""
                                         })

                image['OS'] = arch_list
                image_lst.append(image)
                return image_lst

    
            for arch in os_info:
                arch_dict = {
            "Class": "OS" ,
            "Architecture": arch["architecture"],
            "Variants": arch["variant"],
            "Versions": arch['os_version'],
            "Type": arch['os'],
            "Subtype": ""
            }        
                arch_list.append(arch_dict)

            image['OS'] = arch_list

            image_lst.append(image)

        return image_lst
       

    def recommend_exact_image(self,entity_name:str , verified_and_official_images:list):
        """
        Searches for  exact Dockerhub images

        Args:
            entity_name (str): _description_
            verified_and_official_images (list): list containing all verified and official images from search result

        Returns:
            list: list of  exact images if found
        """

        exact_image = self.exact_image(entity_name, verified_and_official_images)
        exact_image = utils.format_images(exact_image)
        exact_image = self.get_os_architectures(exact_image)
        return exact_image


    def recommend_top_images ( self,entity_name:str , verified_and_official_images:list)->list:

        """
        Recommend top relevant images from Dockerhub. 

        Returns:
            list: top images.
        """
        
        top_images = self.top_images(entity_name, verified_and_official_images)
        top_images = utils.format_images(top_images)
        top_images = self.get_os_architectures(top_images)
        return top_images
    
    def recommended_images(self, image_inst:list, entity_name:str):
        """
        Given an entity_name and a list of relevant images from DockerHub, determine 
        the exact match and top relevant matches.

        Args:
            image_inst (list): list of all images found from dockerhub including unofficial as well as unverified images
            entity_name (str):  query ( entity)

        Returns:
            (list) ,(list): exact dockerhub image , top docker images
        """
        verified_official_images = self.verified_official_images(image_inst)
        exact_image = self.recommend_exact_image(entity_name,verified_official_images)
        top_images = self.recommend_top_images(entity_name , verified_official_images)
        return exact_image , top_images


    def search_dockerhub_images(self, entity: str) -> tuple:
        """
        Search container images from Dockerhub.

        Args:
            entity (str): An entity(query) from the database..

        Returns:

            (tuple): exact_image(list) and top_images(list)

        """

        images , exact_image , top_images = [] , [] , []

        try:
            images = self.client.images.search(term=entity)

    
        except:
            print("ImageNotFound error occurred, check your entry and try again.")
        if images == []:

            print("No Dockerhub images found for {} ".format(entity))

        else:
            exact_image , top_images = self.recommended_images(images, entity)

        return (exact_image , top_images)

        

def save_to_kb(results: list) -> None:
    """
    Save search results as a JSON file to \kb directory 

    Args:
        results (dict): dictionary containing search results from Dockerhub , Quay , and Operatorhub.io
    """
   
    with open("/app/kg_utils/image_search_kg/images.json", "w" , encoding="utf-8") as images_file:
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
        print(entities)
     
    else:
        print('Try $python    -e <entity_names>    -db <database_path"> or type $python  src/search_images.py --help')
        exit() 

    if entities == [] and args.entity !='all' :
        print("No entity names found for {}. Enter a valid entity from the database.\n".format(args.entity))
    
        
    if len(suggest_entities) != 0 and len(entities) == 0:
    
        print("Did you mean the following entity(ies) \n")
        for ent in suggest_entities:
            print("{} \n".format(ent))

        print("Enter a valid entity from the entities table")
        exit()

    return entities
    
      

if __name__ == "__main__":

    # entities = get_entities()
    # docker_api =dockerhub_api.DockerHub(username=os.environ.get("DOCKERHUB_USERNAME", None) , password=os.environ.get("DOCKERHUB_PASSWORD", None))
    # docker_   = DockerHubSearch()
    # quay      = Quay() 
    # operator_ = Operators()

    # results = search(entities)

    # save_to_kb(results)

    save_to_csv.docker_images()
  
    save_to_csv.operator_images()
 
    save_to_csv.openshift_images()
