import unittest

from kg_utils.search_utils  import  dockerhub , quay , operator
from kg_utils.search_utils.save_to_csv import csv_columns
from kg_utils.search_utils.load_entities import filter_entity 


class test_search(unittest.TestCase):

    def setUp(self) -> None:

        self.operator = operator.Operators()
        self.quay     = quay.Quay()
        self.docker   = dockerhub.DockerHubSearch()


    def tearDown(self) -> None:

        self.operator = None
        self.quay     = None
        self.docker   = None


    def test_search_operator(self):

        entity = "DB2"
        self.assertIsInstance(entity , str)


    def test_search_dockerhub_images(self):

        entity =  "DB2"
        self.assertIsInstance(entity , str)

    def test_search_images(self):
        entity = "DB2"
        self.assertIsInstance(entity , str)


    def test_csv_columns(self):

        table_name = "operator_images"
        cols = csv_columns(table_name)
        expected = {'operator_images': '', 'container_name': '', 'OS': None, 'lang': None, 'lib': None, 'app': None, 'app_server': None, 'plugin': None, 'runlib': None, 'runtime': None, 'Operator_Correspondent_Image_Url': [], 'Operator_Repository': ''}
        self.assertEqual(cols , expected)


    def test_filter_entity(self):
        entity =   "MS SQL Server|SQL Server Analysis Services (SSAS)"
        expected = "SQL Server Analysis Services"
        fil_entity = filter_entity(entity)
        self.assertEqual(fil_entity , expected)



        

        


    
  