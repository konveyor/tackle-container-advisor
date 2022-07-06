import unittest

from src.search_images import DockerHubSearch ,Operators , Quay


class test_search_operators(unittest.TestCase):

    def setUp(self) -> None:

        self.operator = Operators()
        self.quay = Quay()
        self.docker = DockerHubSearch()


    def tearDown(self) -> None:

        self.operator = None
        self.quay = None
        self.docker = None

    
    def test_search_operator(self):

        entity = "DB2"

        self.assertIsInstance(entity , str)



    def test_search_dockerhub_images(self):

        entity =  "DB2"
        self.assertIsInstance(entity , str)

    
    def test_search_images(self):
        entity = "DB2"
        self.assertIsInstance(entity , str)




    



      




    



        

   






