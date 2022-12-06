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
import configparser
import os
import logging
import operator
import itertools
from . import utils
#config file
config = configparser.ConfigParser()
config_data = os.path.join("config/kg.ini")
config.read([config_data])

#loggger
logger = logging.getLogger('search')
logger.setLevel(logging.INFO)

class Quay():

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