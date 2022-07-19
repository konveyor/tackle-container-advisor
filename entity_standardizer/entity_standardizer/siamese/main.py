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

import os, logging, random
from sklearn.neighbors import KNeighborsClassifier
import torch
from tqdm import tqdm
import pickle

from .loss import batch_all_triplet_loss, batch_hard_triplet_loss
from .model import Model
from .data import generate_train_entity_sets, batchGenerator, loader

class SIAMESE():
    def __init__(self, task_name):
        super().__init__()
        import configparser
                
        self.task_name = task_name
        self.config    = configparser.ConfigParser()
        common         = os.path.join("config", "common.ini")
        siamese         = os.path.join("config", self.task_name, "siamese.ini")
        self.config.read([common, siamese])
        self.config["task"] = {}
        self.config["task"]["name"] = self.task_name
                   
    def infer(self, infer_data):

        if self.config['train']['disable_cuda']=='False' and torch.cuda.is_available():
            device    = torch.device('cuda')    
        else:
            device    = torch.device('cpu')
        logging.info(f"Device = {device}")

        model_dir  = os.path.join(self.config['general']['model_dir'], self.config['task']['name'])
        model_name = 'siamese.pt'
        model_path = os.path.join(model_dir, model_name)
        model  = Model(self.config)

        if not os.path.exists(model_path):
            logging.info(f"{model_name} does not exist, running training to generate model.")
            model  = self.train()
        else:
            logging.info(f"Loading training parameters from {model_path}.")
            model.load_state_dict(torch.load(model_path, map_location=device))

        model.to(device=device)
        model.eval()

        entity_vector_name = 'entity_vector.pickle'
        entity_vector_path = os.path.join(model_dir, entity_vector_name)
        if not os.path.exists(entity_vector_path):
            _, train_entity_id_to_name = loader(self.config)
            train_entities, labels = list(train_entity_id_to_name.values()), list(train_entity_id_to_name.keys())
            cls = model(train_entities, device)
            embeddings = cls.detach().cpu().numpy()
            with open(entity_vector_path, 'wb') as f:
                pickle.dump((embeddings, labels), f)
        else:
            with open(entity_vector_path, 'rb') as f:
                embeddings,  labels = pickle.load(f)
                num_entities = len(embeddings)
                logging.info(f"Loading embeddings of {num_entities} entities from {entity_vector_path}.")

        x_test = [d['mention'] for _, d in infer_data['data'].items()]
        # y_test = [d['entity_id'] for _, d in infer_data['data'].items()]

        knn = KNeighborsClassifier(n_neighbors=1, metric='cosine').fit(embeddings, labels)

        cls_test = model(x_test, device)
        n_neighbors = int(self.config['infer'].get('topk', 10))
        distances, indices = knn.kneighbors(cls_test.detach().cpu().numpy(),  n_neighbors=n_neighbors)
        distances, indices = distances.tolist(), indices.tolist()
        pred_label_ids = []
        for pred in indices: 
            label = [labels[i] for i in pred]
            pred_label_ids.append(label)
        for idx, inf_id in enumerate(infer_data['data']):
            predictions = list(zip(pred_label_ids[idx], [1-d for d in distances[idx]]))
            infer_data['data'][inf_id]['predictions'] = predictions
        return infer_data


    def train(self):
        if self.config['train']['disable_cuda']=='False' and torch.cuda.is_available():
            device    = torch.device('cuda')    
        else:
            device    = torch.device('cpu')

        seed = int(self.config['train'].get('seed', 0))
        lr = float(self.config['train'].get('lr', 1e-4))
        epochs = int(self.config['train'].get('epoch_num', 80))
        batch_size = int(self.config['train'].get('batch_size', 16))
        group_size = int(self.config['train'].get('group_size', 10))
        margin = int(self.config['loss'].get('margin', 10))

        model_dir  = os.path.join(self.config['general']['model_dir'], self.config['task']['name'])
        model_name = 'siamese.pt'
        model_path = os.path.join(model_dir, model_name)

        train_entity_id_to_mentions, train_entity_id_to_name = loader(self.config)
        
        model = Model(self.config)
        optimizer = torch.optim.AdamW(model.parameters(), lr=lr)
        model.to(device)
        model.train()
        for epoch in tqdm(range(epochs)):
            e_loss = []
            data = generate_train_entity_sets(train_entity_id_to_mentions, train_entity_id_to_name, group_size-1, anchor=True)
            random.shuffle(data)
            for x, y in batchGenerator(data, batch_size):
                # print(len(x), len(y), end='-->')
                optimizer.zero_grad()
                cls = model(x, device)
                if epoch < epochs / 2:
                    loss, _ = batch_all_triplet_loss(torch.tensor(y).to(device), cls, margin, squared=False)
                else:
                    loss = batch_hard_triplet_loss(torch.tensor(y).to(device), cls, margin, squared=False)
                loss.backward()
                optimizer.step()
                e_loss.append(loss.detach().cpu())
                # print(epoch, loss)
                del cls, loss
                torch.cuda.empty_cache()
            print('\nEpoch: {} Averge loss: {}'.format(epoch, sum(e_loss)/len(e_loss)))
        torch.save(model.state_dict(), model_path)
        
        entity_vector_name = 'entity_vector.pickle'
        entity_vector_path = os.path.join(model_dir, entity_vector_name)
        train_entities, labels = list(train_entity_id_to_name.values()), list(train_entity_id_to_name.keys())
        model.eval()
        cls = model(train_entities, device)
        embeddings = cls.detach().cpu().numpy()
        with open(entity_vector_path, 'wb') as f:
            pickle.dump((embeddings, labels), f)

        return model