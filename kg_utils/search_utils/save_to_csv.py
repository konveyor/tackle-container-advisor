
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
import csv

def search_results():
    """
    load results 

    Returns:
        None:  Json file containing  search results
    """

    with open("/app/kg_utils/image_search_kg/images.json", "r" , encoding="utf-8") as images:
        images_ = json.load(images)

    return images_


def entity_type_mapper( entity_type: int , entity_id : str)-> dict:
    """
    Maps entity_types to an interger ranging from 1 to 12

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


def write_to_csv(data:dict, file_name:str):
    """
    Write results to csv file 

    Args:
        data (list): A list containing data to save.
        file_name (str): Name of the file to to save the data as csv.

    """

    with open("/app/kg_utils/image_search_kg/{}.csv".format(file_name) , "w" , encoding="utf-8") as op_csv:

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
                            "Operator_Correspondant_Image_Url": row["Operator_Correspondant_Image_Url"] ,\
                                "Operator_Repository" : row["Operator_Repository"], "Other_Operators": row["Other_Operators"]

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
                            "Opeshift_Correspondent_Image_Url": row["Openshift_Correspondent_Image_Url"] ,\
                                "DockerImageType": row["DockerImageType"]

                                }) 
    

def get_exact_images(all_images:dict , catalogue ="operators", index = 2):
    """
    Gather exact image names found during the search proceedure.

    Args:
        all_images (dict): A large dictionary containg all serach results
        catalogue (str, optional): Catalog's name("operator" , "dockerhub_exact_images" ,or "quay_exact_images" ) . Defaults to "operators".
        index (int, optional): _description_. Defaults to 2.

    Returns:
        list: A list containing exact image names.
    """
    
    if catalogue == "dockerhub_exact_images": index = 0
    if catalogue == "quay_exact_images" : index = 1

    images = []
    
    for image in all_images:
        image_name = list(image.keys())[0]

        if image[image_name][index][catalogue] != []:
            op_data = {image_name: [], "type": image["entity_type"] , "entity_id" : image["entity_id"]}

            op_data[image_name] = image[image_name][index][catalogue] 
            images.append(op_data)

    return images


def csv_columns( table_name = "operator_images"):
    """
    Build the columns headers for the csv files.

    Args:
        table_name (str, optional):The name of the table from the database. Defaults to "operator_images".

    Returns:
        dict:  A fomated headers for the csv.
    """
    
    columns = { table_name: "", "container_name":"", "OS": 426, "lang" : None, "lib": None, "app": None, "app_server": None,"plugin": None,"runlib": None,"runtime": None }

    docker_col_extension = {"Docker_Url":"", "Notes": "", "CertOfImageAndPublisher": "" }
    openshift_col_extension = {"Opeshift_Correspondent_Image_Url":"", "DockerImageType": ""}
    operator_col_extension ={"Operator_Correspondant_Image_Url":[],"Operator_Repository": "", "Other_Operators": ""}

    if table_name == "openshift_images":
        columns.update(openshift_col_extension) 
    elif table_name == "docker_images":
        columns.update(docker_col_extension)
    else:
        columns.update(operator_col_extension)

    return columns


def operator_images_urls(image_links: list ):
    """_summary_

    Args:
        images_links (list): _description_
    """
    urls = []
    if image_links == []:
        return None
    else:
        for dt in image_links  :
            links_ = "\'\'" + dt + "\'\'" 
            urls.append(links_)
        return urls
        
def operator_images():
    """
    Saves operator images to a operator_images.csv

    """
    row_data = []
    cols = csv_columns(table_name="operator_images")
    images_ = search_results()
    op_images = get_exact_images(images_ , catalogue="operators")

    if op_images == None:
        return

    for op in op_images:

        op_name = list(op.keys())[0]

        for operator in op[op_name]:

            op_data = cols.copy()
            op_data["operator_images"] = "operator_images"
            op_data["container_name"] = operator["display_name"]

            op_data["Operator_Correspondant_Image_Url"]= operator_images_urls(operator["container_images"])
            
            op_data["Operator_Repository"] = operator["git_repos"]
            img_data_type = entity_type_mapper(op["type"] , str(op["entity_id"]))
            op_data.update(img_data_type)
            row_data.append(op_data)

    write_to_csv(row_data ,file_name="operator_images")

    
def docker_images() -> None:
    """
    Saves docker images to docker_images.csv
    """
    
    row_data = []
    cols = csv_columns(table_name="docker_images")
    images_ = search_results()
    docker_images = get_exact_images(images_, catalogue="dockerhub_exact_images")

    if docker_images == None:
        return

    
    for exact_images in docker_images:

        if len(exact_images) != 0: 

            for ky, val in exact_images.items():

                if ky not in ["type","entity_id"]:

                    img_data = cols.copy()
                    img_data["docker_images"] = "docker_images"
                    img_data["container_name"] = val[0]["name"]
                    img_data["Docker_Url"] = val[0]["Docker_Url"]
                    img_data["Notes"] = ""

                    if val[0]["Official image"]: 
                        img_data["CertOfImageAndPublisher"] =  "Official Image"
                    if val[0]["Verified Publisher"]: 
                        img_data["CertOfImageAndPublisher"]  = "Verified Publisher"
                        
                    img_data_type = entity_type_mapper(exact_images["type"] ,  str(exact_images["entity_id"]))
                    img_data.update(img_data_type)
                    row_data.append(img_data)
    

    write_to_csv(row_data , "docker_images")


def openshift_images():
    """
    Saves Openshift images to openshift_images.csv.
    
    """
    
    row_data = []
    cols = csv_columns(table_name="openshift_images")
    images_ = search_results()
    quay_images = get_exact_images(images_, catalogue="quay_exact_images")

    if quay_images == None:
        return

    for exact_images in quay_images:

        if len(exact_images) != 0: 
            for ky, val in exact_images.items():
                if ky not in ["type","entity_id"]:
                    img_data = cols.copy()
                    img_data["openshift_images"] = "openshift_images"
                    img_data["container_name"] = val[0]["name"]
                    img_data["Openshift_Correspondent_Image_Url"] = val[0]["url"]
                    
                    img_data_type = entity_type_mapper(exact_images["type"] , str(exact_images["entity_id"]))
                    img_data["DockerImageType"] = list(img_data_type.keys())[0].title()

                    img_data.update(img_data_type)
                    row_data.append(img_data)
    
    write_to_csv(row_data , "openshift_images")

