import json
from selenium_driver import  SeleniumDriver
import sys
from selenium.webdriver.common.by import By
from datetime import date


import warnings
if not sys.warnoptions:
    warnings.simplefilter("ignore")


#Explore Dockerhub base url
search_url = "https://hub.docker.com/search?q="

#Filter for Verified publishers
filter_verified = "&image_filter=store"


#Filter for official images
filter_official = "&image_filter=official"

#Filter for official product and verified publisher
filter_both = "&image_filter=official%2Cstore" 

#Filter for OS
filter_wind_os = "&operating_system=windows"
filter_linux_os = "&operating_system=linux"


################################################################################################
##################### DOCKERHUB CONTAINER PLATFORM ############################################
################################################################################################
class DockerHub(SeleniumDriver):

    def __init__(self, url ,selenium_remote_driver_ip="localhost"):
        SeleniumDriver.__init__(self, remote_ip_addr= selenium_remote_driver_ip)
        self.url = url

    def get_image_href(self, url):
        """

        """
        self.open_driver(url)
        container_elems = self.find_element_by_class_name()

        
        if container_elems == None:
            return  "NA"
            
        else:
            container_elements =container_elems.find_elements(By.TAG_NAME, "a")              
            container_images = []

            for cont in container_elements:
                container_images.append(cont.get_attribute("href")) 
            return container_images

    def windows_base_os(self, entity:str)-> dict:
        """
        Find relevant images that run on windows
        Args:
            entity (str): An entity 

        Returns:
            dict:  A dict of relevant images with a windows based OS
        """
        url = search_url + entity + filter_both +  filter_wind_os
        hrefs = self.get_image_href(url)
        return hrefs
        


    def linux_base_os(self, entity: str)-> dict:
        """
        Find relevant images that run on linux

        Args:
            entity (str): An entity

        Returns:
            dict: A dict of relevant images with a linux based OS
        """

        url = search_url + entity + filter_both + filter_linux_os
        hrefs = self.get_image_href(url)
        return hrefs
        


    def base_os(self, entity:str)-> tuple:
        """
        Find windows and linux based OS for an entity
        Args:
            entity (str): An entity

        Returns:
            tuple: Contains base OS for an entity
        """

        if entity =="" or not isinstance(entity , str):
            print("Cannot find base OS for an empty String. Entity must be a string")
            exit()
        linux_base_os = self.linux_base_os(entity)
        windows_base_os = self.windows_base_os(entity)

        return(linux_base_os,windows_base_os)



    def official_image_name(self, url:str)-> str:
        """
        Given an official image url, get the namespace of the repository

        Args:
            url (str): image url

        Returns:
            str: name of the image
        """
        name = url.split("/r/")[-1]
        return name
    
    def verified_publisher_name(self,url:str)-> str:
        """
        Given a verified publisher url, get the name of the publisher

        Args:
            url (str): image url
        
        Returns:
            str: name of the publisher

        """
        name = url.split("/r/")[-1].split("/")[0]

        return name

    def verified_publishers(self):
        """
        Get the list of all verified publishers

        """
        max_page =100 
        url = search_url + filter_verified 
        verified_lst = []

        for page in range(max_page):
            url = search_url + filter_verified  + "&page=" + str(page+1)
            images_urls =  self.get_image_href(url)
            for url in images_urls:
                name = self.verified_publisher_name(url)
                if name not in verified_lst:
                    verified_lst.append(name)
            print("page: {} ".format(page))
        return verified_lst
    


    def update_verified_publisher_lst(self,verified_publisher_name):
        """
        
        """
        
        with open("kg_utils/image_search_kg/verified_publisher_names.json", "r" , encoding="utf-8")  as latest_file:
            verified_pub_latest= json.load(latest_file)

        
        for publisher in verified_publisher_name:
            if publisher not in verified_pub_latest["verified_publishers"]:
                verified_pub_latest["verified_publishers"].append(publisher)
        
        
        verified_pub_latest["last updated"] = input("Enter today's date") 


        with open("kg_utils/image_search_kg/verified_publisher_names.json", "w" , encoding="utf-8")  as lat_file:
            lat_file.write(json.dumps(verified_pub_latest , indent=4))
    
    

    def search_base_os(self,entities: list) -> list:
        """
        Given a list of exact entities , get the base OS for each image

        Args:
            entities (list): list of entities

        Returns:
            dict: A dict containing images along with the base OS(Linux , Windows)
        """

        search_results = []
        base_os = {"linux":[] , "windows": []}
        
        for entity in entities:
            for _  ,   image in  entity.items(): 
                
                image_dict = {image: base_os.copy()}
                linux_base_os  , windows_base_os = self.base_os(image)
                image_dict[image]["linux"] = linux_base_os
                image_dict[image]["windows"] = windows_base_os
                search_results.append(image_dict)

        return search_results


if __name__ == "__main__":
    
    docker = DockerHub("https://hub.docker.com/",selenium_remote_driver_ip=sys.argv[1]) 
    verified_publisher_names = docker.verified_publishers()
    docker.update_verified_publisher_lst(verified_publisher_names)






    
    
        


    