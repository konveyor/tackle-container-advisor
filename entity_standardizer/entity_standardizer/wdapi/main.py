import os
import json
import logging

class WDAPI():
    def __init__(self, task_name):
        super().__init__()
        import configparser

        self.task_name = task_name                           
        self.config    = configparser.ConfigParser()
        common         = os.path.join("config", "common.ini")
        wdapi          = os.path.join("config", self.task_name, "wdapi.ini")
        self.config.read([common, wdapi])
        self.config["task"] = {}
        self.config["task"]["name"] = self.task_name
        logging.basicConfig(level=logging.INFO, format="[%(levelname)s:%(filename)s:%(lineno)s - %(funcName)5s()] %(message)s", filemode='w')

        if self.config['infer']['max_workers'] == '0':
            logging.info(f"Max. workers (= {self.config['infer']['max_workers']}) should be > 0.")
            self.config['infer']['max_workers']  = "8"
            logging.info(f"Resetting to {self.config['graphs']['num_workers']}")
        
    def infer(self, infer_data):
        from .infer import predict
        predict(self.config, infer_data)        
        return infer_data
    
