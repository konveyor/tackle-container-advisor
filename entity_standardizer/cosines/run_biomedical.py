import os, random
from collections import defaultdict

import torch
import torch.nn as nn
from torch.utils.data import DataLoader

import torch.distributed as dist
from torch.nn.parallel import DistributedDataParallel as DDP
from torch.utils.data.distributed import DistributedSampler
import torch.multiprocessing as mp

from transformers import AutoTokenizer, AutoModel

from data import generate_train_entity_sets

from tqdm import tqdm  ### need to use ipywidgets==7.7.1 the newest version doesn't work
from loss import batch_all_triplet_loss, batch_hard_triplet_loss
from sklearn.neighbors import KNeighborsClassifier
import numpy as np
import logging


def setup(rank, world_size):
    os.environ['MASTER_ADDR'] = 'localhost'
    os.environ['MASTER_PORT'] = '12355'
    dist.init_process_group("nccl", rank=rank, world_size=world_size)
    torch.cuda.set_device(rank)

def cleanup():
    dist.destroy_process_group()

def train_dataloader(vocab_entity_id_mentions, num_sample_per_class, rank, world_size, batch_size=32, pin_memory=True, num_workers=8):
    dataset = generate_train_entity_sets(vocab_entity_id_mentions, entity_id_name=None, group_size=num_sample_per_class, anchor=False)
    sampler = DistributedSampler(dataset, num_replicas=world_size, rank=rank, shuffle=True, drop_last=False)
    return DataLoader(dataset, batch_size=batch_size, pin_memory=pin_memory, num_workers=num_workers, drop_last=False, shuffle=False, sampler=sampler)

def test_dataloader(test_mentions, batch_size=32):
    return DataLoader(test_mentions, batch_size=batch_size, shuffle=False)

def train(rank, epoch, epochs, train_dataloader, model, optimizer, tokenizer, margin):
    # DEVICE = torch.device(f"cuda:{dist.get_rank()}")
    DEVICE = torch.device(f'cuda:{rank}')
    model.train()
    epoch_loss, epoch_len = [epoch], [epoch]

    for groups in tqdm(train_dataloader, desc =f'Training batches on {DEVICE}'):
        groups[0][:] = zip(*groups[0][::-1])
        x, y = [], []
        for mention, label in zip(groups[0], groups[1]):
            mention = [m for m in mention if m != 'PAD']
            x.extend(mention)
            y.extend([label.item()]*len(mention))

        optimizer.zero_grad()
        inputs = tokenizer(x, padding=True, return_tensors='pt')
        inputs = inputs.to(DEVICE)
        cls = model(inputs)
#         cls = torch.nn.functional.normalize(cls)   ## normalize cls embedding before computing loss, didn't work
#         cls = torch.nn.Dropout(p= 0.25)(cls)    ## add dropout, didn't work

#         loss, _ = batch_all_triplet_loss(torch.tensor(y).to(DEVICE), cls, margin, squared=True)
#         loss = batch_hard_triplet_loss(torch.tensor(y).to(DEVICE), cls, margin, squared=True)

        if epoch < epochs / 2:
#         if epoch // (epochs / 4) % 2 == 0:   ## various ways of alternating batch all and batch hard, no obvious advantage
#         if (epoch // 10) % 2 == 0:  ## various ways of alternating batch all and batch hard, no obvious advantage
            loss, _ = batch_all_triplet_loss(torch.tensor(y).to(DEVICE), cls, margin, squared=False)
        else:
            loss = batch_hard_triplet_loss(torch.tensor(y).to(DEVICE), cls, margin, squared=False)
            
        #### tried circle loss, no obvious advantage

        loss.backward()
        optimizer.step()
        # logging.info(f'{epoch} {len(x)} {loss.item()}')
        epoch_loss.append(loss.item())
        epoch_len.append(len(x))
        # del inputs, cls, loss
        # torch.cuda.empty_cache()
    logging.info(f'{DEVICE}{epoch_len}')
    logging.info(f'{DEVICE}{epoch_loss}')

def check_label(predicted_cui: str, golden_cui: str) -> int:
    """
    Some composite annotation didn't consider orders
    So, set label '1' if any cui is matched within composite cui (or single cui)
    Otherwise, set label '0'
    """
    return int(len(set(predicted_cui.replace('+', '|').split("|")).intersection(set(golden_cui.replace('+', '|').split("|"))))>0)

def getEmbeddings(mentions, model, tokenizer, DEVICE, batch_size=200):
    model.to(DEVICE)
    model.eval()
    dataloader = DataLoader(mentions, batch_size, shuffle=False)
    embeddings = np.empty((0, 768), np.float32)
    with torch.no_grad():
        for mentions in tqdm(dataloader, desc ='Getting embeddings'):
            inputs = tokenizer(mentions, padding=True, return_tensors='pt')
            inputs = inputs.to(DEVICE)
            cls = model(inputs)
            embeddings = np.append(embeddings, cls.detach().cpu().numpy(), axis=0)
            # del inputs, cls
            # torch.cuda.empty_cache()
    return embeddings

def eval(rank, vocab_mentions, vocab_ids, test_mentions, test_cuis, id_to_cui, model, tokenizer):
    DEVICE = torch.device(f'cuda:{rank}')
    vocab_embeddings = getEmbeddings(vocab_mentions, model, tokenizer, DEVICE)
    test_embeddings = getEmbeddings(test_mentions, model, tokenizer, DEVICE)

    knn = KNeighborsClassifier(n_neighbors=1, metric='cosine').fit(vocab_embeddings, vocab_ids)
    n_neighbors = [1, 3, 5, 10]
    res = []
    for n in n_neighbors:  
        distances, indices = knn.kneighbors(test_embeddings,  n_neighbors=n)
        num = 0
        for gold_cui, idx in zip(test_cuis, indices):
            candidates = [id_to_cui[vocab_ids[i]] for i in idx]
            for c in candidates:
                if check_label(c, gold_cui):
                    num += 1
                    break
        res.append(num / len(test_cuis))
        # print(f'Top-{n:<3} accuracy: {num / len(test_cuis)}')
    return res
    # print(np.min(distances), np.max(distances))

def save_checkpoint(model, res, epoch, dataName):
    logging.info(f'Saving model {epoch} {res} ')
    torch.save(model.state_dict(), './checkpoints/'+dataName+'.pt')

class Model(nn.Module):
    def __init__(self,MODEL_NAME):
        super(Model, self).__init__()
        self.model = AutoModel.from_pretrained(MODEL_NAME)

    def forward(self, inputs):
        outputs = self.model(**inputs)
        cls = outputs.last_hidden_state[:,0,:]
        return cls

def main(rank, world_size, config):

    print(f"Running main(**args) on rank {rank}.")
    setup(rank, world_size)

    dataName = config['DEFAULT']['dataName']
    logging.basicConfig(format='%(asctime)s %(message)s', filename=config['train']['ckt_path']+dataName+'.log', filemode='a', level=logging.INFO)

    vocab = defaultdict(set)
    with open('./data/biomedical/'+dataName+'/'+config['train']['dictionary']) as f:
        for line in f:            
            vocab[line.strip().split('||')[0]].add(line.strip().split('||')[1].lower())

    cui_to_id, id_to_cui = {}, {}
    vocab_entity_id_mentions = {}
    for id, cui in enumerate(vocab):
        cui_to_id[cui] = id
        id_to_cui[id] = cui
    for cui, mention in vocab.items():
        vocab_entity_id_mentions[cui_to_id[cui]] = mention

    vocab_mentions, vocab_ids = [], []
    for id, mentions in vocab_entity_id_mentions.items():
        vocab_mentions.extend(mentions)
        vocab_ids.extend([id]*len(mentions))

    test_mentions, test_cuis = [], []
    with open('./data/biomedical/'+dataName+'/'+config['train']['test_set']+'/0.concept') as f:
        for line in f:            
            test_cuis.append(line.strip().split('||')[-1])
            test_mentions.append(line.strip().split('||')[-2].lower())
    
    num_sample_per_class = int(config['data']['group_size'])  # samples in each group
    batch_size = int(config['train']['batch_size']) # number of groups, effective batch_size for computing triplet loss = batch_size * num_sample_per_class
    margin = int(config['model']['margin'])
    epochs = int(config['train']['epochs'])
    lr = float(config['train']['lr'])
    MODEL_NAME = config['model']['model_name']

    trainDataLoader = train_dataloader(vocab_entity_id_mentions, num_sample_per_class, rank, world_size, batch_size, pin_memory=False, num_workers=0)
    # test_dataloader = test_dataloader(test_mentions, batch_size=200)

    tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
    model = Model(MODEL_NAME).to(rank)
    optimizer = torch.optim.AdamW(model.parameters(), lr=lr)
    ddp_model = DDP(model, device_ids=[rank], output_device=rank, find_unused_parameters=True)
    
    best = 0
    if rank == 0:
        logging.info(f'epochs:{epochs} group_size:{num_sample_per_class} batch_size:{batch_size} %num:1 device:{torch.cuda.get_device_name()} count:{torch.cuda.device_count()} base:{MODEL_NAME}' )

    for epoch in tqdm(range(epochs)):
        trainDataLoader.sampler.set_epoch(epoch)
        train(rank, epoch, epochs, trainDataLoader, ddp_model, optimizer, tokenizer, margin)
        # if rank == 0 and epoch % 2 == 0:
        if rank == 0:
            res = eval(rank, vocab_mentions, vocab_ids, test_mentions, test_cuis, id_to_cui, ddp_model.module, tokenizer)
            logging.info(f'{epoch} {res}')
            if res[0] > best:
                best = res[0]
                save_checkpoint(ddp_model.module, res, epoch, dataName)
        dist.barrier() 
    cleanup()

if __name__ == '__main__':
    import configparser
    config = configparser.ConfigParser()
    config.read('config.ini')
    world_size = torch.cuda.device_count()
    print(f"You have {world_size} GPUs.")
    mp.spawn(
        main,
        args=(world_size, config),
        nprocs=world_size,
        join=True
    )