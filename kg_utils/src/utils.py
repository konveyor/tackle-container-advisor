import logging
import re
import json
import requests
from sqlite3 import Error
import sqlite3
import docker 
import os

# NLP
import pandas as pd
from requests import session
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity



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


################################################################################
 ############         DOCKERHUB UTILS                             ##############
#################################################################################

def is_exact_match(image_name: str, entity_name: str) -> bool:
    """_summary_

    Args:
        image_name (str): _description_
        entity_name (str): _description_

    Returns:
        bool: _description_
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
    """_summary_

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


   