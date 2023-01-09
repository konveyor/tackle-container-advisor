################################################################################
# Copyright IBM Corporation 2021, 2022
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
################################################################################

import os
import json
from collections import OrderedDict
import logging
from service.utils import Utils
import ast
import numpy as np

import configparser

config = configparser.ConfigParser()
common = os.path.join("config", "common.ini")
kg = os.path.join("config", "kg.ini")
config.read([common, kg])


class Clustering():
    """
    This class for Clustering
    """

    def __init__(self):
        """
            Init method for Clustering Class
            Setting up the logging level as info and opens logfile in write mode to capture the logs in text file
         """

        logging.basicConfig(level=logging.INFO)

        # read entities
        entities_filepath = os.path.join(config['general']['kg_dir'], config['tca']['entities'])
        if os.path.exists(entities_filepath):
            with open(entities_filepath, 'r') as f:
                entities_json = json.load(f)
                self.entity_names = np.empty(len(entities_json['data']), dtype='object')
                for i, en in enumerate(entities_json['data']):
                    self.entity_names[i] = entities_json['data'][en]['entity_name']
        else:
            self.entities = {}
            logging.error(f'entities[{entities_filepath}] is empty or not exists')


    def output_to_ui_clustering(self, appL):
        """
        output_to_ui clustering methods takes the final assessed data as input and formats it & keeps
         only required fields and returns it as output assessment response

        """

        # initialize tech stack
        tech_stack = np.zeros((len(appL), self.entity_names.shape[0]), dtype='bool')
        appL_array = np.array(appL)

        # find unique clusters
        fields = ['OS', 'Lang', 'App Server', 'Dependent Apps', 'Runtime', 'Libs']
        for i, app in enumerate(appL):
            for k in fields:

                if k in app.keys():
                    if type(app[k]) is str:
                        txt = ast.literal_eval(app[k])
                    else:
                        txt = app[k]
                    for t in txt.keys():
                        # entity = list(txt[t].keys())[0]
                        entity = txt[t]['standard_name']

                        # keep only root of hierarchical entity
                        if entity.find('|') > 0:
                            entity = f"{entity.split('|')[0]}|*"

                        tech_stack[i][self.entity_names == entity] = 1

        # find unique clusters
        clusters, index, counts = np.unique(tech_stack, return_inverse=True, return_counts=True, axis=0)

        # sort clusters by number of apps
        order = np.argsort(counts)[::-1]

        clusters = clusters[order]
        counts = counts[order]

        unique_clusters = []
        for i in range(clusters.shape[0]):
            cl = { "id": i, "name": f'unique_tech_stack_{i}',  "type": 'unique', "tech_stack": list(self.entity_names[clusters[i] == 1]),\
                   "num_elements": int(counts[i]), "apps": list(appL_array[index == order[i]]) }

            unique_clusters.append(cl)


        return unique_clusters
