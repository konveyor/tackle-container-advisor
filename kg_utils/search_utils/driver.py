
"""
Module for web scraping
"""
from selenium import webdriver


def get_driver(remote_ip="localhost"):

    print("Waiting for selenium webdriver to load a session...")
    driver = webdriver.Remote(desired_capabilities=webdriver.DesiredCapabilities.FIREFOX, command_executor="http://{}:4444".format(remote_ip))
    
    return driver

    

