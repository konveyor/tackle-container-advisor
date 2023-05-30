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
import time
import copy
import configparser
import argparse
import logging
import numpy as np
from sklearn.metrics import precision_recall_curve
from sklearn.metrics import f1_score
from sklearn.metrics import auc
from matplotlib import pyplot


def parser():
    parser = argparse.ArgumentParser(description="Train and evaluate TCA entity standardization models")
    parser.add_argument("-model_type", type=str, default="siamese", help=" siamese (default) | tf_idf | wiki_data_api | all")
    parser.add_argument("-mode", type=str, default="deploy", help="deploy (default) | benchmark")
    parser.add_argument("-batch_size", type=int, default=0, help="optional, batch size for siamese model. Default is 0, meaning no batching")
    parser.add_argument("-show", action="store_true", help="False (default)")

    return parser.parse_args()


def print_gh_markdown(table_data):
    """
    Creates a table of results in github markdown format
    :param table_data
    :type  table_data: <class 'dict'>

    :returns: Return cleaned string with non-ascii characters removed/replaced
    """
    
    logging.info(f"<p><table>")
    logging.info(f"<thead>")
    logging.info(f"<tr><th>Method</th><th>top-1</th><th>top-3</th><th>top-5</th><th>top-10</th><th>top-inf(count)</th><th>False positive rate</th><th>Runtime (on cpu)</th></tr>")
    logging.info(f"</thead>")
    logging.info(f"<tbody>")
    for model, data in table_data.items():
        cpu_time = data["time"]
        top_k    = data["topk"]
        kns      = data["kns"]
        fpr      = data["fpr"]
        unks     = data["unks"]
        logging.info(f"<tr><td>{model}</td><td>{top_k[0]/max(1,kns):.2f}</td><td>{top_k[1]/max(1,kns):.2f}</td><td>{top_k[2]/max(1,kns):.2f}</td><td>{top_k[3]/max(1,kns):.2f}</td><td>{top_k[4]/max(1,kns):.2f} ({top_k[4]}/{kns})</td><td>{fpr/max(1,unks):.2f}({fpr}/{unks})</td><td>{cpu_time:.2f}s</td></tr>")
    logging.info(f"</tbody>")
    logging.info(f"</table></p>")


def topk(json_data, threshold):
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
        if correct is None or correct == 0:
            unks += 1
        else:
            kns += 1
        if predictions:
            if (correct is None or correct == 0) and predictions[0][1] > threshold:
                fpr += 1
                continue
            for i, pred in enumerate(predictions):
                if (pred[1] > threshold and pred[0] == correct):
                    top_k = (top_k[0],top_k[1],top_k[2],top_k[3],top_k[4]+1)

                    if i <= 0:
                        top_k = (top_k[0] + 1, top_k[1], top_k[2], top_k[3], top_k[4])
                    if i <= 2:
                        top_k = (top_k[0], top_k[1] + 1, top_k[2], top_k[3], top_k[4])
                    if i <= 4:
                        top_k = (top_k[0], top_k[1], top_k[2] + 1, top_k[3], top_k[4])
                    if i <= 9:
                        top_k = (top_k[0], top_k[1], top_k[2], top_k[3] + 1, top_k[4])
                    break

    return {"topk": top_k, "kns": kns, "fpr": fpr, "unks": unks}

def plot(x_data, topk_data, label):
    # plot the curve
    pyplot.plot(x_data, topk_data[0], marker='.', label=label)

def cls_metrics(json_data, label):
    x_data = []
    topk_data = [[] for k in range(3)]
    for thr in np.arange(0.0,1.0,0.05):        
        topk_values = topk(json_data, thr)
        x_data.append(topk_values['fpr']/topk_values['unks'])
        for k in range(3):
            topk_data[k].append(topk_values['topk'][k]/topk_values['kns'])
    plot(x_data, topk_data, label)

def sim_metrics(json_data, label):
    testy    = []
    lr_probs = []
    yhat     = []
    for idx, data in json_data["data"].items():
        testy.append(data["similarity"])
        lr_probs.append(data["sim_score"])
        yhat.append(int(round(data["sim_score"])))

    testy = np.array(testy)
    lr_probs = np.array(lr_probs)
    yhat  = np.array(yhat)

    lr_precision, lr_recall, _ = precision_recall_curve(testy, lr_probs)
    lr_f1, lr_auc = f1_score(testy, yhat), auc(lr_recall, lr_precision)
    # summarize scores
    logging.info('Similarity metrics: f1=%.3f auc=%.3f' % (lr_f1, lr_auc))
    # plot the precision-recall curves
    pyplot.plot(lr_recall, lr_precision, marker='.', label=label)

    return (lr_auc, lr_f1)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="[%(asctime)s] %(name)s:%(levelname)s in %(filename)s:%(lineno)s - %(message)s", filemode='w')

    args = parser()

    model_type = args.model_type
    mode = args.mode
    batch_size = args.batch_size
    show = args.show

    table_data       = {}

    config    = configparser.ConfigParser()

    common = os.path.join("config", "common.ini")
    kg     = os.path.join("config", "kg.ini")
    deploy_configs = os.listdir(os.path.join("config", "deploy"))
    deploys = [os.path.join("config", "deploy", x) for x in deploy_configs]
    config.read([common, kg]+deploys)

    try:
        data_dir = config['general']['data_dir']
        kg_dir   = config['general']['kg_dir']
        threshold= float(config[f"infer_thresholds_{model_type}"]["HIGH_THRESHOLD"])
    except KeyError as k:
        logging.error(f'{k} is not a key in your common.ini file.')
        exit()

    tasks = {'sim':'tca', 'tca': 'tca', 'wikidata':'wikidata', 'deploy': 'deploy'}
    task  = tasks[mode]
    tca_infer_file_name = os.path.join(data_dir, 'tca', "infer.json")
    with open(tca_infer_file_name, 'r', encoding='utf-8') as tca_infer_file:
        tca_infer_data = json.load(tca_infer_file)
    num_pos_data = len(tca_infer_data["data"])

    if mode == "tca":
        tca_neg_infer_file_name = os.path.join(kg_dir, config["tca"]["negatives"])
        with open(tca_neg_infer_file_name, 'r', encoding='utf-8') as tca_neg_infer_file:
            tca_neg_infer_data = json.load(tca_neg_infer_file)
        for idx, data in tca_neg_infer_data["data"].items():
            tca_infer_data["data"][str(num_pos_data+int(idx))] = data

    wikidata_infer_file_name = os.path.join(data_dir, "wikidata", "infer.json")
    with open(wikidata_infer_file_name, 'r', encoding='utf-8') as wikidata_infer_file:
        wikidata_infer_data = json.load(wikidata_infer_file)

    if (model_type == "tf_idf" or model_type == "all") and mode != "sim":
        logging.info("----------- TFIDF -------------")
        from entity_standardizer.tfidf import TFIDF

        tfidf = TFIDF(task)
        tfidf_start = time.time()
        tfidf_infer = copy.deepcopy(tca_infer_data)
        tfidf_infer = tfidf.infer(tfidf_infer)

        tfidf_end = time.time()
        tfidf_time = (tfidf_end - tfidf_start)
        if mode != 'deploy':
            cls_metrics(tfidf_infer, "TFIDF")

        tfidf_topk = topk(tfidf_infer, threshold)
        table_data["tfidf"] = {}
        table_data["tfidf"]["topk"] = tfidf_topk["topk"]
        table_data["tfidf"]["kns"] = tfidf_topk["kns"]
        table_data["tfidf"]["fpr"] = tfidf_topk["fpr"]
        table_data["tfidf"]["unks"] = tfidf_topk["unks"]
        table_data["tfidf"]["time"] = tfidf_time


    if model_type == "siamese" or model_type == "all":
        logging.info("----------- SIAMESE -------------")
        
        from entity_standardizer.siamese import SIAMESE
        siamese = SIAMESE(task)

        siamese_start = time.time()
        siamese_infer = copy.deepcopy(tca_infer_data)
        print(len(siamese_infer['data']))
        label         = siamese_infer.get("label", None)
        siamese_infer = siamese.infer(siamese_infer, batch_size=batch_size)
        siamese_end = time.time()
        siamese_time = (siamese_end - siamese_start)

        if mode != 'deploy':
            if label:    # Classification task
                # if mode != 'deploy':
                cls_metrics(siamese_infer, "Siamese")
                threshold = float(siamese.config['infer_thresholds_siamese']['HIGH_THRESHOLD'])
                siamese_topk = topk(siamese_infer, threshold)
                table_data["siamese"] = {}
                table_data["siamese"]["topk"] = siamese_topk["topk"]
                table_data["siamese"]["kns"] = siamese_topk["kns"]
                table_data["siamese"]["fpr"] = siamese_topk["fpr"]
                table_data["siamese"]["unks"] = siamese_topk["unks"]
                table_data["siamese"]["time"] = siamese_time
            else:
                (score_auc, score_f1) = sim_metrics(siamese_infer, "Siamese")
    '''
    if model_type == "gnn" or model_type == "all":
        logging.info("----------- GNN -------------")
        from entity_standardizer.gnn import GNN

        gnn = GNN(task)
        gnn_start = time.time()
        gnn_infer = copy.deepcopy(tca_infer_data)
        label     = gnn_infer.get("label", None)
        gnn_infer = gnn.infer(gnn_infer)
        gnn_end = time.time()
        gnn_time = (gnn_end - gnn_start)
        if label:    # Classification task
            if mode != "deploy":
                cls_metrics(gnn_infer, "GNN")
            gnn_topk = topk(gnn_infer, threshold)
            table_data["gnn"] = {}
            table_data["gnn"]["topk"] = gnn_topk["topk"]
            table_data["gnn"]["kns"]  = gnn_topk["kns"]
            table_data["gnn"]["fpr"]  = gnn_topk["fpr"]
            table_data["gnn"]["unks"] = gnn_topk["unks"]
            table_data["gnn"]["time"] = gnn_time
        else:       # Similarity task
            (score_auc, score_f1) = sim_metrics(gnn_infer, "GNN")   
    '''
        
    if (model_type == "wiki_data_api" or model_type == "all") and mode == "wikidata":
        logging.info("----------- WIKIDATA API -------------")
        from entity_standardizer.wdapi import WDAPI

        wdapi = WDAPI(task)
        wdapi_start = time.time()
        wdapi_infer = copy.deepcopy(wikidata_infer_data)
        wdapi_infer = wdapi.infer(wdapi_infer)
        wdapi_end = time.time()
        wdapi_time = (wdapi_end - wdapi_start)    
        wdapi_x_data = []
        wdapi_topk_data = [[] for k in range(3)]
        for thr in np.arange(0.0,1.0,0.05):                    
            wdapi_topk = topk(wdapi_infer, thr)
            wdapi_x_data.append(wdapi_topk['fpr']/tfidf_topk['unks'])
            for k in range(3):
                wdapi_topk_data[k].append(wdapi_topk['topk'][k]/wdapi_topk['kns'])
        plot(wdapi_x_data, wdapi_topk_data, '-', 'g', 'wdapi')
        wdapi_topk = topk(wdapi_infer, threshold)
        table_data["wdapi"] = {}
        table_data["wdapi"]["topk"] = wdapi_topk["topk"]
        table_data["wdapi"]["kns"] = wdapi_topk["kns"]
        table_data["wdapi"]["fpr"] = wdapi_topk["fpr"]
        table_data["wdapi"]["unks"] = wdapi_topk["unks"]
        table_data["wdapi"]["time"] = wdapi_time

    if mode == "tca":
        # axis labels
        pyplot.xlabel('False positive rate')
        pyplot.ylabel('Top-1 accuracy')
        # show the legend
        pyplot.legend()
        if show:
            # show the plot
            pyplot.show()
        else:
            pyplot.savefig("top1.png")
        print_gh_markdown(table_data)
    elif mode == "sim":
        # axis labels
        pyplot.xlabel('Recall')
        pyplot.ylabel('Precision')
        # show the legend
        pyplot.legend()
        # show the plot
        if show:
            pyplot.show()
        else:
            pyplot.savefig("prc.png")