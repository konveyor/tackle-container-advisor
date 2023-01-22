
import sqlite3

import argparse

# Connect to the 

db_file = "/app/db/1.0.4.db"


class Table():

    def __init__(self,name:str,num_columns:int , num_foreign_keys:str):
        """_summary_

        Args:
            name (str): table name
            num_columns (int): number of columns 
            num_foreign_keys (str): number of foreign keys

        Returns:
            _type_(None): none
        """
        self.table_name = name
        self.num_columns = num_columns
        self.number_of_foreign_keys = num_foreign_keys

    def  primary_key(self):
        """_summary_
        """
        pass
    def foreign_key(self):
        """
        

        """
        pass
    def default_val(self):
        """_summary_
        """
        pass


    def structure(self):
        """_summary_

        Returns:
            _type_: _description_
        """
        
     
    
    def unique(self):
        """_summary_

        Returns:
            _type_: _description_
        """


        pass
    
    

#View all current tables
def table_names(conn):
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
    

def constraints()

def table_cmd():

    """

    _summary_

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


    if entries.table_name in table_names(conn):
        print("{} is already in the database.".format(entries.table_name))
        Ans = input("Would you like to drop {} table? Y/N".format(entries.table_name))
        if Ans.lower()  == "y": 
            conn.execute("DROP TABLE {}".format(entries.table_name))
        else: exit()

    columns = '('
    print("Enter column name followed by  data type along with any additional column constraints(PRIMARY KEY, FOREIGN KEY, NOT NULL, AUTOINCREMENT, DEFAULT, DETAILS,  ETC ...)")
    print("For common mysql data types, please refer to the documentation at: https://dev.mysql.com/doc/refman/8.0/en/data-types.html")

    
    for num in list(range(int(entries.num_columns))):
        col_ = input("Enter column {} name  , data type , constraints if any.: ".format(num))
        if num +1 == int(entries.num_columns) : columns += col_
        else: columns += col_ + ', '

    if entries.num_foreign_keys == 0: columns += ')'

    else:
        for num in list(range(int(entries.num_foreign_keys))):
            f_key = input("Enter FOREIGN KEY {} : ".format(num+1))
            columns += col_ + ', '


    

    print(columns)

    create_table(conn,entries.table_name,columns)
    print(table_names(conn))










