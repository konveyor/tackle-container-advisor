
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


import requests
import json
import logging

from validator_collection import url
from . import load_entities
from sklearn.utils import resample

BASE_ENDPOINT="https://artifacthub.io/api/v1/"
SEARCH_ENDPOINT = "packages/search"
#Artifact.io kind ids
KINDS = [0,1,2,3,4,5,6,7,8,9,10,11,12,13,14]

class Operators():

    def __init__(self):

        self.api = BASE_ENDPOINT 
        self.package_query = "packages/search?org=operator-framework&repo=community-operators&ts_query_web=&limit=60&offset="
    

    def remove_tags(self, image_link:str)-> str:
        """
        Remove tags(@) from image_link.

        Args:
            image_link (str): URL link

        Returns:
            str: URL without tags 
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
            print(" '{}'  is not a key. So container images registry found for {} ".format("containers_images", operator_name))
           

        return container_images
            
        
    def community_op_git_repos(self, operator_name: str):

        """
        Search git repositories for an operator.

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

                    if val == "source" or val == "GitHub" or val == "Documentation":
                        operator_repository = link_data["url"]

        except KeyError:

            print("No  git , source , or  Documentation url links found.")


        
        return operator_repository

    def community_operators(self, entity: str):

        """
        Search community  operators from https://artifacthub.io/packages/olm/community-operators/
        
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


def do_request(url: str):
    """_summary_

    Args:
        url (str): _description_
    """
    resp = requests.get(url)
    if resp.status_code  in [201, 200]:
        response = resp.json()
        return response
    else:
        print(resp.status_code)
        logging.error(f'error ')
        return None


def search(search_url:str):
    """_summary_

    Args:
        search_url (str): _description_

    Returns:
        _type_: _description_
    """
    resp = requests.get(search_url)
    if resp.status_code  in [201, 200]:
        response = resp.json()
        return response
    else:
        print(resp.status_code)
        logging.error(f'error ')
        return None , None
        
      
def install_instruction(url:str):
    """_summary_

    Args:
        url (str): _description_

    Returns:
        _type_: _description_
    """
    return url + "?modal=install"

  
def official_operators(entity: str, kind:int) -> str:
    """_summary_

    Args:
        entity (str): _description_
        kind (int): _description_

    Returns:
        str: _description_
    """
    url ="https://artifacthub.io/api/v1/packages/search?kind={}&ts_query_web={}&official=true&sort=relevance&page=1".format(kind,entity)
    resp = do_request(url)
    return resp

def verified_publisher_operators(entity:str, kind : int)-> str:
    """_summary_

    Args:
        entity (str): _description_
        kind (int): _description_

    Returns:
        str: _description_
    """

    url ="https://artifacthub.io/api/v1/packages/search?kind={}&ts_query_web={}&verified_publisher=true&sort=relevance&page=1".format(kind,entity)
    resp = do_request(url)
    return resp

def only_operators(entity:str, kind: int) -> str:
    """_summary_

    Args:
        entity (str): _description_
        kind (int): _description_

    Returns:
        str: _description_
    """
    url ="https://artifacthub.io/api/v1/packages/search?kind={}&ts_query_web={}&operators=true&sort=relevance&page=1".format(kind, entity)
    resp = do_request(url)
    return resp

def package_kind ( facets : dict) -> list:
    """_summary_

    Args:
        facets (dict): _description_

    Returns:
        list: _description_
    """
    options = facets[0]["options"]
    
    ids , kind_names = [] , []
    for option in options:
        ids.append(option["id"])
        kind_names.append(option["name"])

    return ids , kind_names

def package_name(package:dict)-> str:
    """_summary_

    Args:
        package (dict): _description_

    Returns:
        str: _description_
    """

    return package['name']

def facet(search_result: dict) -> dict:
    """_summary_

    Args:
        search_result (dict): _description_

    Returns:
        dict: _description_
    """
    return json.loads(json.dumps(search_result["facets"], indent=4))

def operator_urls(entity:str, olm_kind_id: int) -> list:
    """_summary_

    Args:
        entity (str): _description_

    Returns:
        list: _description_
    """

    links = {}
    links["name"] = ""
    links["url"] = ""
    links["instruction_url"] =""
    urls = []
    
    only_ops =  only_operators(entity,olm_kind_id)
    for package in only_ops['packages']:
        
        pac_links = links.copy()
        name = package_name(package)
        pac_links["name"] = name
        pac_links["url"] = "https://artifacthub.io/packages/olm/community-operators/"+ name
        pac_links["instruction_url"]= install_instruction(pac_links["url"]) 
        urls.append(pac_links)
    return urls


def package_installation_urls( entity_name:str) -> list:
    """_summary_

    Args:
        all_packages (dict): _description_

    Returns:
        list: _description_
    """
    search_url = BASE_ENDPOINT + SEARCH_ENDPOINT +  "?offset=0&limit=20&facets=true&ts_query_web={}&sort=relevance&page=1".format(entity_name)
   
    #Global Search 
    result = search(search_url)
    facets = []
    olm_id  = KINDS[3]
    
    facets   =   facet(result)
    kind_ids , _= package_kind(facets)
    if olm_id in kind_ids:
        urls = operator_urls(entity, olm_id)

    else:
        print("No OLM operators found for: {}".format(entity_name))
        urls = []
    
    return urls

if __name__=="__main__":
    

    entities = load_entities.from_database(entity_names="all")[0]
    olm_url = {}
    
    for entity in ["golang","MYSQL" , "nginx","tomcat", "postgres"]:# entities[120:127]:

        entity_name = entity
        urls = package_installation_urls(entity_name)
        olm_url[entity_name] = urls
       
    print(json.dumps(olm_url , indent=4))

    



  






