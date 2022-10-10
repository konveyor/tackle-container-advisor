
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
class Operators():

    def __init__(self):

        self.api = "https://artifacthub.io/api/v1/"  
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