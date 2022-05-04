# *****************************************************************
# Copyright IBM Corporation 2021
# Licensed under the Eclipse Public License 2.0, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# Reference: https://bip.weizmann.ac.il/course/python/PyMOTW/PyMOTW/docs/multiprocessing/mapreduce.html
# *****************************************************************
import os
import collections
import itertools
import multiprocessing
import json
import configparser


config = configparser.ConfigParser()
common = os.path.join("config", "common.ini")
kg     = os.path.join("config", "kg.ini")
config.read([common, kg])

class SimpleMapReduce(object):
    
    def __init__(self, map_func, reduce_func, num_workers=None):
        """
        Initializes the object with the required inputs such as mapper, reducer and parameters for multiprocessing such as the number of processes and maxtaskperchild.
        The processes refers to the number of CPUs or workers. The maxtaskperchild refers to the number of threads.
        """
        self.map_func = map_func
        self.reduce_func = reduce_func
        self.pool = multiprocessing.Pool(processes=int(config['Performance']['processes']),maxtasksperchild=int(config['Performance']['maxtasksperchild']))
    
    def partition(self, mapped_values):
        """
        Organize mapped values by their key
        """
        partitioned_data = collections.defaultdict(list)
        for key, value in mapped_values:
            partitioned_data[key].append(value)
        return partitioned_data.items()
    
    def __call__(self, inputs, chunksize=int(config['Performance']['chunksize'])):
        """
        Processes the input via the mapper and the reducer
        """
        map_responses = self.pool.map(self.map_func, inputs, chunksize=chunksize)
        #accumulated data
        partitioned_data = self.partition(itertools.chain(*map_responses))
        #finally reduce it
        reduced_values = self.pool.map(self.reduce_func, partitioned_data)
        
        return reduced_values
