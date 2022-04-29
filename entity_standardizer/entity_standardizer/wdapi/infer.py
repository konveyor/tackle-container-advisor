import os
import requests
import multiprocessing
import urllib.parse as uparse
import logging
from time import time, sleep
from http import HTTPStatus
from backoff_utils import strategies, apply_backoff



class Wikidata():
    def __init__(self, url):
        super().__init__()
        self.url = url

    def get_data_combinations(self, data):
        """
        Generate phrases from words in data
        
        :param data: A list of mention words e.g. ['Apache', 'Tomcat', 'HTTP', 'Server']
        :type data: list 
        
        # :returns: Returns a list of truncated phrases e.g ['Tomcat HTTP Server', 'HTTP Server', ... 'Apache Tomcat HTTP', 'Apache Tomcat', ...]
        :returns: Returns a list of truncated phrases e.g ['Apache Tomcat HTTP', 'Apache Tomcat', ... , 'Tomcat HTTP Server', 'HTTP Server', ...]
        
        """
        combinations = []
        if not data:
            return combinations
        combinations.append(' '.join(data))
        for i in range(1,len(data),1):
            combinations.append(' '.join(data[:-i]))
        for i in range(1,len(data),1):
            combinations.append(' '.join(data[i:]))
        return combinations

    @apply_backoff(strategy = strategies.Fixed(minimum=3.0), max_tries = 5, max_delay = 15.0)
    def invoke_wikidata_api(self, data):
        """
        Invokes wikidata autocomplete on data
        
        :param data: String to query Wikidata API for qids
        :type data: string 
        
        :returns: Returns a list of qids
        """
        qids    = []
        headers = {'Content-type': 'application/json'}    
        # try:
        R = requests.get(self.url+uparse.quote(data), headers=headers)
        if R.status_code == HTTPStatus.TOO_MANY_REQUESTS:
            raise Exception
        elif R.status_code != HTTPStatus.OK:
            print(f"Data = {data}, Response code = {R.status_code}")
        else:
            candidates = R.json()            
            if candidates.get('success', 0) != 1:
                logging.error(f"Failed wikidata query -> {candidates}")
            else:
                for candidate in candidates['search']:
                    qids.append((candidate['id'], 1.0))

        return qids


    def get_wikidata_qids(self, data):
        """
        Gets wikidata qids for data
        
        :param data: Mention for which to get Wikidata qids
        :type data: string 
    
        :returns: Returns a dictionary of data to predicted qids
        """
        wd_qids = {}
        
        # Get qids for exact phrase
        qids  = []
        qids += self.invoke_wikidata_api(data)    

        fragments    = data.split()
        # Get valid fragments
        data_to_qids = {}
        for i, frag in enumerate(fragments): 
            if frag is None or frag == "" or frag == " ":
                logging.warning("Contains empty fragments = ", fragments)
            frqids = self.invoke_wikidata_api(frag)            
            if frqids:
                data_to_qids[frag] = frqids           
                
        # Get qids for combinations of all fragments
        combinations = self.get_data_combinations(fragments)
        for i, comb in enumerate(combinations):
            if comb is None or comb == "" or comb == " ":
                print("Combinations = ", combinations)
            qids += self.invoke_wikidata_api(comb)        

        # Get qids for combinations of sorted valid fragments
        sorted_qids = {k: v for k, v in sorted(data_to_qids.items(), key=lambda item: len(item[1]))}
        valid_data   = [d for d in sorted_qids]
        combinations = self.get_data_combinations(valid_data)
        for i, comb in enumerate(combinations):
            if comb is None or comb == "" or comb == " ":
                logging.warn("Contains empty combinations= ", valid_data)
            qids += self.invoke_wikidata_api(comb)

        if not qids:           
            logging.info(f"No qids for {data}")                    

        wd_qids[data] = qids
        return wd_qids

def predict(config, json_data):
    """
    Runs wikidata autocomplete on test set

    :param json_data: Dictionary containing mention data and standardized entity data (if available)
    :type json_data: <class 'dict'>

    :returns: Returns the same dictionary with an additional field "predictions"
    """

    data_to_idx      = {}    
    for idx in json_data["data"]:
        mention = json_data["data"][idx]["mention"]
        data_to_idx[mention] = idx        
        
    url              = config["infer"]["wd_url_old"]
    wd_obj           = Wikidata(url)
    pool             = multiprocessing.Pool(min(int(config["infer"]["max_workers"]), 2*os.cpu_count()))
    wd_results       = pool.map(wd_obj.get_wikidata_qids, data_to_idx.keys())
    pool.close()

    wd_qids = {k:v for item in wd_results for k,v in item.items()}
    for mention,qids in wd_qids.items():
        idx = data_to_idx[mention]
        json_data["data"][idx]["predictions"] = qids

    return json_data

