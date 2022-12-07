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

import logging
import docker
import json
import os
from . import  utils , dockerhub_api
from dotenv import load_dotenv ,find_dotenv
import configparser


#load environment variable 
load_dotenv(find_dotenv())

#config file
config = configparser.ConfigParser()
config_data = os.path.join("config/kg.ini")
config.read([config_data])

#loggger
logger = logging.getLogger('search')
logger.setLevel(logging.INFO)

# #load list of verified and official publishers
with open("kg_utils/image_search_kg/verified_publisher_names.json", "r", encoding="utf-8") as verified_file:
    verified_publishers = json.load(verified_file)


docker_api =dockerhub_api.DockerHub(username=os.environ.get("DOCKERHUB_USERNAME", None) , password=os.environ.get("DOCKERHUB_PASSWORD", None))


class DockerHubSearch():

    def __init__(self):

        logging.basicConfig( filename="report.log", filemode="w", level=logging.DEBUG)
        self.client = docker.from_env()
        self.low_level_api = docker.APIClient(base_url='unix://var/run/docker.sock')

    def docker_href(self, image_name: str) -> str:
        """
        Form href using image_name
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

    def user_and_repository(self, image:dict) -> tuple:
        """_summary_

        Args:
            image (dict): _description_

        Returns:
            tuple: _description_
        """

        if image['Official image']:
            user = 'library'
            repository = image["name"]

        else:

            user = image["name"].split("/")[0]
            repository = image["name"].split("/")[1]
        
        return (user , repository)

    def _tag_os(self, results: list)-> list:
        """

        For each tags, get the operating system

        Args:
            results (list): All tags data

        Returns:
            list: A list containing unique OS names
        """
        OS = []
        for result in results:
            images = result["images"]
            for image in images:
                OS.append(image["os"])
        return list(set(OS))

    def tags(self,user:str , repository: str )-> list:
        """
        Args:
            user (str): username
            repository (str): repository

        Returns:
            list: Unique OS  names 
        """
        pages = int(config["dockerhub"]["tags_num_pages"]) # look for OS within x number of pages
        OS = []
        for page in range(pages):
            try:
                tag = docker_api._do_requests_get( "https://registry.hub.docker.com/v2/repositories/{}/{}/tags/?page={}".format(user, repository, page+1) )   
                results = tag.json()["results"]
                OS = OS + self._tag_os(results)
            except:
                logger.info("No more tags found at page{}".format(page))
        return OS


    def get_os(self, images: list ) -> list:

        """"
        Using docker_api_utils, retrieve os  for each image.
        
        Keyword arguments:
        images(list) -- list of images from Dockerhub
        Return: 
         list of images with  updated OS data
        """
        image_lst = []

        if len(images) == 0: 
            return image_lst

        for image in images:

            OS_list = [] 
            user , repository = self.user_and_repository(image)

            OS_list =  self.tags(user, repository)

            image['OS'] = list(set(OS_list))

            image_lst.append(image)

        return image_lst
       

    def recommend_exact_image(self,entity_name:str , verified_and_official_images:list):
        """
        Searches for  exact Dockerhub images.

        Args:
            entity_name (str): _description_
            verified_and_official_images (list): list containing all verified and official images from search result

        Returns:
            list: list of  exact images if found
        """

        exact_image = self.exact_image(entity_name, verified_and_official_images)
        exact_image = utils.format_images(exact_image)
        exact_image = self.get_os(exact_image)
        return exact_image


    def recommend_top_images ( self,entity_name:str , verified_and_official_images:list)->list:

        """
        Recommend top relevant images from Dockerhub. 

        Returns:
            list: top images.
        """
        
        top_images = self.top_images(entity_name, verified_and_official_images)
        top_images = utils.format_images(top_images)
        top_images = self.get_os(top_images)
        return top_images
    
    def recommended_images(self, image_inst:list, entity_name:str):
        """
        Given an entity_name and a list of relevant images from DockerHub, determine 
        exact matches and top relevant matches.

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
    

    def has_tags(self,user , repo:str) -> bool:
        """
        Check if a repository  has tags 
        Args:
            container_url (str): a container url

        Returns:
            bool: True if repository has tags,False otherwise
        """
        try:
            resp = docker_api._do_requests_get("https://registry.hub.docker.com/v2/repositories/{}/{}/tags".format(user, repo) )
            return True

        except:
            return False


    def user_repo_from_url(self, url: str) -> tuple:
        """
        Extract user and repo name fro url
        Args:
            url (str): Image url

        Returns:
            tuple: (user , repo)
        """
            
        user_repo = url.split("https://hub.docker.com")[-1]
        
        if "/_/" in user_repo:
            user ="library"
            repo = user_repo.split("/_/")[-1]
        elif "/r/" in user_repo:

            user_repo_split = user_repo.split("/r/")[-1].split("/")
            user = user_repo_split[0]
            if len(user_repo_split)==3:
                repo = user_repo_split[1]
            else: repo= user_repo_split[-1]
        else:
            user = user_repo.split("/")[0]
            repo = user_repo.split("/")[1]

        return (user , repo)
            


    def docker_containers_with_no_tags(self)-> list:
        """
        Retrieve all docker url from docker_images table
        Returns:
            list: List of container images with no tags data
        """
        docker_urls = utils.container_urls()
        # To avoid hitting the rate limits, run in multiple sessions( in batch mode): docker_urls[0:65], docker_urls[65:130] , docker_urls[130:195] , docker_urls[195:260] ....
    
        images_with_no_tags = []

        for url in docker_urls[:65]:
          
            if "https://hub.docker.com" not in url: continue
            user , repo = self.user_repo_from_url(url)
            
            if self.has_tags(user , repo):
                print("{}:{} has tags: {} ".format(user , repo, url))
            elif not self.has_tags(user ,repo):
                print("{}:{} has no tags: {}".format(user, repo, url))
                images_with_no_tags.append(url)
            else: continue
        print(json.dumps(images_with_no_tags, indent=4))
        return images_with_no_tags


