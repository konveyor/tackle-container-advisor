
import sqlite3

import argparse

# Connect to the 

db_file = "/app/db/1.0.4.db"


#View all current tables
def current_table_names(conn):
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = []

    for col in cursor.fetchall():
        tables.append(col[0])

    return tables

    print("Tables: {}".format(tables))



def create_table(conn, table_name:str, columns:str): 
    """
    Create a custom table

    Args:
        conn (_type_): _description_
    """
    cur = conn.cursor()

    table = "CREATE TABLE {}{}".format(table_name, columns)

    print(table)
    # table2 = "CREATE TABLE {}(Id INTEGER PRIMARY KEY, label TEXT NOT NULL, label_url TEXT, \
    #         container_name TEXT, container_image_url TEXT , repository_url TEXT )".format(table_name)
    res = cur.execute(table)


def table_cmd():

    """

    _summary_

    """

    parser = argparse.ArgumentParser(
                    prog = 'add_tables.py',
                    description = 'Add a new table to the database')
    parser.add_argument('-t', '--table_name')      #
    parser.add_argument('-n', '--num_columns') 

    return parser.parse_args() 

   
if "__name__==__main__":

    # initiate connection to db file
    conn = sqlite3.connect(db_file)
   
    entries = table_cmd()
    print(entries.table_name)

    columns = '('
    print("For common mysql datatypes, refer to the doc: https://dev.mysql.com/doc/refman/8.0/en/data-types.html")

    
    if entries.table_name in current_table_names(conn):
        print("Cannot have duplicated Table name")
    # for num in list(range(int(entries.num_columns))):
    #     col_name = input("column {} name: ".format(num))
    #     col_data_type = input("{} data type : ".format(col_name))
        
    #     if num + 1 < int(entries.num_columns):
    #         columns += col_name + ' ' + col_data_type + ', '
    #     else : columns += col_name + ' ' +col_data_type
    
    # columns += ')'
    #create_table(conn,entries.table_name,columns)

    
    #explore_db(conn)
    #conn.execute("DROP TABLE {}".format(entries.table_name))









