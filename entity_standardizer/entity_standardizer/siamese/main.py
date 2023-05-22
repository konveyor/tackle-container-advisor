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

import os, logging, random, time
import numpy as np
from sklearn.neighbors import KNeighborsClassifier
import torch
from tqdm import tqdm
import pickle

from .loss import batch_all_triplet_loss, batch_hard_triplet_loss
from .model import Model
from .data import generate_train_entity_sets, batchGenerator, loader
from sklearn.metrics.pairwise import cosine_similarity

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
                   
    def infer(self, infer_data, batch_size=0):

        logging.info(f"batch_size {batch_size}.")

        if self.config['train']['disable_cuda'] == 'False' and torch.cuda.is_available():
            device    = torch.device('cuda')    
        else:
            device    = torch.device('cpu')
        logging.info(f"Device = {device}")

        model_dir = os.path.join(self.config['general']['model_dir'], self.config['task']['name'],'siamese_model')
        model_name = 'pytorch_model.bin' #'siamese.pt'
        model_path = os.path.join(model_dir, model_name)
        model = Model(self.config)

        if not os.path.exists(model_path):
            logging.info(f"{model_name} does not exist, running training to generate model.")
            model  = self.train()
        else:
            logging.info(f"Loading training parameters from {model_path}.")
            model.load_state_dict(torch.load(model_path, map_location=device))
            logging.info(f"Done.")

        model.to(device=device)
        model.eval()

        entity_vector_name = 'entity_vector.pickle'
        entity_vector_path = os.path.join(model_dir, entity_vector_name)
        if not os.path.exists(entity_vector_path):
            logging.info(f"Computing training embeddings to {entity_vector_path}.")
            _, train_entity_id_to_name = loader(self.config)
            train_entities, labels = list(train_entity_id_to_name.values()), list(train_entity_id_to_name.keys())

            if batch_size > 0:
                for i in tqdm(range(0, int(len(train_entities)/batch_size)+1)):
                    if i * batch_size < len(train_entities) - 1:
                        # logging.info(f'{i}/{int(len(train_entities)/batch_size)}')
                        cls = model(train_entities[i*batch_size:min(len(train_entities),(i+1)*batch_size)], device)
                        if i == 0:
                            embeddings = cls.detach().cpu().numpy()
                        else:
                            embeddings = np.concatenate((embeddings, cls.detach().cpu().numpy()), axis=0)
            else:
                cls = model(train_entities, device)
                embeddings = cls.detach().cpu().numpy()

            logging.info(f'writing to {entity_vector_path}')
            with open(entity_vector_path, 'wb') as f:
                pickle.dump((embeddings, labels), f)

            logging.info('done')
        else:
            with open(entity_vector_path, 'rb') as f:
                embeddings,  labels = pickle.load(f)
                num_entities = len(embeddings)
            logging.info(f"Loading embeddings of {num_entities} entities from {entity_vector_path}.")


        inf_start     = time.time()
        label         = infer_data.get("label", None)
        if label:
            logging.info('doing test embeddings extraction')

            x_test = [d['mention(s)'] for _, d in infer_data['data'].items()]
            # y_test = [d['entity_id'] for _, d in infer_data['data'].items()]

            knn = KNeighborsClassifier(n_neighbors=1, metric='cosine').fit(embeddings, labels)

            if batch_size > 0:
                for i in tqdm(range(0, int(len(x_test)/batch_size)+1)):
                    if i*batch_size < len(x_test)-1:
                        # logging.info(f'{i}/{int(len(train_entities)/batch_size)}')
                        cls_test = model(x_test[i*batch_size:min(len(x_test),(i+1)*batch_size)], device)
                        if i == 0:
                            test_embeddings = cls_test.detach().cpu().numpy()
                        else:
                            test_embeddings = np.concatenate((test_embeddings, cls_test.detach().cpu().numpy()), axis=0)
            else:
                cls_test = model(x_test, device)
                test_embeddings = cls_test.detach().cpu().numpy()



            n_neighbors = int(self.config['infer'].get('topk', 10))

            logging.info('doing knn matching')

            distances, indices = knn.kneighbors(test_embeddings,  n_neighbors=n_neighbors)
            distances, indices = distances.tolist(), indices.tolist()

            pred_label_ids = []
            for pred in indices: 
                label = [labels[i] for i in pred]
                pred_label_ids.append(label)
            for idx, inf_id in enumerate(infer_data['data']):
                predictions = list(zip(pred_label_ids[idx], [1-d for d in distances[idx]]))
                infer_data['data'][inf_id]['predictions'] = predictions
        else:
            logging.info('get infer data')
            data = infer_data["data"]
            slice_size = 5000
            with tqdm(range(int(np.ceil(len(data)/slice_size))), ncols=100) as progress:
                for i in progress:
                    mention_0s = []
                    mention_1s = []
                    for idx in range(i*slice_size, min(len(data), (i+1)*slice_size)):
                        mention_0s.append(data[str(idx)]["mention_0"])
                        mention_1s.append(data[str(idx)]["mention_1"])

                    m0_set = list(set(mention_0s))
                    cls_test    = model(m0_set, device)
                    m0_vecs_slc = cls_test.detach().cpu().numpy()
                    m0_vecs_dct = {}
                    for idx, mention in enumerate(m0_set):
                        m0_vecs_dct[mention] = m0_vecs_slc[idx]

                    m1_set = list(set(mention_1s))
                    cls_test    = model(m1_set, device)
                    m1_vecs_slc = cls_test.detach().cpu().numpy()
                    m1_vecs_dct = {}
                    for idx, mention in enumerate(m1_set):
                        m1_vecs_dct[mention] = m1_vecs_slc[idx]
                
                    m0_vecs = []
                    for idx, mention in enumerate(mention_0s):
                        m0_vecs.append(m0_vecs_dct[mention])
                    m0_vecs = np.array(m0_vecs)
                    m0_vecs_dct.clear()

                    m1_vecs = []
                    for idx, mention in enumerate(mention_1s):
                        m1_vecs.append(m1_vecs_dct[mention])
                    m1_vecs = np.array(m1_vecs)    
                    m1_vecs_dct.clear()

                    idx       = 0
                    for m0,m1 in zip(m0_vecs, m1_vecs):
                        men0 = data[str(i*slice_size+idx)]["mention_0"]
                        men1 = data[str(i*slice_size+idx)]["mention_1"]
                        csim      = cosine_similarity(np.array([m0]), np.array([m1]))
                        sim       = torch.from_numpy(csim)        
                        _, max_sim_idx = torch.topk(sim, 1, dim=1)
                        sim_score = sim[max_sim_idx].item()
                        data[str(i*slice_size+idx)]["sim_score"] = sim_score
                        idx += 1
        inf_end     = time.time()
        logging.info(f"Inference took {inf_end-inf_start:.2f} seconds.")

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
