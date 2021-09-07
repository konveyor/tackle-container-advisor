# *****************************************************************
# Copyright IBM Corporation 2021
# Licensed under the Eclipse Public License 2.0, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# *****************************************************************

import sqlite3
from sqlite3 import Error

def create_db_connection(db_file):

    """
    Create a connection  to Mysqlite3 databade

    :param db_file: Path to mysql file
    :type db_file:  .db file 
    
    
    :returns: Connection to mysql db
    :rtype:   <class 'sqlite3.Connection'>

    """

    connection = None
    try:
        connection = sqlite3.connect(db_file)

    except Error as e:
        logging.error(f'{e} cannot create connection to db. Check that the {db_file} is the correct file ')
        print(e)
        exit()

    return connection
