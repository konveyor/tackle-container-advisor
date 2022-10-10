
#selenium driver
#import chromedriver_binary
from time import sleep
from selenium.webdriver.common.by import By
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support.ui import Select
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from driver import  get_driver

class SeleniumDriver():

    def __init__(self, remote_ip_addr) -> None:

        self.remote_ip_addr = remote_ip_addr
        self.driver = get_driver(self.remote_ip_addr)

    def open_driver(self, url:str):
        """
        Args:
           url: str
        Returns:
            open the selenium driver
        """
        self.driver.get(url)

    def close_driver(self):
        """
        Args:
        
        Returns:
            close the Selenium driver
        """ 
        self.driver.quit()

    def get_containers(self, url, catalogue_name ="DockerHub" ,default_container = "mysql"):
        self.driver.switch_to("tab") 

        
        """
        Args:
            url: str
            new_driver: Selenium Class instance
            all: boolean
            default_container: str

        Returns:

            containers: list 
            
        """
        self.open_driver(url)
        search_url = self.all_containers_url(catalogue_name , default_container) 
        return search_url
        


    def get_all_xpath(self):
        """
        Args:
         
        Returns:
            xpath_element: 
        """
        return self.driver.find_elements(By.XPATH ,".//*" )

    def all_containers_url(self, catalogue_name,  entity:str) -> str:

        """
        Args:
            entity: name entity
        Returns:
            str: search results url                            

        """
        search_url = ""
        if catalogue_name == "DockerHub": 
            search_element = self.driver.find_element(By.CSS_SELECTOR ,".autocompleteInput")
            search_element.send_keys(entity)
            search_element.send_keys(Keys.ENTER)
            search_url = self.driver.current_url

        elif catalogue_name == "OpenShift":
            search_element = self.driver.find_element(By.CSS_SELECTOR ,"#searchBar")
            search_element.send_keys(entity)
            search_element.send_keys(Keys.ENTER) 
            search_url = self.driver.current_url
        
        else: 
            search_element = self.driver.find_element(By.CSS_SELECTOR ,"#search-input-main")
            search_element.send_keys(entity)
            search_element.send_keys(Keys.ENTER) 
            search_url = self.driver.current_url
            print(search_url)

        return search_url

    def search_body(self, empty_body_element_class_name = "pf-c-empty-state__body"):

        element_body = ''
      
        try:
            element_body = WebDriverWait(self.driver,8).until(EC.presence_of_element_located((By.CLASS_NAME, empty_body_element_class_name ))).text
        
        finally:
            return element_body


    def find_element_by_css_selector(self, selector:str):

        elements = None
        try: 
            elements = self.driver.find_element(By.CSS_SELECTOR , selector)
        except Exception as e: 
            print(e)
        return  elements


    def find_element_by_class_name(self):
        """
        Args:
    
        Returns:
            elements containing search results
        """

        #no  result found class
        no_result_class = "MuiTypography-root MuiTypography-h3 css-dubhfy"

        #result found class
        result_wrapper_class = "styles__resultsWrapper___38JCx"
        
        elements = None

        try:
            if "No results" in self.driver.find_element(By.CLASS_NAME, no_result_class).text: 
                elements = None
        except Exception as e:
            print("Relevant images found.")

        try:
            elements = WebDriverWait(self.driver, 5).until(
        EC.presence_of_element_located((By.CLASS_NAME, result_wrapper_class))
    )   

        except Exception as e:
            print("There are no results for this search in Docker Hub.  ")
        
        return  elements
      

    