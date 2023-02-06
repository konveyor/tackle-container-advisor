
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


from .load_entities import all_OS_from_db, filter_entity
from .utils import  get_column , remove_tags_url , create_db_connection

# from load_entities import all_OS_from_db, filter_entity
# from utils import  get_column , remove_tags_url , create_db_connection



#List of all OS
all_os_entities = all_OS_from_db() 

#Assign default OS as linux
default_os_id =  [_id   for  _id , val in all_os_entities.items() if val.lower()=="linux"]

db_connection = create_db_connection()


with open("/app/kg/class_type_mapper.json", 'r', encoding="utf-8") as type_map:  
    type_mapper = json.load(type_map)


def entity_mapper(db_connection):
    """
    Loads entity names from "entities" table from mysql db

    :param db_connection: A connection to mysql
    :type db_connection:  <class 'sqlite3.Connection'>

    :returns: A dictionary of entity_names
    :rtype: dict

    """
    parent_class = {}

    parent_cursor = db_connection.cursor()
    parent_cursor.execute("SELECT * FROM entities")

    for entity_row in parent_cursor.fetchall():
        
        class_id, entity = entity_row[0], entity_row[1]
        parent_class[ entity]= str(class_id) 
    return parent_class

entity_mapping_ids = entity_mapper(db_connection)


def search_results():
    """
    load results.

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
    Writes results to csv file.

    Args:
        data (list): A list containing data to save.
        file_name (str): Name of the file to to save the data as csv.

    """

    with open("kg_utils/image_search_kg/{}.csv".format(file_name) , "w" , encoding="utf-8") as op_csv:

        if data == []:
            logging.warning("No {} found".format(file_name))
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

        if file_name == "move2kube_images":
            for row in data:
                writer.writerow({"move2kube_images":row["move2kube_images"],'container_name': row["container_name"], 'OS': row["OS"] \
                    , "lang":row["lang"],  "lib": row["lib"] , "app": row["app"] \
                        ,"app_server": row["app_server"] , "plugin":row["plugin"] , \
                            "runlib": row["runlib"] , "runtime": row["runtime"] , \
                            "move2kube_correspondent_image_url": row["move2kube_correspondent_image_url"] }) 

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
    Builds column headers for csv files.

    Args:
        table_name (str, optional):The name of the table from the database.

    Returns:
        dict:  csv header.
    """
    
    columns = { table_name: "", "container_name":"", "OS": None, "lang" : None, "lib": None, "app": None, "app_server": None,"plugin": None,"runlib": None,"runtime": None }
    docker_col_extension = {"Docker_Url":"", "Notes": "", "CertOfImageAndPublisher": "" }
    openshift_col_extension = {"Openshift_Correspondent_Image_Url":"", "DockerImageType": ""}
    operator_col_extension ={"Operator_Correspondent_Image_Url":[],"Operator_Repository": ""}
    move2kube_col_extension = {"move2kube_correspondent_image_url":[]}

    if table_name == "openshift_images":
        columns.update(openshift_col_extension) 

    elif table_name == "docker_images":
        columns.update(docker_col_extension)
    elif table_name == "operator_images":
        columns.update(operator_col_extension)
    elif table_name == "move2kube_images":
        columns.update(move2kube_col_extension)
    else: 
        logging.debug("Wrong table's name. Enter a valid table name from the database")
        exit()
        
    return columns
        
def operator_images():
    """
    Saves operator images to operator_images.csv.

    """
    row_data = []
    cols = csv_columns(table_name="operator_images")
    images_ = search_results()
    operator_images  = get_column("operator_images", column_index=1)
    
    #All exact images from the three catalogs.
    operator_exact_images = get_exact_images(images_ , catalogue="operators")
    
    for operator_image in operator_exact_images:
        image_name = list(operator_image.keys())[0]

        if operator_image[image_name] == []:
            logging.info("No exact Operator images were found for {}.".format(image_name))
    
        for op in operator_image[image_name]:

            op_data = cols.copy()
            op_data["operator_images"] = "operator_images"
            op_data["container_name"] = op["display_name"].lower().strip()

            if op_data["container_name"] in operator_images:
                logging.info("{}  is already present".format(op_data["container_name"]))
                continue
        
            op_data["OS"] = default_os_id[0]
            img_data_type = entity_type_mapper( operator_image["type"] , str( operator_image["entity_id"]))

            if list(img_data_type.keys())[0] in list(op_data.keys()):
                op_data.update(img_data_type)
                row_data.append(op_data)

            if len(op["container_images"]) >=1:
                Operator_Correspondent_Image_Url = remove_tags_url(op["container_images"][0])
                logging.info("{}  ==> {}".format(op["container_images"][0], Operator_Correspondent_Image_Url))
                op_data["Operator_Correspondent_Image_Url"] = Operator_Correspondent_Image_Url
            else:
                op_data["Operator_Correspondent_Image_Url"] = None
            op_data["Operator_Repository"] = op["git_repos"]
    
    write_to_csv(row_data ,file_name="operator_images")

def docker_os_type_id(os_types:list ) -> dict:
    """
    Retrieves OS ids.
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
        exact_image (dict): An  image from dockerhub.
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


def docker_images() -> None:
    """
    Saves docker images to docker_images.csv.

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



def default_id(component:str)-> int:
    """
    Assign default OS ids 
    Args:
        component (str): component_type [ OS, Lang, Lib, App, App Server, Plugin, Runlib, Runtime]

    Returns:
        int: default os id. 
    """
    if component == "OS":
        return default_os_id[0]
    


def standard_name_type(standard_name: str) ->str:

    return type_mapper[standard_name]

    
def standard_name_ids(type_data: dict , type_name:str) -> list:
    """
    Get standard name from type_data.
    Args:
        type_data (dict): Contains data 
        type_name (str): _description_

    Returns:
        list: List of tuple containing (entity_id, entity_type).

    """

    ids , standard_name_type = [] , []
    entity_names = list(type_data[type_name].keys())
    
    if len(entity_names) == 0:
        return []

    else: 
        for entity_name in entity_names:
            standard_name = type_data[type_name][entity_name].get("standard_name",None)
            id = entity_mapping_ids[str(standard_name)]
            standard_name_type = type_mapper["mappings"][standard_name]
            ids.append((id , standard_name_type))
    return ids
    

def create_n_rows( column_data: dict , ids: list,  url :str):

     rows = []
     component_columns=  {'Lang': 'lang', 'Lib': 'lib', 'App Server': 'app server', "Runlib": "runlib", 'Runtime': 'runtime',"Plugin": 'plugin' ,'App': 'app', 'OS': 'OS'}

     for n_row , id in enumerate(ids):
        row_data = column_data.copy()
        entity_id , entity_type = id[0] , id[1]
        col_name = component_columns[entity_type]
        row_data[col_name] = entity_id

        if row_data["OS"] == None: row_data["OS"] = int(default_os_id[0])
        row_data["move2kube_correspondent_image_url"] = url
        rows.append(row_data)
        print("row {} , data: {} , ===> type: {}".format(n_row, row_data, entity_type))
        del row_data

     return rows
    
  





def move2kube():
    """
    Convert move2kube json data to csv
    """

    columns = csv_columns(table_name="move2kube_images")
    row_data = []


    with open("kg_utils/image_search_kg/ibm_cloud_catalog_standardized.json", "r" , encoding="utf-8") as catalog:
        ibm_cloud_catalog = json.load(catalog)

    with open("kg_utils/image_search_kg/ibm_cloud_catalog.json", "r" , encoding="utf-8") as catalog_url:
        ibm_cloud_catalog_url = json.load(catalog_url)

    for idx , cat in enumerate(ibm_cloud_catalog[:]):
        app_data = cat.copy()
        column_data = columns.copy()
        app_data.update({"container_name": app_data.pop("Name")})
        app_data.pop("Desc") 
        app_data.pop("Cmpt")
        app_data.pop("Reason")
        app_data.pop("KG Version")
        app_data.update({"move2kube_correspondent_image_url":ibm_cloud_catalog_url[idx]["application_url"]}) 

        #update row_data
        column_data["move2kube_images"] = "move2kube_images"
        column_data["container_name"] = app_data["container_name"]

        components = ["OS", "Lang" , "Libs" , "App" ,"App Server" , "Plugin", "Runlib", "Runtime", "Dependent Apps"]
        component_columns=  {'Lang': 'lang', 'Lib': 'lib', 'App Server': 'app server', "Runlib": "runlib", 'Runtime': 'runtime',"Plugin": 'plugin' ,'App': 'app', 'OS': 'OS'}
        create_multiple_rows = False
        rows = None

        for component in components:
            if component in list(app_data.keys()):  
                ids  = standard_name_ids(app_data , component)
                if len(ids) > 1:
                    rows = create_n_rows(column_data, ids, app_data["move2kube_correspondent_image_url"] )
                    create_multiple_rows = True
                    continue
                else:
                    for id in ids:
                        entity_id , entity_type = id[0] , id[1]
                        col_name = component_columns[entity_type]
                        column_data[col_name] = entity_id           
            else:
                if component != "Dependent Apps":
                    col_name = component_columns[component] 
                    column_data[col_name] = None

        if create_multiple_rows:
            for ro in rows:
                row_data.append(ro)
        else: 
            if column_data["OS"] == None: column_data["OS"] = int(default_os_id[0])
            column_data["move2kube_correspondent_image_url"] = app_data["move2kube_correspondent_image_url"]
            row_data.append(column_data)
            
    write_to_csv(row_data, "move2kube_images")

    
    
if "__name__==__main__":

    move2kube()
    # docker_images()
    # openshift_images()
    # openshift_images()