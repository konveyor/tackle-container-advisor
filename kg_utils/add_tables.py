
import sqlite3
import argparse
import configparser
import os
import logging

#config file
config = configparser.ConfigParser()
config_data = os.path.join("config/kg.ini")
config.read([config_data])
db_file = config["database"]["database_path"]    


def table_names(conn) ->list:
    """
    View table names.
    
    Args:
        conn (_type_): Connection to the database.

    Returns:
        list: A list containing all table names.
    """
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = []

    for col in cursor.fetchall():
        tables.append(col[0])
    return tables



def create_table(conn, table_name:str, columns:str):

    """
    Create a custom table.

    Args:
        conn (_type_): Connection to the database.
    """
    cur = conn.cursor()

    table = "CREATE TABLE {}{}".format(table_name, columns)
    cur.execute(table)
    logging.info("{} added to the database!".format(table_name))
    
    
def table_cmd()->object:
    """
    Parses input arguments
    Returns:
        object: A parser
    """

    parser = argparse.ArgumentParser(
                    prog = 'add_tables.py',
                    description = 'Add a new table to the database')
    parser.add_argument('-t', '--table_name')      #
    parser.add_argument('-n', '--num_columns')
    parser.add_argument('-f',  '--num_foreign_keys') 
    return parser.parse_args() 

   
if "__name__==__main__":

    # initiate connection to db file
    conn = sqlite3.connect(db_file)
   
    entries = table_cmd()

    columns = '('
    print("Enter column name followed by  data type along with any additional column constraints(PRIMARY KEY, NOT NULL, AUTOINCREMENT, DEFAULT, DETAILS,  ETC ...)")
    print("For common mysql data types, please refer to the documentation at: https://dev.mysql.com/doc/refman/8.0/en/data-types.html")
    print("============================================================================================================================")
    
    for num in list(range(int(entries.num_columns))):
        col_ = input("column {}: ".format(num))
        if num +1 == int(entries.num_columns) : columns += col_
        else: columns += col_ + ', '
    
    print("\n")
    if entries.num_foreign_keys == 0: columns += ')'
    
    else:
        print("Enter FOREIGN KEYS.")
        print("Format: FOREIGN KEY (column_name) REFERENCES <table_name> (<corresponding column from table_name>)")
        print("Example: FOREIGN KEY (entity_id) REFERENCES entities (id)")
        print("==============================================================================================")
        for num in list(range(int(entries.num_foreign_keys))):
            f_key = input("FOREIGN KEY {} : ".format(num+1))
            columns +=  ', '  + f_key
    
    columns += ')'
    create_table(conn,entries.table_name,columns)










