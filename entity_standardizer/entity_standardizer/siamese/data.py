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

import random
import json
import os
def generate_train_entity_sets(entity_id_mentions, entity_id_name, group_size, anchor=True):
    # split entity mentions into groups
    # anchor = False, don't add entity name to each group, simply treat it as a normal mention
    entity_sets = []
    if anchor:
        for id, mentions in entity_id_mentions.items():
            random.shuffle(mentions)
            positives = [mentions[i:i + group_size] for i in range(0, len(mentions), group_size)]
            anchor_positive = [([entity_id_name[id]]+p, id) for p in positives]
            entity_sets.extend(anchor_positive)
    else:
        for id, mentions in entity_id_mentions.items():
            group = list(set([entity_id_name[id]] + mentions))
            random.shuffle(group)
            positives = [(mentions[i:i + group_size], id) for i in range(0, len(mentions), group_size)]
            entity_sets.extend(positives)
    return entity_sets

def batchGenerator(data, batch_size):
    for i in range(0, len(data), batch_size):
        batch = data[i:i+batch_size]
        x, y = [], []
        for t in batch:
            x.extend(t[0])
            y.extend([t[1]]*len(t[0]))
        yield x, y


def loader(config):
    kg_dir = config['general']['kg_dir']
    kg_file_name = os.path.join(kg_dir, 'tca_entities.json')
    with open(kg_file_name, 'r', encoding='utf-8') as file:
        entities = json.load(file)
    all_entity_id_name = {entity['entity_id']: entity['entity_name'] for _, entity in entities['data'].items()}

    data_dir = config['general']['data_dir']
    name        = config['task']['name']
    json_file_name = os.path.join(data_dir, name, 'train.json')
    with open(json_file_name, 'r', encoding='utf-8') as file:
        train = json.load(file)

    train_entity_id_mentions = {data['entity_id']: data['mentions'] for _, data in train['data'].items()}
    train_entity_id_name = {data['entity_id']: all_entity_id_name[data['entity_id']] for _, data in train['data'].items()}
    
    return train_entity_id_mentions, train_entity_id_name