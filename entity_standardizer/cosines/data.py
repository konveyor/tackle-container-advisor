import random
def generate_train_entity_sets(entity_id_mentions, entity_id_name=None, group_size=10, anchor=False):
    # split entity mentions into groups
    # anchor = False, don't add entity name to each group, simply treat it as a normal mention
    entity_sets = []
    if anchor:
        for id, mentions in entity_id_mentions.items():
            mentions = list(mentions)
            random.shuffle(mentions)
            positives = [mentions[i:i + group_size] for i in range(0, len(mentions), group_size)]
            anchor_positive = [([entity_id_name[id]]+p, id) for p in positives]
            entity_sets.extend(anchor_positive)
    else:
        for id, mentions in entity_id_mentions.items():
            if entity_id_name:
                group = list(set([entity_id_name[id]] + mentions))
            else:
                group = list(mentions)
                if len(group) == 1:
                    group.append(group[0])
                group.extend((group_size-len(group))%group_size * ['PAD'])
            random.shuffle(group)
            positives = [(group[i:i + group_size], id) for i in range(0, len(group), group_size)]
            entity_sets.extend(positives)
    return entity_sets

def batchGenerator(data, batch_size):
    for i in range(0, len(data), batch_size):
        batch = data[i:i+batch_size]
        x, y = [], []
        for t in batch:
            t[0] = [e for e in t[0] if e != 'PAD']
            x.extend(t[0])
            y.extend([t[1]]*len(t[0]))
        yield x, y