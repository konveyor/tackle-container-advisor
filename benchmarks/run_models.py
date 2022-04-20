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

import os
import json
import time
import copy
import configparser
import argparse

def parser():
    parser = argparse.ArgumentParser(description="Train and evaluate TCA entity standardization models")
    parser.add_argument("-model_type", type=str, default="tf_idf", help="tf_idf (default) | gnn | wiki_data_api | all")
    parser.add_argument("-mode", type=str, default="deploy", help="deploy (default) | tca | wikidata")
    return parser.parse_args()

def print_gh_markdown(table_data):
    """
    Creates a table of results in github markdown format
    :param table_data
    :type  table_data: <class 'dict'>

    :returns: Return cleaned string with non-ascii characters removed/replaced
    """
    print(f"<p><table>")
    print(f"<thead>")
    print(f"<tr><th>Method</th><th>top-1</th><th>top-3</th><th>top-5</th><th>top-10</th><th>top-inf(count)</th><th>False positive rate</th><th>Runtime (on cpu)</th></tr>")
    print(f"</thead>")
    print(f"<tbody>")
    for model, data in table_data.items():
        cpu_time = data["time"]
        top_k    = data["topk"]
        kns      = data["kns"]
        fpr      = data["fpr"]
        unks     = data["unks"]
        print(f"<tr><td>{model}</td><td>{top_k[0]/max(1,kns):.2f}</td><td>{top_k[1]/max(1,kns):.2f}</td><td>{top_k[2]/max(1,kns):.2f}</td><td>{top_k[3]/max(1,kns):.2f}</td><td>{top_k[4]/max(1,kns):.2f} ({top_k[4]}/{kns})</td><td>{fpr/max(1,unks):.2f}({fpr}/{unks})</td><td>{cpu_time:.2f}s</td></tr>")
    print(f"</tbody>")
    print(f"</table></p>")

def topk(json_data):
    """
    Computes the top-1,3,5,10,inf for predictions in json_data
    :param json_data
    :type  json_data: <class 'dict'>

    :returns: Return cleaned string with non-ascii characters removed/replaced
    """
    label  = json_data.get("label", "label")
    top_k  = (0, 0, 0, 0, 0) # Top-1, top-3, top-5, top-10, top-inf
    unks   = 0
    fpr    = 0
    kns    = 0
    for idx in json_data["data"]:
        correct = json_data["data"][idx].get(label, None)
        predictions = json_data["data"][idx].get("predictions", [])
        if correct is None:
            unks += 1
        else:
            kns += 1
        if predictions:
            if correct is None:
                fpr += 1
                continue
            for i, pred in enumerate(predictions):
                if (pred[0] == correct):
                    top_k = (top_k[0],top_k[1],top_k[2],top_k[3],top_k[4]+1)
                    if i <= 0:
                        top_k = (top_k[0]+1,top_k[1],top_k[2],top_k[3],top_k[4]) 
                    if i <= 2:
                        top_k = (top_k[0],top_k[1]+1,top_k[2],top_k[3],top_k[4])
                    if i <= 4:
                        top_k = (top_k[0],top_k[1],top_k[2]+1,top_k[3],top_k[4])
                    if i <= 9:
                        top_k = (top_k[0],top_k[1],top_k[2],top_k[3]+1,top_k[4])
                    break
            
    return {"topk": top_k, "kns": kns, "fpr": fpr, "unks": unks}

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="[%(asctime)s] %(name)s:%(levelname)s in %(filename)s:%(lineno)s - %(message)s", filemode='w')

    args = parser()

    model_type = args.model_type
    mode = args.mode

    table_data       = {}

    config    = configparser.ConfigParser()
    common = os.path.join("config", "common.ini")
    config.read(common)

    try:
        data_dir = config['general']['data_dir']
    except KeyError as k:
        print(f'{k} is not a key in your common.ini file.')
        exit()
    
    task = {'tca': 'tca', 'wikidata':'tca', 'deploy': 'tca'}
    tca_infer_file_name = os.path.join(data_dir, task[mode], "infer.json")
    with open(tca_infer_file_name, 'r', encoding='utf-8') as tca_infer_file:
        tca_infer_data = json.load(tca_infer_file)

    wikidata_infer_file_name = os.path.join(data_dir, "wikidata", "infer.json")
    with open(wikidata_infer_file_name, 'r', encoding='utf-8') as wikidata_infer_file:
        wikidata_infer_data = json.load(wikidata_infer_file)

    if model_type == "tf_idf" or model_type == "all":
        print("----------- TFIDF -------------")
        from entity_standardizer.tfidf import TFIDF
        tfidf            = TFIDF(mode)
        tfidf_start      = time.time()
        tfidf_infer      = copy.deepcopy(tca_infer_data)
        tfidf_infer      = tfidf.infer(tfidf_infer)
        tfidf_end        = time.time()
        tfidf_time       = (tfidf_end-tfidf_start)
        tfidf_topk       = topk(tfidf_infer)
        table_data["tfidf"]= {}
        table_data["tfidf"]["topk"] = tfidf_topk["topk"]
        table_data["tfidf"]["kns"]  = tfidf_topk["kns"]
        table_data["tfidf"]["fpr"]  = tfidf_topk["fpr"]
        table_data["tfidf"]["unks"] = tfidf_topk["unks"]
        table_data["tfidf"]["time"] = tfidf_time
    
    '''
    if model_type == "wiki_data_api" or model_type == "all":
        print("----------- WIKIDATA API -------------")
        from entity_standardizer.wdapi import WDAPI
        wdapi            = WDAPI(mode)   # wikidata
        wdapi_start      = time.time()
        wdapi_infer      = copy.deepcopy(wikidata_infer_data)
        wdapi_infer      = wdapi.infer(wdapi_infer)
        wdapi_end        = time.time()
        wdapi_time       = (wdapi_end-wdapi_start)
        wdapi_topk       = topk(wdapi_infer)
        table_data["wdapi"]= {}
        table_data["wdapi"]["topk"] = wdapi_topk["topk"]
        table_data["wdapi"]["kns"]  = wdapi_topk["kns"]
        table_data["wdapi"]["fpr"]  = wdapi_topk["fpr"]
        table_data["wdapi"]["unks"] = wdapi_topk["unks"]
        table_data["wdapi"]["time"] = wdapi_time
    
    print("----------- ENTITY LINKING API -------------")
    from entity_standardizer.entlnk import ENTLNK 
    entlnk           = ENTLNK("wikidata")
    entlnk_start     = time.time()
    entlnk_infer     = copy.deepcopy(wikidata_infer_data)
    entlnk_infer     = entlnk.infer(entlnk_infer)
    entlnk_end       = time.time()
    entlnk_time      = (entlnk_end-entlnk_start)
    entlnk_topk      = topk(entlnk_infer)
    table_data["entlnk"]= {}
    table_data["entlnk"]["topk"] = entlnk_topk["topk"]
    table_data["entlnk"]["kns"]  = entlnk_topk["kns"]
    table_data["entlnk"]["fpr"]  = entlnk_topk["fpr"]
    table_data["entlnk"]["unks"] = entlnk_topk["unks"]
    table_data["entlnk"]["time"] = entlnk_time
    table_data["entlnk"]["total"]= len(entlnk_infer_data["data"])    
    '''
    print_gh_markdown(table_data)