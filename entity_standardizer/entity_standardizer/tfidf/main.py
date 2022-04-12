import os
import json
import logging

class TFIDF():
    def __init__(self, task_name):
        super().__init__()
        import configparser

        self.task_name = task_name                           
        self.config    = configparser.ConfigParser()
        common = os.path.join("config", "common.ini")
        kg     = os.path.join("config", "kg.ini")
        tfidf  = os.path.join("config", self.task_name, "tfidf.ini")
        self.config.read([common, kg, tfidf])
        self.config["task"] = {}
        self.config["task"]["name"] = self.task_name

    def infer(self, infer_data):
        from .infer import predict
        predict(self.config, infer_data)        
        return infer_data


