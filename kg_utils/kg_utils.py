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

import os
import json
import re
import configparser
import logging
import sqlite3
from sqlite3 import Error
from packaging import version as pv

config = configparser.ConfigParser()
common = os.path.join("config", "common.ini")
kg = os.path.join("config", "kg.ini")
config.read([common, kg])


def cleanStrValue(value):
    """
    Clean input strings

    :param value: input string
    :returns: value

    """
    if value:
        value = str(value).strip()
        value = value.replace(u'\u00a0', ' ')
        value = re.sub(r'[^\x00-\x7F]+', ' ', ' ' + str(value) + ' ').strip()
    else:
        value = ''
    return value


def table_names(connect):
    """_summary_

    Args:
        connect (_type_): _description_

    """
    cursor = connect.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = []

    for col in cursor.fetchall():
        tables.append(col[0])
    return tables


def explore_db(conn):
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = table_names(conn)
    for table in tables:
        print(table)
        print("===============================")
        cur = conn.cursor()
        cur.execute("SELECT * FROM  {}".format(table))
        # view Column names
        col_name_list = [tuple[0] for tuple in cur.description]
        print(col_name_list)
        # view first two rows
        for row in cur.fetchmany(5):
            print(row)
        print("\n")


def type_mapper(db_connection):
    """Maps each entity to the corresponding type

    :param conn:  A connection to mysql
    :type conn:  <class 'sqlite3.Connection'>

    :returns: {'1': 'Lang', '2': 'Lib', '3': 'App Server', '4': 'Runtime', '5': 'App', '6': 'OS'}
    :rtype: dict


    """

    type_cursor = db_connection.cursor()
    type_cursor.execute("SELECT * FROM entity_types")
    type_map = {}

    for type_tuple in type_cursor.fetchall():
        type_id, tech_type = type_tuple

        type_map[str(type_id)] = tech_type

    return type_map


def entity_mapper(db_connection):
    """
    Method to load entity names from "entities" table from mysql db

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
        if entity == 'Windows|*':
            entity = 'Windows'
        if entity == 'Linux|*':
            entity = 'Linux'
        parent_class[str(class_id)] = entity
    return parent_class


def save_json(json_file, file_name):
    """
    Save json file to the ontologies folder

    """
    dst_pth = config["general"]["kg_dir"]

    if not os.path.isdir(dst_pth):
        os.mkdir(dst_pth)

    with open(os.path.join(dst_pth, config["filenames"][file_name]), encoding="utf-8", mode="w") as comp_file:
        comp_file.write(json.dumps(json_file, indent=2))


def create_class_type_mapper(db_connection):
    """
    Method to extract Entities from sql db and maps each entity to the  corresponding type ("APP, APP SERVER , RUNTIME , LANG , LIB, OS)

    :param db_connection: A connection to mysql
    :type db_connection:  <class 'sqlite3.Connection'>


    :returns: Saves entity_mentions  in config["kg"]["class_type_mapper_raw"]
    :retype: None
    """

    entity_mentions = {}
    entity_mentions["kg_version"] = config["general"]["version"]
    entity_mentions["mappings"] = {}

    types_ = type_mapper(db_connection)
    entity_names = entity_mapper(db_connection)

    cursor = db_connection.cursor()
    cursor.execute("SELECT * FROM  entity_mentions")
    mentions = cursor.fetchall()

    for mention in mentions:
        class_type = types_[str(mention[2])]
        index = str(mention[3])
        entity = entity_names[index]
        entity_mentions["mappings"][entity] = class_type

    # add Linux|* and Windows|*
    entity_mentions["mappings"]['Linux|*'] = 'OS'
    entity_mentions["mappings"]['Windows|*'] = 'OS'

    save_json(entity_mentions, "class_type_mapper")


def create_inverted_compatibility_kg(db_connection):
    """
    Create inverted compatibility kwonledge graph.

    :param db_connection:  A connection to mysql
    :type db_connection:  <class 'sqlite3.Connection'>

    :returns: Saves inverted compatibility kwonledge to the ontology folder
    :rtype: JSON file

    """

    inverted_compatibilty_kg = {}
    inverted_cursor = db_connection.cursor()
    inverted_cursor.execute("SELECT * FROM entity_relations")

    entity_ids = entity_mapper(db_connection)

    type_ids = type_mapper(db_connection)

    inverted_compatibilty_kg["KG Version"] = config["general"]["version"]

    for inverted_ids in inverted_cursor.fetchall():
        inverted_lst = []
        parent_type_id, parent_id, child_type_id, child_id = inverted_ids[1:5]

        inverted_lst.append({"Parent Type": type_ids[str(parent_type_id)], "Parent Class": entity_ids[str(parent_id)],
                             "Child Type": type_ids[str(child_type_id)]})

        child_class = entity_ids[str(child_id)]

        inverted_compatibilty_kg[child_class] = inverted_lst

    save_json(inverted_compatibilty_kg, "inverted_compatibilityKG")


def create_compatibilty_kg(db_connection):
    """
    Create compatibility KG.

    :param db_connection:  A connection to mysql
    :type db_connection:  <class 'sqlite3.Connection'>

    :returns: Saves compatibility KG to the ontology folder
    :rtype: JSON file

    """

    CompatibilityKG = {}
    compatibility_list = []

    CompatibilityKG["KG Version"] = config["general"]["version"]

    type_ids = type_mapper(db_connection)
    entity_ids = entity_mapper(db_connection)

    relation_cursor = db_connection.cursor()
    relation_cursor.execute("SELECT * FROM entity_relations")

    for ids in relation_cursor.fetchall():
        parent_type_id, parent_id, child_type_id, child_id = ids[1:5]

        compatibility_list.append(
            {"Parent Type": type_ids[str(parent_type_id)], "Parent Class": entity_ids[str(parent_id)],
             "Child Type": type_ids[str(child_type_id)], "Child Class": entity_ids[str(child_id)]})

    CompatibilityKG["Compatibility List"] = compatibility_list

    save_json(CompatibilityKG, "compatibilityKG")


def create_base_os_kg(db_connection):
    """
    Create base OS  KG.

    :param db_connection:  A connection to mysql
    :type db_connection:  <class 'sqlite3.Connection'>

    :returns: Saves base OS  KG to the ontology folder
    :rtype: JSON file

    """

    # current base OS list
    current_base_os = ["dockerhub", "openshift"]
    current_corresponding_kg_names = ["baseOSKG", "openshift_baseOSKG"]

    tables = catalogs(db_connection)

    for table in tables:
        if table in current_base_os:

            kg_name = current_corresponding_kg_names[current_base_os.index(
                table)]
            table_name = table + "_baseos_images"
            base_cursor = db_connection.cursor()
            base_cursor.execute("SELECT * FROM  {}".format(table_name))

            mapped_os = entity_mapper(db_connection)

            base_os = {}
            base_os["KG Version"] = config["general"]["version"]
            base_os["Container Images"] = {}

            for docker_baseos_image in base_cursor.fetchall():
                baseos_image, os_id, docker_url = docker_baseos_image[
                    1], docker_baseos_image[2], docker_baseos_image[3]
                Note, Status = docker_baseos_image[4], docker_baseos_image[6]
                base_os["Container Images"][baseos_image] = {}
                base_os["Container Images"][baseos_image]["OS"] = [
                    {"Class": mapped_os[str(os_id)], "Variants": "", "Version": "", "Type": "OS", "Subtype": ""}]

                base_os["Container Images"][baseos_image]["Lang"], base_os["Container Images"][baseos_image]["Lib"] = [
                ], []
                base_os["Container Images"][baseos_image]["App"], base_os["Container Images"][baseos_image][
                    "App Server"] = [], []

                base_os["Container Images"][baseos_image]["Plugin"], base_os["Container Images"][baseos_image]["Runlib"], \
                    base_os["Container Images"][baseos_image]["Runtime"] = [], [], []
                base_os["Container Images"][baseos_image]["image_url"] = docker_url

                base_os["Container Images"][baseos_image]["Notes"], base_os["Container Images"][baseos_image][
                    "CertOfImageAndPublisher"] = Note, Status

            save_json(base_os, kg_name)


def create_inverted_base_os_kg(db_connection):
    """
    Create  inverted openshift based OS KG.

    :param db_connection:  A connection to mysql
    :type db_connection:  <class 'sqlite3.Connection'>

    :returns: Saves inverted openshift based OS KG to the ontology folder
    :rtype: JSON file

    """
    tables = catalogs(db_connection)
    # current base OS list
    current_base_os = ["dockerhub", "openshift"]
    current_corresponding_kg_names = ["baseOSKG", "openshift_baseOSKG"]

    for table in tables:
        if table in current_base_os:
            base_cursor = db_connection.cursor()

            table_name = table + "_baseos_images"
            kg_name = "inverted_" + \
                current_corresponding_kg_names[current_base_os.index(table)]
            base_cursor.execute("SELECT * FROM {}".format(table_name))
            mapped_os = entity_mapper(db_connection)
            inverted_baseos_kg = {}
            inverted_baseos_kg["KG Version"] = config["general"]["version"]

            for base_image in base_cursor.fetchall():
                os, os_id = base_image[1], base_image[2]
                inverted_baseos_kg[mapped_os[str(os_id)]] = [os]

            save_json(inverted_baseos_kg, kg_name)


def get_os_variants(db_connection):
    """
    Extract OS Variants from the entities database.

    :param db_connection:  A connection to mysql
    :type db_connection:  <class 'sqlite3.Connection'>

    :returns: Dictionary containing variants for each OS type.
    :rtype: dict

    """

    cur = db_connection.cursor()
    cur.execute("SELECT * FROM  entities")
    all_os = []
    os_variants = {}
    types_map = type_mapper(db_connection)

    for entity in cur.fetchall():

        entity_name, entity_type_id = entity[1:3]
        type_ = types_map[str(entity_type_id)]
        if type_ == "OS":
            all_os.append(entity_name)

        if entity_name.split("|")[-1] == "*" and type_ == "OS":
            os_variants[entity_name] = []

    OS = [os for os in all_os if os not in list(os_variants.keys())]

    os_variants["|*"] = OS

    for os_variant in list(os_variants.keys()):

        if os_variant == "|*":
            continue

        var_lst = []
        for variant in OS:
            if os_variant.split("|")[0] in variant:
                var_lst.append(variant)
        os_variants[os_variant] = var_lst

    return os_variants


def create_compatibility_os_kg(db_connection):
    """
    Create  compatibility  OS  KG.

    :param db_connection:  A connection to mysql
    :type db_connection:  <class 'sqlite3.Connection'>

    :returns: Saves  compatibility OS  KG to the ontology folder.
    :rtype: JSON file


    """

    cursor1 = db_connection.cursor()
    cursor2 = db_connection.cursor()
    entities = entity_mapper(db_connection)
    type_ids = type_mapper(db_connection)

    cursor1.execute("SELECT * FROM  entity_relations")
    cursor2.execute("SELECT * FROM  entity_relations")
    compatibilty_os_kg = {}
    compatibilty_os_kg["KG Version"] = config["general"]["version"]

    os_variant = get_os_variants(db_connection)

    for relation in cursor1.fetchall():
        parent_type_id, _, _, child_id = relation[1:5]

        parent_type = type_ids[str(parent_type_id)]

        if parent_type == "OS":
            child = entities[str(child_id)]
            compatibilty_os_kg[child] = []

    for entity_relation in cursor2.fetchall():

        type_id, parent_id, child_type_id, child_id = entity_relation[1:5]

        type_ = type_ids[str(type_id)]

        parent_os = entities[str(parent_id)]
        child = entities[str(child_id)]

        if type_ == "OS":

            if parent_os in list(os_variant.keys()):
                os_list = os_variant[parent_os]
                for os_ in os_list:
                    compatibilty_os_kg[child].append(os_)

            else:
                compatibilty_os_kg[child].append(parent_os)

    save_json(compatibilty_os_kg, "compatibilityOSKG")


def create_cot_kg(db_connection):
    """
    Create  COT  KG.

    :param db_connection:  A connection to mysql
    :type db_connection:  <class 'sqlite3.Connection'>

    :returns: Saves COT KG to the ontology folder
    :rtype: JSON file

    """

    cur = db_connection.cursor()
    cur.execute("SELECT * FROM  entities")
    entities = entity_mapper(db_connection)
    cot_kg = {}
    cot_kg['Version'] = config["general"]["version"]

    cots = []
    for entity in cur.fetchall():
        entity_name = entity[1]
        cots.append(entity_name)

    cot_kg["COTS"] = cots

    save_json(cot_kg, "COTSKG")


def create_version(db_connection):
    """
    Create  versions  KG.

    :param db_connection:  A connection to mysql
    :type db_connection:  <class 'sqlite3.Connection'>

    :returns: Saves versions along with release cost to the ontology folder.
    :rtype: JSON file
    """

    cur = db_connection.cursor()
    cur.execute("SELECT * FROM  entity_versions")
    entities = entity_mapper(db_connection)
    ver_kg = {}
    ver_kg['Version'] = config["general"]["version"]

    versions = {}
    for ver in cur.fetchall():

        if int(config['general']['version'][-1]) >= 4:
            entity_id, version, release_date, end_date = ver[1:]
        else:
            entity_id, version, release_date, end_date, cost = ver[1:]

        entity_name = entities[str(entity_id)]

        if entity_name not in versions.keys():
            versions[entity_name] = []

        if int(config['general']['version'][-1]) >= 4:
            versions[entity_name].append([version, release_date, end_date])
        else:
            versions[entity_name].append(
                [version, release_date, end_date, cost])

    for entity_name in versions.keys():
        latest_version = ""
        for entry in versions[entity_name]:
            if latest_version == "" or pv.parse(latest_version) < pv.parse(entry[0]):
                latest_version = entry[0]
        for entry in versions[entity_name]:
            entry.append(latest_version)

    ver_kg["Entity"] = versions
    save_json(ver_kg, "entity_versionsKG")


def create_catalog_kg(con):

    catalog_names = "catalogKG"
    cursor = con.cursor()
    cursor.execute("SELECT *  FROM  catalogs")
    catalog_kg = {}
    names = []
    for name in cursor.fetchall():
        names.append(name[1])

    catalog_kg["names"] = names
    save_json(catalog_kg, catalog_names)


def create_db_connection(db_file):
    """
    Create Mysql db connection

    :param db_file: path to mysql file
    :type db_file:  .db file

    :returns: Connection to mysql db

    :rtype:  <class 'sqlite3.Connection'>

    """

    connection = None

    try:
        connection = sqlite3.connect(db_file)
    except Error as e:
        logging.error(
            f'{e}: Issue connecting to db. Please check whether the .db file exists.')
    return connection


def catalogs(connect):
    """
    retrieve all catalog names.
    Args:
        connect (_type_): Connection to the main database.
    """
    cursor = connect.cursor()
    cursor.execute("SELECT * FROM catalogs")
    catalog_names = []
    for name in cursor.fetchall():
        catalog_names.append(name[1])

    return catalog_names


def create_catalog_image_kg(connect):
    """
    Create a knowledge graph for each catalog.

    "catalog_name" + "_images"
    Args:
        connect (_type_):Connection to the database.

    """

    cat_names = catalogs(connect)
    entities = entity_mapper(connect)
    image_kg = {}

    image_kg["KG Version"] = config["general"]["version"]
    class_types = ["OS", "Lang", "Lib", "App",
                   "App Server", "Plugin", "Runlib", "Runtime"]

    for catalog in cat_names:
        cursor = connect.cursor()
        table_name = catalog + "_images"
        kg_name = catalog + "_imageKG"
        cursor.execute("SELECT * FROM {}".format(table_name))
        image_kg["Container Images"] = {}
        inverted_images_kg = {}

        col_name_list = [tuple[0] for tuple in cursor.description]

        for image in cursor.fetchall():

            image_data = image[1:11]
            rem_row_data = zip(col_name_list[11:], image[11:])

            map_class_type_ids = zip(image_data[1:9], class_types)
            container_name, image_url = image_data[0], image_data[-1]
            image_kg["Container Images"][container_name] = {}

            for row in map_class_type_ids:
                class_id, type_name = row[0], row[1]
                if type_name == "OS":
                    image_kg["Container Images"][container_name]["OS"] = [
                        {"Class": entities[str(class_id)], "Variants": "", "Versions": "", "Type": type_name, "Subtype": ""}]
                    continue
                if class_id == None:
                    image_kg["Container Images"][container_name][type_name] = []
                else:
                    image_kg["Container Images"][container_name][type_name] = [
                        {"Class": entities[str(class_id)], "Variants": "", "Versions": "", "Type":type_name, "Subtype": ""}]

            image_kg["Container Images"][container_name]["image_url"] = image_url
            for rem in rem_row_data:
                col_name, col_data = rem[0], rem[1]
                image_kg["Container Images"][container_name][col_name] = col_data

        save_json(image_kg, kg_name)


def create_inverted_catalog_kg(connect):
    """"   
    Keyword arguments:
    argument -- description
    Return: return_description
    """

    tables = catalogs(connect)

    for table in tables:
        table_name = table + "_images"
        kg_name = "inverted_"+table + "_imageKG"
        inverted_cur = connect.cursor()
        inverted_cur.execute("SELECT * FROM {}".format(table_name))
        entities = entity_mapper(connect)
        inverted_images_kg = {}
        inverted_images_kg['Version'] = config["general"]["version"]
        cur = connect.cursor()
        cur.execute("SELECT * FROM {}".format(table_name))

        # init inverted_image_kg
        for img in cur.fetchall():
            type_ids_init = img[2:10]
            for type_id in type_ids_init:
                if type_id == None:
                    pass
                else:
                    inverted_images_kg[entities[str(type_id)]] = []

        # fill inverted_image_kg
        for img in inverted_cur.fetchall():
            container_name, type_ids = img[1], img[2:10]
            for type_id in type_ids:
                if type_id == None:
                    pass
                else:
                    inverted_images_kg[entities[str(type_id)]].append(
                        container_name)

        save_json(inverted_images_kg, kg_name)


if __name__ == '__main__':
    logging.basicConfig(
        level=logging.INFO, format="[%(asctime)s] %(name)s:%(levelname)s in %(filename)s:%(lineno)s - %(message)s", filemode='w')

    try:
        version = config["general"]["version"]
        db_dir = config["general"]["db_dir"]
    except KeyError as k:
        logging.error(f'{k}  is not a key in your config file(s).')
        exit()

    db_path = os.path.join(db_dir, version + ".db")
    if not os.path.isfile(db_path):
        logging.error(
            f'{db_path} is not a file. Run "sh setup" from /tackle-advise-containerizeation folder to generate db files')
        exit()

    else:

        connection = create_db_connection(db_path)

        create_class_type_mapper(connection)
        create_cot_kg(connection)
        create_version(connection)
        create_base_os_kg(connection)

        create_compatibility_os_kg(connection)
        create_compatibilty_kg(connection)
        # explore_db(connection)

        create_catalog_kg(connection)
        create_catalog_image_kg(connection)
        create_inverted_catalog_kg(connection)

        create_inverted_compatibility_kg(connection)
        create_inverted_base_os_kg(connection)
