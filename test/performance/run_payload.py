import os
import sys
import logging
import configparser
import requests
from concurrent.futures import ThreadPoolExecutor
import json
import time
import subprocess

def call_tca(url):
    global data
    start = time.time()
    headers = {'Accept': 'application/json', 'Content-Type': 'application/json'}
    resp = requests.post(url, data=json.dumps(data), headers=headers)
    return time.time()-start,resp

def get_performance_data(n_user, n_data):
    global alldata, data
    actual_len = len(alldata)
    if n_data != 0:
        required_data = n_data
    else:
        required_data = actual_len
    quo = required_data // actual_len
    rem = required_data % actual_len
    data = quo * alldata + alldata[:rem]

    assert(n_user > 0)
  
    urls = [host+':'+port+'/standardize']*n_user  

    with open(os.devnull, 'wb') as devnull:
        cmd = ctrserv + ' run --name tca -d -p 8000:'+port+ ' -m '+memlim+' '+image+':'+version
        subprocess.check_call(cmd, shell=True, stdout=devnull, stderr=subprocess.STDOUT)

    try:
        status_code = 400
        while status_code != 200:    
            headers = {'Accept': 'application/json', 'Content-Type': 'application/json'}
            resp = requests.get(host+':'+port+'/health_check', headers=headers)
            status_code = resp.status_code

        with ThreadPoolExecutor() as pool:
            results = pool.map(call_tca, urls)
    
        result           = {}
        result['n_user']    = n_user
        result['n_data']    = len(data)
        result['succ_rate'] = 0
        result['avg_resp_time'] = 0
        for i,whole_resp in enumerate(list(results)):
            time_taken, resp_code = whole_resp
            result['avg_resp_time'] += round(time_taken,2)
            if resp_code.status_code == 201:
                result['succ_rate'] += 1

        result['succ_rate'] = result['succ_rate']/n_user
        result['avg_resp_time'] = round(result['avg_resp_time']/n_user, 2)
    except Exception as e:
        print("Exception = ", e)

    with open(os.devnull, 'wb') as devnull:
        cmd = ctrserv + ' stats --no-stream --format=json tca > stats.json'
        subprocess.check_call(cmd, shell=True, stdout=devnull, stderr=subprocess.STDOUT)
        cmd = ctrserv + ' exec -it tca grep \"unique mentions\" /app/gunicorn.debug.log'
        subprocess.check_call(cmd, shell=True)
        cmd = ctrserv + ' stop tca'
        subprocess.check_call(cmd, shell=True, stdout=devnull, stderr=subprocess.STDOUT)
        cmd = ctrserv + ' rm tca'
        subprocess.check_call(cmd, shell=True, stdout=devnull, stderr=subprocess.STDOUT)


    with open('stats.json', 'r') as stats_file:
        stats = json.load(stats_file)
        result['server'] = stats[0]

    return result

logging.basicConfig(level=logging.INFO, format="[%(asctime)s] %(name)s:%(levelname)s in %(filename)s:%(lineno)s - %(message)s", filemode='w')
config      = configparser.ConfigParser()
test        = os.path.join("config", "test.ini")
config.read(test)
try:
    host   = config['service']['host']
    port   = config['service']['port']
    ctrserv= config['service']['ctrserv']
    image  = config['service']['image']
    version= config['service']['version']
    memlim = config['service']['memlim']
    file   = config['payload']['file']
except KeyError as k:
    logging.error(f'{k}  is not a key in your test.ini file.')
    exit()

data    = None
alldata = None
with open(os.path.join("test", "performance", file)) as f:
    alldata = json.load(f)

dpts    = [(1,10), (1,100), (1,1000), (1,5000)]
results = []
for pt in dpts:
    print("Working on", pt)
    result = get_performance_data(pt[0], pt[1])
    results.append(result)

with open(os.path.join("test", "performance", "results.json"), 'w') as f:
    json.dump(results, f, indent=4)


