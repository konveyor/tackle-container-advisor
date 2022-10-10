import logging
import re
import json
import requests
from sqlite3 import Error
import sqlite3
import docker 
import os
import configparser

# NLP
import pandas as pd
from requests import session
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity



#config file
config = configparser.ConfigParser()
config_data = os.path.join("config/kg.ini")
config.read([config_data])

#path to DB
db_path    =  config["database"]["database_path"]

def create_db_connection():
    """
    Create connection to database

    Args:

        database_path (str): path to the database

    Returns:

        _type_: sqlite3 connection 

    """
    
    connection = None
    
    try:
        connection = sqlite3.connect(db_path)
    except Error as e:
        logging.error(f'{e}: Issue connecting to db. Please check whether the .db file exists.')
    return connection



def clean_string_value(value):

    """
    arguments:   
        value : str 
    Return:             
        str : formated str
    """    
    if value:
        value = str(value).strip()
        value = value.replace(u'\u00a0', ' ')
        value = re.sub(r'[^\x00-\x7F]+', ' ', ' ' + str(value) + ' ').strip()
    else:
        value = ''
        
    return value


def get_table(table_name="entities"):
    """
    Connect to a table
    """

    connection =   create_db_connection()
    cursor = connection.cursor()
    cursor.execute("SELECT   *  FROM {} ".format(table_name))
    return cursor

def remove_tags_url(url:str)-> str:
    """
    Remove tag from url links
    Args:
        url (str): input url

    Raises:
        ValueError: _description_

    Returns:
        str: A url with no tag
    """
    
    image_url =""
    
    if "https" in url or "http" in url:
        url_splt = url.split(":")
        image_url = url_splt[0]+":"+url_splt[1]
    else:
        image_url = url.split(":")[0]
    
    print(image_url)
    return image_url

################################################################################
 ############         DOCKERHUB UTILS                             ##############
#################################################################################


def get_column(table_name:str, column_index:int) -> list:
    """_summary_

    Args:
        table_name (str): table_name from database.
        column_index (int): index of a column from table_name

    Returns:
        list: list of data from column
    """
    cur = get_table(table_name=table_name)
    container_names= []

    for entity  in cur.fetchall():
        container_names.append(entity[column_index])
    return container_names


def container_urls():
    """
    Retrieve all docker container urls from docker_images table
    """
    url_cur = get_table(table_name="docker_images")
    urls =[]
    for row in url_cur.fetchall():
        urls.append(row[10])
    return urls




def is_exact_match(image_name: str, entity_name: str) -> bool:
    """
    get exact match()

    Args:
        image_name (str): image_name from dockerhub
        entity_name (str): entity from database

    Returns:
        bool: True if image_name==entity_name, otherwise False
    """

    
    name = image_name

    if not isinstance(image_name, str) or not isinstance(entity_name, str):
        logging.error("you can only compare two string")
        exit()

    if entity_name.lower() == name.lower():
        return True
    else:
        return False


def line_similarity(linelist: list, query: str):
    """
    Take a list of lines, vectorize it and compare the similarity between the query and lines


    Args:
        linelist (list): List of all lines
        query (str): Search query 

    Raises:
        ValueError: _description_

    Returns:
        (list): _description_
        (int): 
    """
    lines = {}

    for id, line in enumerate(linelist):
        parse_line = re.sub("[^A-Za-z0-9]+", " ", str(line)).strip()
        if len(parse_line) > 0:
            lines[str(id)] = parse_line

    line_vectorizer = TfidfVectorizer()
    vectorized_line = line_vectorizer.fit_transform(linelist)

    formatted_query = re.sub("[^A-Za-z0-9]+", " ", str(query))

    query = formatted_query.lower().strip()
    if not query:
        raise ValueError("Formatted query string cannot be empty")

    vectorized_query = line_vectorizer.transform([query])
    line_score = cosine_similarity(vectorized_query, vectorized_line)

    line_score = line_score[0]
    topscore_lines = line_score.argsort()[-5:][::-1]

    return topscore_lines, line_score

    
def format_images(images:list)-> list:
    """
    Create the return structure for all images

    Args:
        images (list): All images

    Returns:
        (list): Structure
    """

 
    images_list = []
    if images == None : return images_list

    for im in images:

        img_dict = {}
        img_dict ={"name": " " , 'Official image': False , 'Verified Publisher':  False, "Description": '' ,'star_count':'',"Docker_Url": '', 'OS':[] }

        img_dict["name"] = im["name"]

        if "/" in im['name']: img_dict['Verified Publisher'] = True
        
        else: img_dict['Official image']  = im["is_official"]
        img_dict['star_count'] = im['star_count']
        img_dict["Docker_Url"] = docker_href(im['name'])
        img_dict['OS']= []
        images_list.append(img_dict)

    return images_list
   

def docker_href( image_name: str) -> str:
    """
    image_name url 

    Args:
        image_name (str): Image entity name 

    Returns:
        str: href of a DockerHub image. 
    """

    href = ""

    if "/" in image_name:
        href = "https://hub.docker.com/r/" + image_name

    else:
        href = "https://hub.docker.com/_/" + image_name

    return href


################################################################################
 ############         QUAY UTILS                             ################
#################################################################################

