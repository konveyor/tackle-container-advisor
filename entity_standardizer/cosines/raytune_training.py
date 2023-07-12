import warnings
warnings.filterwarnings('ignore')

from tqdm.notebook import tqdm
import torch
import json
import random 
import numpy as np
import matplotlib.pyplot as plt

from transformers import AutoTokenizer
from transformers import AutoModel
from utils import batch_all_triplet_loss, batch_hard_triplet_loss
from ray import tune
import ray

from sklearn.model_selection import KFold
from sklearn.model_selection import StratifiedKFold

import transformers
transformers.utils.logging.set_verbosity_error()


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



with open('./kg/tca_entities.json', 'r') as file:
    entities = json.load(file)
all_entity_id_name = {entity['entity_id']: entity['entity_name'] for _, entity in entities['data'].items()}


with open('./data/tca/train.json', 'r') as file:
    train = json.load(file)
train_entity_id_mentions = {data['entity_id']: data['mentions'] for _, data in train['data'].items()}
train_entity_id_name = {data['entity_id']: all_entity_id_name[data['entity_id']] for _, data in train['data'].items()}

X, Y = [], []
for k, v in train_entity_id_mentions.items():
    X.extend(v)
    Y.extend(len(v)*[k])
X, Y = np.array(X), np.array(Y)


num_sample_per_class = 10  # samples in each group
batch_size = 16 # number of groups, effective batch_size = batch_size * num_sample_per_class
margin = 2
epochs = 60
DEVICE = torch.device('cuda') if torch.cuda.is_available() else torch.device('cpu')
MODEL_NAME = 'prajjwal1/bert-small'


def train_siamese(config):
    tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
    skf = StratifiedKFold(n_splits=5, shuffle=True, random_state=0)
#     skf = KFold(n_splits=5, shuffle=True, random_state=0)
    
    all_acc, all_loss = [], []
    for fold, (train_index, test_index) in enumerate(skf.split(X, Y)):
        model = AutoModel.from_pretrained(MODEL_NAME)
        optimizer = torch.optim.AdamW(model.parameters(), lr=config['lr'])  
        X_train, X_test = X[train_index], X[test_index]
        y_train, y_test = Y[train_index], Y[test_index]
        
        train_partial_entity_id_mentions =  {}
        unique, counts = np.unique(y_train, return_counts=True)
        for id in unique:
            idx = np.where(y_train==id)
            mentions = np.array(X_train)[idx[0]].tolist()
            train_partial_entity_id_mentions[id] = mentions
        
        train_entities = [train_entity_id_name[id] for id in train_partial_entity_id_mentions]
        labels = [id for id in train_partial_entity_id_mentions]
        
        temp = []
        for idx, men in enumerate(X_test):
            if men not in train_entities and men.lower() not in train_entities:
                temp.append((men, y_test[idx]))
        X_test = [t[0] for t in temp]
        y_test = [t[1] for t in temp]
        print(len(X_test),len(y_test))
        
        fold_acc, fold_loss = [], []
        for epoch in range(config['epochs']):
            model.to(DEVICE)
            model.train()
            data = generate_train_entity_sets(train_partial_entity_id_mentions, train_entity_id_name, config['batch_size']-1, anchor=True)
            random.shuffle(data)
            for x, y in batchGenerator(data, batch_size):
                # print(len(x), len(y), end='-->')
                optimizer.zero_grad()
                inputs = tokenizer(x, padding=True, return_tensors='pt')
                inputs = inputs.to(DEVICE)
                outputs = model(**inputs)
                cls = outputs.last_hidden_state[:,0,:]
                
                if config['training'] == 'halfhalf':
                    if epoch // (config['epochs'] / 4) % 2 == 0:
                        loss, _ = batch_all_triplet_loss(torch.tensor(y).to(DEVICE), cls, config['margin'], squared=config['squared'])
                    else:
                        loss = batch_hard_triplet_loss(torch.tensor(y).to(DEVICE), cls, config['margin'], squared=config['squared'])
                else:
                    if epoch < epochs / 2:
                        loss, _ = batch_all_triplet_loss(torch.tensor(y).to(DEVICE), cls, config['margin'], squared=config['squared'])
                    else:
                        loss = batch_hard_triplet_loss(torch.tensor(y).to(DEVICE), cls, config['margin'], squared=config['squared'])
                loss.backward()
                optimizer.step()
                fold_loss.append(loss.item())
                # print(epoch, loss)
                del inputs, outputs, cls
            torch.cuda.empty_cache()
            
            if (epoch+1) % config['epochs'] == 0:
                model.eval()
                inputs = tokenizer(train_entities, padding=True, return_tensors='pt')
                inputs = inputs.to(DEVICE)
                outputs = model(**inputs)
                cls = outputs.last_hidden_state[:,0,:]

                from sklearn.neighbors import KNeighborsClassifier
                embeddings = cls.detach().cpu().numpy()

                knn = KNeighborsClassifier(n_neighbors=1).fit(embeddings, labels)

                inputs_test = tokenizer(X_test, padding=True, return_tensors='pt')
                inputs_test = inputs_test.to(DEVICE)
                outputs_test = model(**inputs_test)
                cls_test = outputs_test.last_hidden_state[:,0,:]

                distances, indices = knn.kneighbors(cls_test.detach().cpu().numpy(),  n_neighbors=1)
                pred_labels = [labels[i[0]] for i in indices]

                acc = sum(np.array(pred_labels) == y_test) / len(y_test)
                fold_acc.append(acc)
                del inputs, inputs_test, outputs, outputs_test, cls, cls_test
                torch.cuda.empty_cache()
        all_acc.append(fold_acc)
        all_loss.append(fold_loss)
    tune.report(allAcc=all_acc, allLoss=all_loss)
    
    

config = {
    "lr": tune.grid_search([1e-5]),     # "lr": tune.grid_search([1e-4, 5e-5, 1e-5, 1e-6])
    "batch_size": tune.grid_search([16]), # "batch_size": tune.grid_search([4, 8, 16, 32])
    "margin": tune.grid_search([2]), # "margin": tune.grid_search([0.5, 1, 2, 5, 10])
    "epochs": tune.grid_search([200, 220, 240, 260, 280, 300]),
    "squared":tune.grid_search([True, False]),
    "training": tune.grid_search(['halfhalf', 'alternating'])
}

analysis = tune.run(train_siamese, config=config, resources_per_trial={"gpu": 1}, verbose=1)