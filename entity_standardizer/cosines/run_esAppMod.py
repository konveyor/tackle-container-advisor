import torch
import json
import random 
import numpy as np
from transformers import AutoTokenizer
from transformers import AutoModel
from loss import batch_all_triplet_loss, batch_hard_triplet_loss
from sklearn.neighbors import KNeighborsClassifier

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


with open('./data/esAppMod/tca_entities.json', 'r') as file:
    entities = json.load(file)
all_entity_id_name = {entity['entity_id']: entity['entity_name'] for _, entity in entities['data'].items()}

with open('./data/esAppMod/train.json', 'r') as file:
    train = json.load(file)
train_entity_id_mentions = {data['entity_id']: data['mentions'] for _, data in train['data'].items()}
train_entity_id_name = {data['entity_id']: all_entity_id_name[data['entity_id']] for _, data in train['data'].items()}


num_sample_per_class = 10  # samples in each group
batch_size = 16 # number of groups, effective batch_size for computing triplet loss = batch_size * num_sample_per_class
margin = 2
epochs = 200
DEVICE = torch.device('cuda') if torch.cuda.is_available() else torch.device('cpu')
MODEL_NAME = 'prajjwal1/bert-small' #'bert-base-cased'  'distilbert-base-cased' 

tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
model = AutoModel.from_pretrained(MODEL_NAME)
optimizer = torch.optim.AdamW(model.parameters(), lr=1e-5)

model.to(DEVICE)
model.train()

losses = []

for epoch in range(epochs):
    data = generate_train_entity_sets(train_entity_id_mentions, train_entity_id_name, num_sample_per_class-1, anchor=True)
    random.shuffle(data)
    for x, y in batchGenerator(data, batch_size):
        print(len(x), len(y), end='-->')
        optimizer.zero_grad()
        inputs = tokenizer(x, padding=True, return_tensors='pt')
        inputs = inputs.to(DEVICE)
        outputs = model(**inputs)
        cls = outputs.last_hidden_state[:,0,:]
        if epoch < epochs / 2:
            loss, _ = batch_all_triplet_loss(torch.tensor(y).to(DEVICE), cls, margin, squared=False)
        else:
            loss = batch_hard_triplet_loss(torch.tensor(y).to(DEVICE), cls, margin, squared=False)
        loss.backward()
        optimizer.step()
        print(epoch, loss)
        losses.append(loss)
        del inputs, outputs, cls, loss
        torch.cuda.empty_cache()

torch.save(model.state_dict(), './checkpoint/siamese.pt')

with open('./data/esAppMod/infer.json', 'r') as file:
    test = json.load(file)
x_test = [d['mention'] for _, d in test['data'].items()]
y_test = [d['entity_id'] for _, d in test['data'].items()]
train_entities, labels = list(train_entity_id_name.values()), list(train_entity_id_name.keys())

model.eval()
inputs = tokenizer(train_entities, padding=True, return_tensors='pt')
outputs = model(**inputs)
cls = outputs.last_hidden_state[:,0,:]
embeddings = cls.detach().numpy()


inputs_test = tokenizer(x_test, padding=True, return_tensors='pt')
outputs_test = model(**inputs_test)
cls_test = outputs_test.last_hidden_state[:,0,:]


knn = KNeighborsClassifier(n_neighbors=1, metric='cosine').fit(cls.detach().numpy(), labels)
n_neighbors = [1, 3, 5, 10]

for n in n_neighbors:  
    distances, indices = knn.kneighbors(cls_test.detach().numpy(),  n_neighbors=n)
    num = 0
    for a,b in zip(y_test, indices):
        b = [labels[i] for i in b]
        if a in b:
            num += 1
    print(f'Top-{n:<3} accuracy: {num / len(y_test)}')
print(np.min(distances), np.max(distances))
