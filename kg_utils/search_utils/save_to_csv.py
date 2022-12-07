
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

import json
import logging
import csv
from .load_entities import all_OS_from_db
from .utils import  get_column , remove_tags_url


#List of all OS
all_os_entities = all_OS_from_db() 

#Assign default OS as linux
default_os_id =  [_id   for  _id , val in all_os_entities.items() if val.lower()=="linux"]


def search_results():
    """
    load results 

    Returns:
        None:  Json file containing  search results
    """

    with open("kg_utils/image_search_kg/images.json", "r" , encoding="utf-8") as images:
        images_ = json.load(images)

    return images_


def entity_type_mapper( entity_type: int , entity_id : str)-> dict:
    """
    Maps entity_types to an integer ranging from 1 to 12

    Args:
        entity_type (int): entity_type id
        entity_id (int): entity index from the entity_name table from the database

    Returns:
        dict: a mapping of entity_type_name to a unique id 

    """
    type_mapper = {"technology": 1, "app": 2 , "vm": 3 , "hw" : 4 , "plugin": 5 , "OS" : 6 , "runlib": 7, \
          "app_server" : 8 , "lang": 9 , "runtime": 10 , "storage": 11 , "lib": 12
        
        }

    for ky , val in type_mapper.items():
        if val == entity_type:
            return {ky:entity_id}


def write_to_csv(data:list, file_name:str):
    """
    Write results to csv file 

    Args:
        data (list): A list containing data to save.
        file_name (str): Name of the file to to save the data as csv.

    """

    with open("kg_utils/image_search_kg/{}.csv".format(file_name) , "w" , encoding="utf-8") as op_csv:

        if data == []:
            print("No {} found".format(file_name))
            return

        columns = list(data[0].keys())
        writer = csv.DictWriter(op_csv, fieldnames=columns)
        writer.writeheader()

        if file_name == "operator_images":

            for row in data:
                writer.writerow({"operator_images":row["operator_images"],'container_name': row["container_name"], 'OS': row["OS"] \
                    , "lang":row["lang"],  "lib": row["lib"] , "app": row["app"] \
                        ,"app_server": row["app_server"] , "plugin":row["plugin"] , \
                            "runlib": row["runlib"] , "runtime": row["runtime"] , \
                            "Operator_Correspondent_Image_Url": row["Operator_Correspondent_Image_Url"] ,\
                                "Operator_Repository" : row["Operator_Repository"]
                                }) 
        if file_name == "docker_images":
            for row in data:

                writer.writerow({"docker_images":row["docker_images"],'container_name': row["container_name"], 'OS': row["OS"] \
                    , "lang":row["lang"],  "lib": row["lib"] , "app": row["app"] \
                        ,"app_server": row["app_server"] , "plugin":row["plugin"] , \
                            "runlib": row["runlib"] , "runtime": row["runtime"] , \
                            "Docker_Url": row["Docker_Url"] ,\
                                "Notes": row["Notes"], \
                            "CertOfImageAndPublisher": row["CertOfImageAndPublisher"]

                                }) 

        if file_name =="openshift_images":
            for row in data:

                writer.writerow({"openshift_images":row["openshift_images"],'container_name': row["container_name"], 'OS': row["OS"] \
                    , "lang":row["lang"],  "lib": row["lib"] , "app": row["app"] \
                        ,"app_server": row["app_server"] , "plugin":row["plugin"] , \
                            "runlib": row["runlib"] , "runtime": row["runtime"] , \
                            "Openshift_Correspondent_Image_Url": row["Openshift_Correspondent_Image_Url"] ,\
                                "DockerImageType": row["DockerImageType"]

                                }) 
    

def get_exact_images(all_images: dict , catalogue ="operators", index = 2):
    """
    Gather exact image names.

    Args:
        all_images (dict): A large dictionary containing all search results
        catalogue (str, optional): Catalog's name("operator" , "dockerhub_exact_images" ,or "quay_exact_images" ) . Defaults to "operators".
        index (int, optional): _description_. Defaults to 2.

    Returns:
        list: A list containing exact image names.
    """

    if all_images == []:
        logging.error("All_images list is empty. ")
        exit()
    
    if catalogue == "dockerhub_exact_images": index = 0
    if catalogue == "quay_exact_images"     : index = 1
    
    exact_images_lst = []

    for id_ , image in enumerate(all_images):
        
        
        image_name = list(image.keys())[0]
        
        
           
    
        if  image[image_name][index][catalogue] != []:
            
        

            exact_images= {image_name: [], "type": image["entity_type"] , "entity_id" : image["entity_id"]}
            exact_images[image_name] = image[image_name][index][catalogue] 
            exact_images_lst.append(exact_images)
        else:
            exact_images_lst.append({image_name: [], "type": image["entity_type"] , "entity_id" : image["entity_id"]})

    return exact_images_lst

def csv_columns( table_name:str ):
    """
    Build the columns headers for the csv files.

    Args:
        table_name (str, optional):The name of the table from the database.

    Returns:
        dict:  csv header.
    """
    
    columns = { table_name: "", "container_name":"", "OS": None, "lang" : None, "lib": None, "app": None, "app_server": None,"plugin": None,"runlib": None,"runtime": None }

    docker_col_extension = {"Docker_Url":"", "Notes": "", "CertOfImageAndPublisher": "" }

    openshift_col_extension = {"Openshift_Correspondent_Image_Url":"", "DockerImageType": ""}

    operator_col_extension ={"Operator_Correspondent_Image_Url":[],"Operator_Repository": ""}

    if table_name == "openshift_images":
        columns.update(openshift_col_extension) 

    elif table_name == "docker_images":
        columns.update(docker_col_extension)
    elif table_name == "operator_images":
        columns.update(operator_col_extension)
    else: 
        logging.debug("Wrong table's name. Enter one of the following table's names: docker_images, operator_images,operator_images")
        exit()
        
    return columns
        
def operator_images():
    """
    Saves operator images to a operator_images.csv

    """
    row_data = []
    cols = csv_columns(table_name="operator_images")
    images_ = search_results()
    operator_images  = get_column("operator_images", column_index=1)

    operator_exact_images = get_exact_images(images_ , catalogue="operators") #All exact images from the three catalogs.
    
    for operator_image in operator_exact_images:
        image_name = list(operator_image.keys())[0]

        if operator_image[image_name] == []:
            logging.info("No exact Operator images were found for {}.".format(image_name))
    
        for op in operator_image[image_name]:

            op_data = cols.copy()
            op_data["operator_images"] = "operator_images"
            op_data["container_name"] = op["display_name"].lower().strip()

            if op_data["container_name"] in operator_images:
                print("{}  is already present".format(op_data["container_name"]))
                continue
        
            op_data["OS"] = default_os_id[0]
            img_data_type = entity_type_mapper( operator_image["type"] , str( operator_image["entity_id"]))

            if list(img_data_type.keys())[0] in list(op_data.keys()):
                op_data.update(img_data_type)
                row_data.append(op_data)

            if len(op["container_images"]) >=1:
                Operator_Correspondent_Image_Url = remove_tags_url(op["container_images"][0])
                print("{}  ==> {}".format(op["container_images"][0], Operator_Correspondent_Image_Url))
                op_data["Operator_Correspondent_Image_Url"] = Operator_Correspondent_Image_Url
            else:
                op_data["Operator_Correspondent_Image_Url"] = None
            op_data["Operator_Repository"] = op["git_repos"]
    
    write_to_csv(row_data ,file_name="operator_images")

def docker_os_type_id(os_types:list ) -> dict:
    """
    Get OS ids.
    Args:
        os_types (list):  List of OS names
       
    Returns:
        dict: A dict containing OS name as key and id as value.
    """
    os_type_ids = {}

    for os_type in os_types:
        for entity_id , os_name in all_os_entities.items():
            if os_name.lower() == os_type:
                os_type_ids[os_name.lower()] = entity_id 
    return os_type_ids         

def docker_os_types(exact_image:dict)-> list:
    """
    Get the OS type ( Linux , Centos , Ubuntu etc ..) of an image. 
    Args:
        exact_image (dict): An  image from dockerhub
    Returns:
        list: list of OS types this particular image runs on. 
    """
  
    os_types = exact_image["OS"] 
    os_types = list(set(os_types))
    os_type_ids = docker_os_type_id(os_types) 

    if  not os_type_ids:
        logging.info("No OS info was found for this image. So the OS type_id will default to {}".format(default_os_id))
        return {"linux":default_os_id[0]}
    else:
        return os_type_ids

def containers_with_multiple_os(container_names: list) -> list:
    """_summary_

    Args:
        container_names (list): _description_

    Returns:
        list: _description_
    """
    pass


def docker_images() -> None:
    """
    Saves docker images to docker_images.csv
    """
    
    row_data = []
    cols = csv_columns(table_name="docker_images")
    images_ = search_results()
    docker_exact_images = get_exact_images(images_, catalogue= "dockerhub_exact_images")
    docker_images  = get_column("docker_images", column_index=1)
    
    for idx , exact_image in enumerate(docker_exact_images):

        image_name_ = list(exact_image.keys())[0]
        
        if exact_image[image_name_] == []:
            logging.info("No exact Docker images were found for {} ".format(image_name_))
            continue

        for image in exact_image[image_name_]:

            img_data = cols.copy()
            img_data["docker_images"] = "docker_images"
            img_data["container_name"] = image["name"].lower().strip()
            
            #get OS types
            os_types =  docker_os_types(image)
            os_names = list(os_types.keys())

            #check for container_name_os_name
            if img_data["container_name"] + "_" + os_names[0] in docker_images:
                print("{} : {}  is already present".format(idx, img_data["container_name"] + "_" + os_names[0]))
                continue

            if img_data["container_name"] in docker_images:
                print("{} : {}  is already present".format(idx ,img_data["container_name"]))
                continue

            img_data["Docker_Url"] = image["Docker_Url"]
            img_data["Notes"] = ""

            #image certification status
            if image["Official image"]: 
                img_data["CertOfImageAndPublisher"] =  "Official Image"
            if image["Verified Publisher"]: 
                img_data["CertOfImageAndPublisher"]  = "Verified Publisher"

            #map entity to type
            img_data_type = entity_type_mapper(exact_image["type"] ,  str(exact_image["entity_id"]))
            img_data.update(img_data_type)

      
            #Assign OS name
            if len(list(os_types.keys()))== 1 and list(os_types.keys())[0] =="linux":
                img_data["OS"] = default_os_id[0]
                row_data.append(img_data)

            else: 
                for OS_name , os_id in os_types.items():
                    new_row_data = img_data.copy()
                    new_row_data["container_name"] = img_data["container_name"] + "_" + OS_name.lower()
                    new_row_data["OS"] = os_id
                    row_data.append(new_row_data)
   
    write_to_csv(row_data , "docker_images")


def openshift_images():
    """
    Saves Openshift images to openshift_images.csv.
    
    """
    
    row_data     = []
    cols         = csv_columns(table_name="openshift_images")
    images_      = search_results()
    quay_exact_images  = get_exact_images(images_, catalogue="quay_exact_images")
    openshift_images  = get_column("openshift_images", column_index=1)

    for quay_image in quay_exact_images:

        image_name   = list(quay_image.keys())[0]

        if quay_image[image_name] == []:
            logging.info("No exact Quay images were found for {}".format(image_name))
        

        for image in quay_image[image_name]: 
            
            img_data = cols.copy()
            img_data["openshift_images"] = "openshift_images"
            img_data["container_name"] = ''
            img_data["container_name"] = image["url"].split("/repository/")[-1].lower().strip()

            if "/application/" in image["url"]: 
                img_data["container_name"] =  image["url"].split("/application/")[-1].lower().strip()
             
            if img_data["container_name"] in openshift_images :
                print("{}  is already present".format(img_data["container_name"]))
                continue

            #check duplicate names
            if "/" in img_data["container_name"]:
                split_name = img_data["container_name"].split("/")
                if split_name[0]==split_name[1] and split_name[0] in openshift_images:
                    print("{}  is already present".format(img_data["container_name"]))
                    continue  

            img_data["OS"] = default_os_id[0]
            
            img_data["Openshift_Correspondent_Image_Url"] = image["url"]

            img_data_type = entity_type_mapper(quay_image["type"] , str(quay_image["entity_id"]))
            if list(img_data_type.keys())[0].title() =='Os': img_data["DockerImageType"] ='OS'
            else: img_data["DockerImageType"] = list(img_data_type.keys())[0].title()

            if list(img_data_type.keys())[0] in list(img_data.keys()):
                img_data.update(img_data_type)
                row_data.append(img_data)
    write_to_csv(row_data , "openshift_images")

