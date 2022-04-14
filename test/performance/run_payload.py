import os
import sys
import logging
import configparser
import requests
from concurrent.futures import ThreadPoolExecutor
import json
import time

logger = logging.getLogger('test')
logger.setLevel(logging.INFO)

config   = configparser.ConfigParser()
test     = os.path.join("config", "test.ini")
config.read(test)
try:
    host = config['performance']['host']
    port = config['performance']['port']
except KeyError as k:
    logger.error(f'{k}  is not a key in your test.ini file.')
    exit()

with open(os.path.join("test", "performance", "small.json")) as f:
    data = json.load(f)

actual_len = len(data)

try:
    required_data = int(sys.argv[2])
except IndexError:
    required_data = 1000
  
quo = required_data // actual_len
rem = required_data % actual_len
data = quo * data + data[:rem]
print('Payload size : ', len(data), 'records')
  
try:
    n_user = int(sys.argv[1])
except IndexError:
    n_user = 1
  
print('No of concurrent user : ',n_user)
  
urls = [host+':'+port+'/containerization-assessment']*n_user  

def call_tca(url):
    start = time.time()
    headers = {'Accept': 'application/json', 'Content-Type': 'application/json'}
    resp = requests.post(url, data=json.dumps(data), headers=headers)
    return time.time()-start,resp
  
  
with ThreadPoolExecutor() as pool:
    results = pool.map(call_tca, urls)
    
success = 0
for i,whole_resp in enumerate(list(results)):
    time_taken, resp_code = whole_resp
    if resp_code.status_code == 201:
        success += 1
    print(f'User {i+1} Time taken  : {round(time_taken,2)}s Response Code : {resp_code.status_code}')
  
print(f'Passed - {success}/{n_user}')
