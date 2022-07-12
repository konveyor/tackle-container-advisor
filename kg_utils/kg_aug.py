import sqlite3
import csv
import re
import sys, getopt
from os.path import exists
import pandas as pd
import json
import argparse
from qwikidata.linked_data_interface import get_entity_dict_from_api

value_constraints = {
    "entities": {"COTS": {"Y", "N"}, "Legacy": {"Y", "N"}, "ContainerImage": {"Y", "N"}, "OpenSource": {"Y", "N"}},
    "entity_mentions": {"source": {"others", "also_known_as", "rediects_transclusions"}},
    "entity_versions": {"opensource": {"True", "False"}}
}

default_value = {
    "entities": {"COTS": "N", "Legacy": "N", "ContainerImage": "N", "OpenSource": "N", "external_link": "{}"}
}

accept_null = {
    "operator_images": {"OS", "lang", "lib", "app", "app_server", "plugin", "runlib", "runtime"},
    "openshift_images": {"OS", "lang", "lib", "app", "app_server", "plugin", "runlib", "runtime"},
    "docker_images": {"OS", "lang", "lib", "app", "app_server", "plugin", "runlib", "runtime"},
    "docker_environment_variables": {"Required", "Default_Values"},
    "docker_baseos_images": {"OpenShift_Correspondent_Image_URL", "OpenShiftStatus", "Notes"},
    "openshift_baseos_images": {"Notes", "OpenShiftStatus", "DockerImageType"},
    "entity_versions": {"release_date", "end_date"}
}

def get_input_batch(filename):
    """
         get the batch input from a csv file
         args:
             filename: CSV file with all the input data

         returns: dictionary of the data to be inserted into KB
    """
    data = []
    if exists(filename):
        with open(filename, newline='') as f:
            reader = csv.reader(f)
            data = list(reader)
    for d, input in enumerate(data):
        combineStIdx = -1
        combineEndIdx = -1
        for i, entry in enumerate(input):
            if "{" in entry and "}" not in entry:
                combineStIdx = i
            elif "}" in entry and "{" not in entry:
                if combineStIdx >= 0:
                    combineEndIdx = i
                    break
        if combineStIdx >= 0 and combineEndIdx >= 0:
            combinedStr = ""
            for j in range(combineStIdx, combineEndIdx + 1):
                combinedStr += input[j]
                if j != combineEndIdx:
                    combinedStr += ","
            data[d][combineStIdx] = combinedStr
            data[d] = data[d][:combineStIdx + 1] + data[d][combineEndIdx + 1:]
    # print(data)
    return (data)


def check_input_batch(input_entry, cur):
    """
         set of validation checks (format, type, length etc.) before inserting into KB
         args:
             input_entry: CSV file with all the input data
             cur: cursor pointer to the KB database
         returns: dictionary of the data to be inserted into KB
    """
    tables = cur.execute("SELECT name FROM sqlite_master WHERE type='table';")
    table_names = []
    for table_name in tables:
        if table_name[0] != "sqlite_sequence":
            table_names.append(table_name[0])
    # print(table_names)
    table_name = ""
    userColVals = []
    process_entry = True
    if len(input_entry) <= 1:
        process_entry = False
    else:
        table_name = input_entry[0]
        if table_name not in table_names:
            process_entry = False
        if process_entry:
            getColCmd = "PRAGMA table_info('" + table_name + "') "
            columns = cur.execute(getColCmd).fetchall()
            # print(table_name, len(columns), len(input_entry))
            if len(columns) != len(input_entry):  # id is not present in input..
                process_entry = False
            i = 1
            if process_entry:
                for col in columns:
                    # print("Column name:",col[1],"Type:",col[2])
                    if col[1] == "id":
                        continue
                    userval = input_entry[i].strip()
                    if col[2] == "integer":
                        if userval == "":
                            userval = "NULL"
                        if not userval.isdigit():
                            can_accept_null = False
                            if table_name in accept_null.keys():
                                if col[1] in accept_null[table_name]:
                                    can_accept_null = True
                            if can_accept_null:
                                if userval != "NULL":
                                    process_entry = False
                    elif col[2].find('TEXT(') >= 0:
                        start = col[2].find('TEXT(') + 5
                        end = col[2].find(')', start)
                        text_len_limit = int(col[2][start:end])
                        if len(userval) > text_len_limit:
                            process_entry = False
                    if process_entry:
                        if table_name in value_constraints.keys():
                            if col[1] in value_constraints[table_name].keys():
                                if userval not in value_constraints[table_name][col[1]]:
                                    process_entry = False
                    userColVals.append(userval)
                    # print(process_entry)
                    i = i + 1
    return (table_name, userColVals, process_entry)


def get_input_cmdline(cur):
    """
         To receive an input from the command line for interactive mode
         args:
             cur: cursor pointer to the KB database
         returns: the tablename and the list of values for the various fields
    """
    tables = cur.execute("SELECT name FROM sqlite_master WHERE type='table';")
    table_names = []
    for table_name in tables:
        if table_name[0] != "sqlite_sequence":
            table_names.append(table_name[0])
    print("Tables in the database:", table_names)
    table_accept = False
    table_name = ""
    while not table_accept:
        table_name = input("Enter the table name of your choice:")
        if table_name in table_names:
            table_accept = True
        else:
            print("Unknown table -- please re-enter")
    getColCmd = "PRAGMA table_info('" + table_name + "') "
    columns = cur.execute(getColCmd).fetchall()
    userColVals = []
    for col in columns:
        # print("Column name:",col[1],"Type:",col[2])
        if col[1] == "id":
            continue
        userval_accept = False
        while not userval_accept:
            collValCmd = "Enter the value for column: " + col[1] + " (type: " + col[2]
            valConstrSet = {}
            valConstr = ""
            if table_name in value_constraints.keys():
                if col[1] in value_constraints[table_name].keys():
                    valConstrSet = value_constraints[table_name][col[1]]
                    valConstr = " accepted values: [ "
                    for entry in valConstrSet:
                        valConstr = valConstr + entry + " "
                    valConstr = valConstr + "]"

            defaultConstr = ""
            if table_name in default_value.keys():
                if col[1] in default_value[table_name].keys():
                    defaultConstr = " to skip enter " + default_value[table_name][col[1]]

            nullConstr = ""
            can_accept_null = False
            if table_name in accept_null.keys():
                if col[1] in accept_null[table_name]:
                    can_accept_null = True
                    nullConstr = " to skip enter NULL"
            collValCmd = collValCmd + valConstr + defaultConstr + nullConstr + ")"
            userval = input(collValCmd)
            if col[2] == "integer":
                if userval.isdigit():
                    userval_accept = True
                else:
                    if can_accept_null:
                        if userval == "NULL":
                            userval_accept = True
                        else:
                            print("Type not integer/NULL -- please re-enter")
                    else:
                        print("Type not integer -- please re-enter")
            elif col[2].find('TEXT(') >= 0:
                start = col[2].find('TEXT(') + 5
                end = col[2].find(')', start)
                text_len_limit = int(col[2][start:end])
                if len(userval) <= text_len_limit:
                    userval_accept = True
                else:
                    print("Text exceeds length -- please re-enter")
            else:
                userval_accept = True
            if userval_accept:
                if len(valConstrSet) > 0:
                    if userval not in valConstrSet:
                        userval_accept = False
                        print("Not a valid entry for column -- please re-enter")
            if userval_accept:
                userColVals.append(userval)
    return (table_name, userColVals)


def check_for_entry_in_table(cur, table_name, column_name, value):
    # print(table_name,column_name)
    sqlquery = "SELECT " + column_name + " FROM " + table_name + " WHERE " + column_name + " = \"" + value + "\""
    answer = cur.execute(sqlquery)
    return (answer.fetchall())


def check_if_duplicate(table_name, userColVals, cur):
    getColCmd = "PRAGMA table_info('" + table_name + "') "
    columns = cur.execute(getColCmd).fetchall()
    ## check for duplicates -- which is table based:
    add_to_table = True
    if table_name != "entity_relations" and table_name != "entity_versions":
        if len(check_for_entry_in_table(cur, table_name, columns[1][1], userColVals[0])) > 0:
            add_to_table = False
        if table_name == "entities":
            if len(check_for_entry_in_table(cur, "entity_mentions", "entity_mention_name", userColVals[0])) > 0:
                add_to_table = False
    if table_name == "entities" or table_name == "entity_mentions" or table_name == "entity_relations":
        getIdQuery = "SELECT max(id) FROM entity_types"
        answer = cur.execute(getIdQuery)
        maxEntityTypeId = answer.fetchall()[0][0]
        if table_name == "entities" or table_name == "entity_mentions":
            if int(userColVals[1]) > maxEntityTypeId or int(userColVals[1]) <= 0:
                add_to_table = False
        else:
            if int(userColVals[0]) > maxEntityTypeId or int(userColVals[0]) <= 0 or int(
                    userColVals[2]) > maxEntityTypeId or int(userColVals[2]) <= 0:
                add_to_table = False
    return add_to_table


def alter_case_format(table_name, userColVals):
    if table_name == "entities":
        userColVals[0] = userColVals[0].lower()


def insert_into_table(table_name, userColVals, cur):
    """
         set of validation checks (format, type, length etc.) before inserting into KB
         args:
             table_name: table name
             userColVals:
             cur: cursor pointer to the KB database
         returns: dictionary of the data to be inserted into KB
    """
    count = 1
    list_len = len(userColVals)
    getIdQuery = "SELECT max(id) FROM " + table_name
    answer = cur.execute(getIdQuery)
    myId = answer.fetchall()[0][0] + 1
    sqlquery = "INSERT INTO " + table_name + " values (" + str(myId) + ","
    for colVal in userColVals:
        if colVal.isdigit() or colVal == "NULL":
            sqlquery += colVal
        else:
            sqlquery += ("'" + colVal + "'")
        if count < list_len:
            sqlquery += ","
        count += 1
    sqlquery += ")"
    print(sqlquery)
    cur.execute(sqlquery)


def generate_mentions_wiki(cur, my_entity_name):
    """
         generate mentions from wikidata when a new entity is added to the entity table
         args:
             cur: cursor pointer to the KB database
             my_entity_name: new entity thats added to the KB

         returns: newly generated mentions from wikiata
    """
    gen_mentions = []
    my_qid = ""
    sqlquery = "SELECT external_link FROM entities WHERE entity_name" + " = \"" + my_entity_name + "\""
    # print(sqlquery)
    answer = cur.execute(sqlquery)
    result = str(answer.fetchall()[0][0])
    result = result.replace("'", '"')
    # print(result)
    try:
        result_dict = json.loads(result)
        # print(result_dict)
        if "qid" in result_dict.keys():
            my_qid = result_dict["qid"]
            java_dict = get_entity_dict_from_api(my_qid)
            if "aliases" in java_dict.keys():
                if "en" in java_dict["aliases"].keys():
                    for x in java_dict["aliases"]["en"]:
                        if "value" in x.keys():
                            gen_mentions.append((x["value"], "also_known_as"))
    except json.decoder.JSONDecodeError:
        pass
    return gen_mentions


def enter_mentions_to_table(cur, gen_mentions, entity_id, entity_type_id):
    """
         add the newly generated mentions generated from
         args:
             cur: cursor pointer to the KB database
             my_entity_name: new entity thats added to the KB

         returns: newly generated mentions from wikiata
    """
    for val in gen_mentions:
        userColVals = [val[0], entity_type_id, entity_id, val[1]]
        add_to_table = check_if_duplicate("entity_mentions", userColVals, cur)
        if add_to_table:
            insert_into_table("entity_mentions", userColVals, cur)
            print("Mention " + val[0] + " inserted to table..")


# main insert new entry function
def insert_to_kg(mode, batch_filename, cur):
    """
         set of validation checks (format, type, length etc.) before inserting into KB
         args:
             table_name: table name
             userColVals:
             cur: cursor pointer to the KB database
         returns: dictionary of the data to be inserted into KB
    """
    assert (mode == "batch" or mode == "interactive"), 'Mode is either batch or interactive'
    num_entries = 1
    batch_data = []
    if mode == "batch":
        batch_data = get_input_batch(batch_filename)
        num_entries = len(batch_data)
    if num_entries == 0:
        print("No entries to process")
    else:
        for i in range(0, num_entries):
            table_name = ""
            userColVals = []
            process_entry = True
            if mode == "interactive":
                table_name, userColVals = get_input_cmdline(cur)
            else:
                table_name, userColVals, process_entry = check_input_batch(batch_data[i], cur)
            # print(table_name, userColVals)
            if process_entry:
                alter_case_format(table_name, userColVals)
                add_to_table = check_if_duplicate(table_name, userColVals, cur)
                if add_to_table:
                    insert_into_table(table_name, userColVals, cur)
                    print("Entry " + str(i) + " inserted to table..")
                    if table_name == "entities":
                        my_entity_name = userColVals[0]
                        # autogenerate mentions..
                        gen_mentions = generate_mentions_wiki(cur, my_entity_name)
                        # generate a entity mention with just upper case if not found in wiki.
                        if len(gen_mentions) == 0:
                            gen_mentions.append((my_entity_name.upper(), "others"))
                        if len(gen_mentions) > 0:
                            sqlquery = "SELECT id,entity_type_id FROM entities WHERE entity_name" + " = \"" + my_entity_name + "\""
                            # print(sqlquery)
                            answer = cur.execute(sqlquery)
                            result = answer.fetchall()[0]
                            entity_id = str(result[0])
                            entity_type_id = str(result[1])
                            # print(entity_id,entity_type_id)
                            enter_mentions_to_table(cur, gen_mentions, entity_id, entity_type_id)
                else:
                    print("Entry " + str(i) + " is a duplicate and skipped..")
            else:
                print("Entry " + str(i) + " cannot be processed..")


# edit entities table
def remove_from_entities(table_name, cur, entities_to_remove):
    """
       remove or replace entities from the entities table
       args:
           table_name: str, name of table to edit ('entities')
           cur: cursor pointer to the KB database
           entities_to_remove: list of entity IDs to remove/replace

       returns: nothing, all operations are done on the db connection
    """

    # loop over entities to remove/replace
    for d in entities_to_remove.keys():
        # only delete
        if entities_to_remove[d] == 'NA':
            sqlquery = f"DELETE FROM {table_name} WHERE Id='{d}'"
            cur.execute(sqlquery)
        else:
            # replace as needed

            # entity to be used as replacement
            sqlquery = f"SELECT entity_type_id,external_link,COTS,Legacy,ContainerImage,OpenSource FROM {table_name} WHERE Id='{entities_to_remove[d]}'"
            answer = cur.execute(sqlquery)
            try:
                result = answer.fetchall()[0]
                entity_type_id_ref = str(result[0])
                external_link_ref = str(result[1])
                COTS_ref = str(result[2])
                Legacy_ref = str(result[3])
                ContainerImage_ref = str(result[4])
                OpenSource_ref = str(result[5])
                elr_items = external_link_ref.split(' ')
            except:
                print(f'Invalid Id {entities_to_remove[d]}')
                break

            # entity to be replaced
            sqlquery = f"SELECT entity_type_id,external_link,COTS,Legacy,ContainerImage,OpenSource FROM {table_name} WHERE Id='{d}'"
            answer = cur.execute(sqlquery)
            try:
                result = answer.fetchall()[0]
                entity_type_id = str(result[0])
                external_link = str(result[1])
                COTS = str(result[2])
                Legacy = str(result[3])
                ContainerImage = str(result[4])
                OpenSource = str(result[5])
                el_items = external_link.split(' ')
            except:
                print(f'Invalid Id {d}')
                break

            # check if the entities pair has the same type_id, COTS, Legacy, ContainerImage and Opensource values
            # since they are supposed to represent the same entity, they should be consistent
            if entity_type_id != entity_type_id_ref or COTS != COTS_ref or Legacy != Legacy_ref or \
                    ContainerImage != ContainerImage_ref or OpenSource != OpenSource_ref:
                print(f'Values for {d} and {entities_to_remove[d]} in ENTITIES table are different')
                # continue

            # check if the external links correspond. If not, use the longest one (which is supposed to contain more information)
            matching_external_links = True
            for link in el_items[:-1]:
                if link not in elr_items:
                    matching_external_links = False
                    break

            if not matching_external_links:
                if len(external_link) > len(external_link_ref):
                    sqlquery = f''' UPDATE {table_name}
                                             SET external_link="{external_link}"
                                             WHERE Id="{entities_to_remove[d]}"'''

                    cur.execute(sqlquery)

            # remove row
            sqlquery = f"DELETE FROM {table_name} WHERE Id='{d}'"
            cur.execute(sqlquery)


# remove entities from baseos images tables
def remove_from_baseos_images(table_name, cur, entities_to_remove):
    """
       remove or replace entities (assuming they are OS) from baseos_images tables (dockerhub, openshift)
       args:
           table_name: str, name of table to edit
           cur: cursor pointer to the KB database
           entities_to_remove: list of entity IDs to remove/replace

       returns: nothing, all operations are done on the db connection
    """

    # NOTE: potentially add check for entity type before invoking this function? must be OS

    sqlquery = f"SELECT OS FROM '{table_name}'"
    answer = cur.execute(sqlquery)
    all_os = [str(x[0]) for x in answer.fetchall()]

    for os in entities_to_remove.keys():
        if os in all_os:
            if entities_to_remove[os] == 'NA':
                # entity to delete, remove row
                sqlquery = f"DELETE FROM {table_name} WHERE OS='{os}'"
            else:
                # entity to replace
                sqlquery = f''' UPDATE {table_name}
                                SET OS="{entities_to_remove[os]}"
                                WHERE OS="{os}"'''

            cur.execute(sqlquery)


# remove entities from images tables
def remove_from_images(table_name, cur, entities_to_remove):
    """
       remove or replace entities from images tables (dockerhub, openshift, operator)
       args:
           table_name: str, name of table to edit
           cur: cursor pointer to the KB database
           entities_to_remove: list of entity IDs to remove/replace

       returns: nothing, all operations are done on the db connection
    """
    # get table columns names
    cols = cur.execute(f"SELECT name FROM PRAGMA_TABLE_INFO('{table_name}');")
    columns = [str(x[0]) for x in cols]

    avoid_columns = ['id', 'container_name', 'Docker_URL', 'Notes', 'CertOfImageAndPublisher', \
                     'OpenShift_Correspondent_Image_URL', 'DockerImageType', 'Operator_Correspondent_Image_URL']

    # loop over columns to edit entries
    for c in columns:
        if c not in avoid_columns:
            for en in entities_to_remove.keys():
                if entities_to_remove[en] == 'NA':
                    # entity to delete, replace with NULL values
                    sqlquery = f''' UPDATE {table_name}
                                    SET {c}=NULL
                                    WHERE {c}="{en}"'''
                else:
                    # entity to replace
                    sqlquery = f''' UPDATE {table_name}
                                       SET {c}="{entities_to_remove[en]}"
                                       WHERE {c}="{en}"'''

                cur.execute(sqlquery)


# remove from entity mentions table
def remove_from_entity_mentions(table_name, cur, entities_to_remove, entity_types):
    """
       remove or replace entities from entity_mentions tables
       args:
           table_name: str, name of table to edit
           cur: cursor pointer to the KB database
           entities_to_remove: list of entity IDs to remove/replace

       returns: nothing, all operations are done on the db connection
    """

    # loop over entities to remove/replace
    for en in entities_to_remove.keys():
        if entities_to_remove[en] == 'NA':
            # entity to delete, remove row
            sqlquery = f"DELETE FROM {table_name} WHERE entity_id='{en}'"
            cur.execute(sqlquery)
        else:
    	    # replace as needed
            # entity to be used as replacement
            sqlquery = f"SELECT entity_type_id FROM {table_name} WHERE entity_id='{entities_to_remove[en]}'"
            answer = cur.execute(sqlquery)
            try:
                result = answer.fetchall()[0]
                entity_type_id_ref = str(result[0])
            except:
                print(f'Invalid Id {entities_to_remove[en]}')
                break
            # entity to replace
            sqlquery = f"SELECT entity_type_id FROM {table_name} WHERE entity_id='{en}'"
            answer = cur.execute(sqlquery)
            try:
                result = answer.fetchall()[0]
                entity_type_id = str(result[0])
            except:
                print(f'Invalid Id {en}')
                break

            # check if the entities pair has the same type_id
            # since they are supposed to represent the same entity, they should be consistent
            if entity_type_id != entity_type_id_ref:
                print(f'entity_type_id for {en} and {entities_to_remove[en]} in entity_mentions table are different')
                sqlquery = f''' UPDATE {table_name}
                                   SET entity_type_id="{entity_type_id_ref}"
                                   WHERE entity_id="{en}"'''
                cur.execute(sqlquery)
            # update row
            sqlquery = f''' UPDATE {table_name}
                                SET entity_id="{entities_to_remove[en]}"
                                WHERE entity_id="{en}"'''
            cur.execute(sqlquery)

# remove from entity relations table
def remove_from_entity_relations(table_name, cur, entities_to_remove, entity_types):
    """
         remove or replace entities from entity_relations table
         args:
             table_name: str, name of table to edit
             cur: cursor pointer to the KB database
             entities_to_remove: list of entity IDs to remove/replace

         returns: nothing, all operations are done on the db connection
    """
    for en in entities_to_remove.keys():
        if entities_to_remove[en] == 'NA':
            # entity to delete, remove row
            sqlquery = f"DELETE FROM {table_name} WHERE entity_parent_id='{en}' OR entity_child_id='{en}'"
            cur.execute(sqlquery)
        else:
            # replace as needed

            # entity to be used as replacement
            sqlquery = f"SELECT entity_parent_type_id FROM {table_name} WHERE entity_parent_id='{entities_to_remove[en]}'"
            answer = cur.execute(sqlquery)
            try:
                result = answer.fetchall()[0]
                entity_parent_type_id_ref = str(result[0])
            except:
                print(f'Invalid parent Id {entities_to_remove[en]}')
                break

            sqlquery = f"SELECT entity_child_type_id FROM {table_name} WHERE entity_child_id='{entities_to_remove[en]}'"
            answer = cur.execute(sqlquery)
            try:
                result = answer.fetchall()[0]
                entity_child_type_id_ref = str(result[0])
            except:
                print(f'Invalid child Id {entities_to_remove[en]}')
                break

            # entity to be replaced
            sqlquery = f"SELECT entity_parent_type_id FROM {table_name} WHERE entity_parent_id='{en}'"
            answer = cur.execute(sqlquery)
            try:
                result = answer.fetchall()[0]
                entity_parent_type_id = str(result[0])
            except:
                print(f'Invalid parent Id {en}')
                break

            sqlquery = f"SELECT entity_child_type_id FROM {table_name} WHERE entity_child_id='{en}'"
            answer = cur.execute(sqlquery)
            try:
                result = answer.fetchall()[0]
                entity_child_type_id = str(result[0])
            except:
                print(f'Invalid child Id {en}')
                break

            # check if the entities pair has the same type_id
            # since they are supposed to represent the same entity, they should be consistent
            if entity_parent_type_id != entity_parent_type_id_ref:
                print(f'entity_parent_type_id for {en} and {entities_to_remove[en]} in entity_relations table are different')
                sqlquery = f''' UPDATE {table_name}
                                   SET entity_parent_type_id="{entity_parent_type_id_ref}"
                                   WHERE entity_parent_id="{en}"'''
                cur.execute(sqlquery)

            if entity_child_type_id != entity_child_type_id_ref:
                print(f'entity_child_type_id for {en} and {entities_to_remove[en]} in entity_relations table are different')
                sqlquery = f''' UPDATE {table_name}
                                   SET entity_child_type_id="{entity_child_type_id_ref}"
                                   WHERE entity_child_id="{en}"'''
                cur.execute(sqlquery)

            # update row
            sqlquery = f''' UPDATE {table_name}
                               SET entity_parent_id="{entities_to_remove[en]}"
                               WHERE entity_parent_id="{en}"'''
            cur.execute(sqlquery)
            sqlquery = f''' UPDATE {table_name}
                               SET entity_child_id="{entities_to_remove[en]}"
                               WHERE entity_child_id="{en}"'''
            cur.execute(sqlquery)

            # remove duplicates if they were created as a result of replacement
            sqlquery = f"DELETE FROM {table_name} WHERE entity_parent_id==entity_child_id"
            cur.execute(sqlquery)



# remove from entity versions table
def remove_from_entity_versions(table_name, cur, entities_to_remove):
    """
        remove or replace entities from entity_versions table
        args:
            table_name: str, name of table to edit
            cur: cursor pointer to the KB database
            entities_to_remove: list of entity IDs to remove/replace

        returns: nothing, all operations are done on the db connection
    """
    for en in entities_to_remove.keys():
        if entities_to_remove[en] == 'NA':
            # entity to delete, remove row
            sqlquery = f"DELETE FROM {table_name} WHERE entity_id='{en}'"
            cur.execute(sqlquery)
        else:
            # entity to replace
            sqlquery = f"SELECT 1 FROM {table_name} WHERE entity_id='{entities_to_remove[en]}'"
            answer = cur.execute(sqlquery)
            try:
                result = answer.fetchall()[0]
                sqlquery = f"DELETE FROM {table_name} WHERE entity_id='{en}'"
                cur.execute(sqlquery)
            except:
                sqlquery = f''' UPDATE {table_name}
                                   SET entity_id="{entities_to_remove[en]}"
                                   WHERE entity_id="{en}"'''
                cur.execute(sqlquery)

# convert entity names to entity ids
def fetch_ids(data, cur):
    """
        Convert entity names to entity IDs
        args:
            data: list of entity names (or entity names pairs)
            cur: cursor pointer to the KB database

        returns: entities_to_remove - dict with entity IDs to remove as keys() and replacement IDs or 'NA' as values()
    """

    entities_to_remove = {}

    # fetch entity names and IDs from the entities table
    sqlquery = f"SELECT id,entity_name FROM 'entities'"
    answer = cur.execute(sqlquery)
    entity_names = []
    entity_ids = []
    for x in answer.fetchall():
        entity_names.append(str(x[1]))
        entity_ids.append(str(x[0]))

    # loop over list of entities to delete/replace and look for them in the existing entities table
    for d in data:
        # entity to delete
        if len(d) == 1:
            if d[0] in entity_names:
                ind = entity_names.index(d[0])
                entities_to_remove[entity_ids[ind]] = 'NA'
            else:
                if d[0].isnumeric() and d[0] in entity_ids:
                    entities_to_remove[d[0]] = 'NA'
                else:
                    print(f'Entity {d[0]} not found in KB. Will be skipped')
                    continue
        else:
            # entity to replace
            if d[0] in entity_names and d[1] in entity_names:
                ind0 = entity_names.index(d[0])
                ind1 = entity_names.index(d[1])
                entities_to_remove[entity_ids[ind0]] = entity_ids[ind1]
            else:
                if d[0].isnumeric() and d[0] in entity_ids and d[1].isnumeric() and d[1] in entity_ids:
                    entities_to_remove[d[0]] = d[1]
                else:
                    print(f'Entity {d[0]} or {d[1]} not found in KB. Will be skipped')
                    continue

    return entities_to_remove


# get a dict of enitity_type for each entity
def get_entity_types(cur):
    """
        List entity type for each entity
        args:
            cur: cursor pointer to the KB database

        returns: entity_types - dict with entity IDs as keys() and entity types as values()
    """
    entity_types = {}

    sqlquery = f"SELECT id,entity_type_id FROM 'entities'"
    answer = cur.execute(sqlquery)

    for x in answer.fetchall():
        entity_types[str(x[0])] = str(x[1])

    return entity_types


# main delete/replace entities function
def delete_from_kg(del_file, cur, table_names):
    """
        Remove/Replace entities from the KB
        args:
            del_file: string with the path of the file containing the list of entities to delete/replace
            cur: cursor pointer to the KB database
            table_names: list of table names in the KB

        returns: nothing, all operations are done on the db connection
    """
    # read entries to delete/replace from the del_file
    with open(del_file, newline='') as f:
        reader = csv.reader(f)
        data = list(reader)

    # separate data to remove by table
    data_tables = {}
    for t in table_names:
        data_tables[t] = []

    for d in data:
        if d[0] not in data_tables:
            print(f'Error unrecognized table name: {d[0]}. Entry {d} will be skipped')
            continue

        data_tables[d[0]].append(d[1:])

    # remove mentions
    if len(data_tables['entity_mentions']) > 0:
        remove_lines_from_entity_mentions('entity_mentions', cur, data_tables['entity_mentions'])

    # remove entities
    if len(data_tables['entities']) > 0:
        # convert entity names to a list of entity ids
        entities_to_remove = fetch_ids(data_tables['entities'], cur)

        # loop over tables and remove/replace entities
        for table_name in table_names:
            if table_name == 'entities':
                remove_from_entities('entities', cur, entities_to_remove)

            if table_name == 'docker_baseos_images' or table_name == 'openshift_baseos_images':
                remove_from_baseos_images(table_name, cur, entities_to_remove)

            if table_name == 'docker_images' or table_name == 'openshift_images' or table_name == 'operator_images':
                remove_from_images(table_name, cur, entities_to_remove)

            entity_types = get_entity_types(cur)
            if table_name == 'entity_mentions':
                remove_from_entity_mentions(table_name, cur, entities_to_remove, entity_types)

            if table_name == 'entity_relations':
                remove_from_entity_relations(table_name, cur, entities_to_remove, entity_types)

            if table_name == 'entity_versions':
                remove_from_entity_versions(table_name, cur, entities_to_remove)


# input argument parser
def parser():
    parser = argparse.ArgumentParser(description="modify KB by adding or deleting entities")
    parser.add_argument("-m", dest="mode", type=str, help="mode: interactive or batch", required=True)
    parser.add_argument("-d", dest="db_file", type=str, help="database file (.db) path", required=True)
    parser.add_argument("-b", dest="batch_file", type=str, default="", help="batch file (.txt) path")
    parser.add_argument("-r", dest="del_file", type=str, default="",
                        help="entities to delete/replace list file (.csv) path")
    return parser.parse_args()


def main():
    # parse inputs
    args = parser()

    mode = args.mode
    batch_filename = args.batch_file
    db_file = args.db_file
    del_file = args.del_file

    # check inputs
    if mode != "batch" and mode != "interactive":
        print("mode -mode should be batch or interactive")
        sys.exit()
    if mode == "batch":
        if not exists(batch_filename):
            print("batch_file -", batch_filename, "- does not exist")
            sys.exit()
    if not exists(db_file):
        print("db_file -", db_file, "- does not exist")
        sys.exit()
    if del_file != "" and not exists(del_file):
        print("del_file -", db_file, "- does not exist")
        sys.exit()

    # initiate connection to db file
    conn = sqlite3.connect(db_file)
    cur = conn.cursor()

    # get table names
    tables = cur.execute("SELECT name FROM sqlite_master WHERE type='table';")
    table_names = []
    for table_name in tables:
        if table_name[0] != "sqlite_sequence":
            table_names.append(table_name[0])

    # execute changes to KB
    if del_file != "":
        delete_from_kg(del_file, cur, table_names)
    else:
        insert_to_kg(mode, batch_filename, cur)

    # commit changes and close connection
    conn.commit()
    conn.close()


if __name__ == "__main__":
    main()
