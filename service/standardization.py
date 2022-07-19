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
import logging
import configparser
import re
import numpy as np
from word2number import w2n

from entity_standardizer.tfidf import TFIDF
from entity_standardizer.tfidf import utils
from service.version_detector import version_detector
from service.utils import Utils

version_suffixes = ['4gl' 'ambrai' 'ansi' 'arc' 'bbn' 'beta' 'cal' 'chez' 'chicken' 'clojure'
 'cloud' 'common' 'distributed' 'dolphin' 'domain' 'dylan' 'embedded'
 'enterprise' 'erlang' 'es' 'euLisp' 'express' 'extended' 'flavored'
 'franz' 'free' 'game' 'gnu' 'goal' 'hpe' 'hy' 'ikarus' 'in' 'iseries'
 'jdk' 'le' 'lfe' 'little' 'lswsvision' 'machine' 'me' 'mq' 'mqseries'
 'mt' 'nil' 'nonstop' 'nt' 'object' 'on' 'oriented' 'pdst' 'pocket'
 'portable' 'preview' 'progress' 'public' 'quicknet' 'racket' 'resilient'
 'scheme' 'sefun' 'server' 'siod' 'skill' 'slate' 'smalltalk' 'sp' 'sparc'
 'squat' 'squeak' 'standard' 'strong' 'studio' 'suse' 'susie' 'talks'
 'transfer' 'turbo' 'txr' 'vista' 'visualage' 'visualworks' 'vmx' 'x' 'xe'
 'xoku' 'xp']

def is_version(s):

    try:
        w2n.word_to_num(s)
        return True
    except:
        return s.replace('.', '').isdigit() or \
               len(re.findall('(\d+(st|nd|rd|th))', s.lower())) > 0 or \
               len(re.sub("[^0-9]", "", s)) > len(s) / 3

def intersection(lst1, lst2):
    return list(set(lst1) & set(lst2))

class Standardization():
    """
    This class for entity, version, and app standardization
    """

    def __init__(self):
        """
            Init method for Standardization Class
        """
        config = configparser.ConfigParser()
        common = os.path.join("config", "common.ini")
        kg     = os.path.join("config", "kg.ini")
        config.read([common, kg])

        try:
            kg_dir                = config["general"]["kg_dir"]
            entities_json         = config["tca"]["entities"]
            self.high_threshold   = float(config["Thresholds"]["HIGH_THRESHOLD"])
            self.medium_threshold = float(config["Thresholds"]["MEDIUM_THRESHOLD"])
            na_category           = config['NA_VALUES']['NA_CATEGORY']
            self.na_version       = config['NA_VALUES']['NA_VERSION']
            class_type_mapper     = config['filenames']['class_type_mapper']
        except KeyError as k:
            logging.error(f'{k} is not a key in your common.ini or kg.ini file.')

        self.__class_type_mapper = {}

        self.__tca_input_mapper = {
                                "application_name": "application_name",
                                "application_description": "application_description",
                                "component_name": "component_name",
                                "operating_system": "tech_stack",
                                "programming_languages": "tech_stack",
                                "middleware": "tech_stack",
                                "database": "tech_stack",
                                "integration_services_and_additional_softwares": "tech_stack",
                                "technology_summary": "tech_stack"
                            }
        
        class_type_mapper_filepath = os.path.join(kg_dir, class_type_mapper)
        if os.path.exists(class_type_mapper_filepath):
            with open(class_type_mapper_filepath, 'r') as f:
                self.__class_type_mapper = json.load(f)            
        else:
            self.__class_type_mapper = {}
            logging.error(f'class_type_mapper[{class_type_mapper_filepath}] is empty or not exists')

        if len(self.__tca_input_mapper) == 0 or len(self.__class_type_mapper) == 0:
            logging.error('ontologies init failed')

        # Check that kg contains entities file
        entity_file_name = os.path.join(kg_dir, entities_json)
        if not os.path.isfile(entity_file_name):
            logging.error(f"Entities json file {entity_file_name} does not exist. Run kg generator to create this file.")

        # Get mapping of entity id to entity names
        with open(entity_file_name, 'r', encoding='utf-8') as entity_file:
            entities = json.load(entity_file)
        
        self.__entity_data = {}
        for idx, entity in entities["data"].items():
            entity_name = entity["entity_name"] 
            tca_id      = entity["entity_id"]
            entity_type_name = entity["entity_type_name"]
            self.__entity_data[tca_id] = (entity_name, entity_type_name)

    def remove_scores(self, apps):
        for app in apps:
            for k in app.keys():
                if type(app[k]) is dict:
                    for m in app[k].keys():
                        app[k][m] = {key: val for key, val in app[k][m].items() if key != 'score'}

        return apps

    def entity_standardizer(self, mention_data):
        """
        Invokes detect_access_token for accesstoken validation and if it's valid, it will call
        entity_standardizer to get standardized name and type.
        """
        try:
            mentions = {}  # Holds all mentions as pointers to unique mention
            menhash  = {}  # Maps mention string to unique mention id
            uniques  = {}  # Holds unique mentions
            appid    = {}  # Holds mapping of mention_id -> app_id 
            for mention in mention_data:        
                app_id     = mention.get("app_id", None)    
                mention_id = mention.get("mention_id", None)
                mention_name = mention.get("mention", "")

                if mention_name.lower() not in ['na', 'null', 'string', 'none']:
                    appid[mention_id] = app_id

                    if mention_name in menhash:
                        mentions[mention_id] = uniques[menhash[mention_name]]
                    else:
                        ulen                  = len(uniques)
                        menhash[mention_name] = ulen
                        uniques[ulen] = {"mention": mention_name}
                        mentions[mention_id] = uniques[ulen]

        except Exception as e:
            logging.error(str(e))
            track = traceback.format_exc()
            return dict(status = 400,message = 'Input data format doesn\'t match the format expected by TCA'), 400

        if not uniques:
            dict(status=201, message="Entity standardization completed successfully!", result=list(mentions.values())), 201

        infer_data = {"label_type": "int", "label": "entity_id", "data_type": "strings", "data": uniques}

        tfidf            = TFIDF("deploy")
        tfidf_start      = time.time()
        tfidf_data       = tfidf.infer(infer_data)
        tfidf_end        = time.time()
        # tfidf_time       = (tfidf_end-tfidf_start)
        # entities         = {}
        mention_data     = tfidf_data.get("data", {})


        for idx, mention in mention_data.items():
            mention_name= mention.get("mention", "")
            predictions = mention.get("predictions", [])
            if not predictions:            
                logging.info(f"No predictions for {mention}")
                continue
            entity_names= [self.__entity_data[p[0]][0] for p in predictions if p[1] > self.medium_threshold]
            entity_types= [self.__entity_data[p[0]][1] for p in predictions if p[1] > self.medium_threshold]
            conf_scores = [round(p[1],2) for p in predictions if p[1] > self.medium_threshold]
            mention["entity_names"] = entity_names
            versions    = []
            for entity, score in zip(entity_names, conf_scores):
                version  = self.version_standardizer(mention_name, [entity, score])
                versions.append(version)
                # if version[1] == self.na_version:
                #    versions.append('')
                # else:
                #    versions.append(version[1])
            mention["entity_types"] = entity_types
            mention["confidence"]   = conf_scores
            mention["versions"]     = versions
            del mention["predictions"]

        import copy
        for idx in mentions:
            mentions[idx] = copy.deepcopy(mentions[idx])
            mentions[idx]["mention_id"] = idx
            if appid[idx] is not None:
                mentions[idx]["app_id"] = appid[idx]

        return list(mentions.values())

    def version_standardizer(self, mention, entity):
        vd = version_detector()
        version = vd.get_version_strings(mention.lower())
        std_version = vd.get_standardized_version(vd, entity, version)
        final_version = (version,std_version)
        if std_version != self.na_version:
            logging.debug(f"Mention = {mention}, Entity = {entity}, Version = {version}, Std. version = {std_version}")
        return final_version



    def remove_redundant_mentions(self, app_data):

        app_keys = ['Runlib', 'Runtime', 'OS', 'Lib', 'App Server', 'Lang', 'App', 'VM', 'Storage', 'Plugin', 'HW', 'Technology']

        for app in app_data:

            #  remove mention_id
            for k in app.keys():
                if type(app[k]) is dict:
                    for m in app[k].keys():
                        app[k][m] = {key: val for key, val in app[k][m].items() if key != 'mention_id'}

            used_mentions = ""
            used_mentions_general = ""
            words_to_entities = {}
            for k in app_keys:
                if k in app:
                    for m in app[k]:
                        used_mentions = used_mentions + ' ' + str(m)
                        used_mentions_general = used_mentions_general + ' ' + str(m)
                        words = m.split(' ')
                        for w in words:
                            if w in words_to_entities:
                                words_to_entities[w]['entities'].append(m)
                                words_to_entities[w]['scores'].append(app[k][m]['score'])
                            else:
                                words_to_entities[w] = {'entities': [m], 'scores': [app[k][m]['score']]}


            used_mentions = np.unique(np.array(used_mentions.split(' '))).tolist()
            if '' in used_mentions:
                used_mentions.remove('')

            # low medium confidence
            if 'low_medium_confidence' in app:

                low_mentions = []
                low_mentions_count = []
                for lmc in app['low_medium_confidence']:
                    m = lmc.split(' ')
                    low_mentions.append(m)
                    low_mentions_count.append(len(m))

                to_remove = []
                for i, lmc in enumerate(app['low_medium_confidence']):
                    for t in lmc.split(' '):
                        if t in used_mentions:
                            if lmc not in to_remove:
                                to_remove.append(lmc)
                                break

                        for j, m in enumerate(low_mentions):
                            if j != i:
                                if t in m and low_mentions_count[i] <= low_mentions_count[j]:
                                    if lmc not in to_remove:
                                        to_remove.append(lmc)
                                        break

                if len(to_remove) > 0:
                    for t in to_remove:
                        app['low_medium_confidence'].pop(t)

                if bool(app['low_medium_confidence']) is False:
                    app.pop('low_medium_confidence')

            # unknown
            if 'unknown' in app:
                app['unknown'] = np.unique(np.array(app['unknown'])).tolist()
                unknown_mentions = []
                unknown_mentions_count = []
                for u in app['unknown']:
                    m = u.split(' ')
                    unknown_mentions.append(m)
                    unknown_mentions_count.append(len(m))

                to_remove = []
                for i, u in enumerate(app['unknown']):
                    for t in u.split(' '):
                        if t in used_mentions:  # used_mentions_general
                            if u not in to_remove:
                                to_remove.append(u)
                                break

                        remove = False
                        for j, m in enumerate(unknown_mentions):
                            if j != i:
                                if t in m and unknown_mentions_count[i] < unknown_mentions_count[j]:
                                    remove = True
                                    break

                        if remove is True:
                            if u not in to_remove:
                                to_remove.append(u)
                                break

                if len(to_remove) > 0:
                    for t in to_remove:
                        app['unknown'].remove(t)

                if app['unknown'] == []:
                    app.pop('unknown')

            # regular keys
            m_to_remove = []
            m_to_keep = []
            for m in used_mentions:
                if m in words_to_entities:
                    if len(words_to_entities[m]['entities']) > 1:
                        ind = np.argsort(np.array(words_to_entities[m]['scores']))[::-1]
                        m_to_keep.append(words_to_entities[m]['entities'][ind[0]])
                        for i in ind[1:]:
                            m_to_remove.append(words_to_entities[m]['entities'][i])
                    elif len(words_to_entities[m]['entities']) == 1:
                        m_to_keep.append(words_to_entities[m]['entities'][0])


            if len(m_to_remove) > 0:
                for m in m_to_remove:
                    if m not in m_to_keep:
                        for k in app_keys:
                            if k in app:
                                if m in app[k]:
                                    app[k].pop(m)


        return app_data

    def remove_stopwords(self, s):
        stop_words = [" of ", " for ", " on ", " in ", " no ", "unknown", "none", " as ", "string", " id ", \
                      "version", "edition", " a ", " by ", " if ", "other"]
        for w in stop_words:
            s = re.sub(w, ' ', s, flags=re.IGNORECASE)

        return s

    def select_mentions(self, mentions):

        # group mentions by app
        res = {}
        for v in mentions:
            if v['app_id'] not in res.keys():
                res[v['app_id']] = []

            res[v['app_id']].append(v)

        # loop over apps
        m_to_keep = []
        for app in res:
            mentions = res[app]
            used_mentions = ""
            words_to_entities = {}

            # build list of possible entities/mentions per mention word
            for m in mentions:
                if 'combo_id' not in m.keys():
                    m['combo_id'] = m['mention_id']
                if len(m['entity_names']) > 0:
                    words = str(m['mention']).split(' ')

                    for w in words:
                        used_mentions = used_mentions + ' ' + w + '_' + str(m['combo_id'])
                        w_id = w + '_' + str(m['combo_id'])
                        if w_id in words_to_entities:
                            words_to_entities[w_id]['entities'].append(m)  # m['entity_names'][0]
                            words_to_entities[w_id]['scores'].append(m['confidence'][0])
                        else:
                            words_to_entities[w_id] = {'entities': [m],
                                                    'scores': [m['confidence'][0]]}  # m['entity_names'][0]
                else:
                    m_to_keep.append(m)


            used_mentions = np.unique(np.array(used_mentions.split(' '))).tolist()
            if '' in used_mentions:
                used_mentions.remove('')


            for m in used_mentions:
                ind = np.argsort(np.array(words_to_entities[m]['scores']))[::-1]
                if words_to_entities[m]['entities'][ind[0]] not in m_to_keep:
                    m_to_keep.append(words_to_entities[m]['entities'][ind[0]])

        return m_to_keep



    def compute_combinations(self, tech_stack):
        """Split the text with white space delimiter compute all combinations of words"""
        try:
            limit = 6

            text0 = tech_stack
            tech_list0 = text0.split(" ")

            if len(tech_list0) > 1:

                tech_list = []
                for i, each in enumerate(tech_list0):
                    if is_version(tech_list0[i]):
                        continue

                    tech_list.append(each)
                    if i < len(tech_list0) - 1:
                        for j in range(i + 1, min(i + limit, len(tech_list0))):
                            if is_version(tech_list0[j]):
                                tech_list[-1] = ' '.join(tech_list0[i:j + 1])
                            else:
                                tech_list.append(' '.join(tech_list0[i:j + 1]))
                            if is_version(tech_list0[j]) and j < min(i + limit, len(tech_list0))-1 and tech_list0[j+1] not in version_suffixes:
                                break

            else:
                tech_list = tech_list0

            return tech_list

        except Exception as e:
            logging.error(str(e))

    
    def app_standardizer(self, app_data):
        """
        app_standardizer methods takes app_data as input, extracts mentions for entity and
        version standardization followed by assessment of high, low, medium confidence and
        unknown technology data predictions
        """                
        if (not app_data)  or len(app_data) == 0:
            return app_data

        general_term_key = 'Technology'

        mentions = []
        id_to_app = {}
        mentions_to_combos = {}
        num_combo = 0

        for idx, app in enumerate(app_data):
            id_to_app[idx] = app

            tech_stack = ''
            for header in app:

                if self.__tca_input_mapper.get(header, 'NA') == 'tech_stack' and app[header] and str(app[header]).lower() not in ['na', 'null', 'string', 'none']:
                    component_string = str(app[header])
                    component_string = self.remove_stopwords(component_string)

                    if tech_stack:
                        tech_stack = tech_stack + ', ' + component_string
                    else:
                        tech_stack = component_string

            if not tech_stack:
                continue

            tech_stack = Utils.preprocess_tech_stack_for_sim(tech_stack)
            app_mentions = utils.preprocess(tech_stack)

            # split each mention into combination of words
            for m in app_mentions:
                combos = self.compute_combinations(m)

                for c in combos:
                    num_mentions = len(mentions)
                    mentions.append({"app_id": idx, "mention_id": num_mentions, "mention": c, "combo_id": num_combo})
                    mentions_to_combos[num_mentions] = num_combo

                num_combo += 1


            app["KG Version"] = self.__class_type_mapper['kg_version']
            for x in set(self.__class_type_mapper['mappings'].values()):
                app[x] = {}


        # standardize mentions
        std_mentions = self.entity_standardizer(mentions)

        # add back combos after standardization
        for m in std_mentions:
            m["combo_id"] = mentions_to_combos[m['mention_id']]

        valid_mentions = self.select_mentions(std_mentions)

        for mention_data in valid_mentions:

            if 'entity_names' not in mention_data.keys():
                continue

            mention     = mention_data["mention"]
            app_id      = mention_data["app_id"]
            entity_names= mention_data["entity_names"]
            # entity_types= mention_data["entity_types"]
            conf_scores = mention_data["confidence"]
            versions    = mention_data["versions"]
            app         = id_to_app[app_id]

            low_medium_confidence = app.get('low_medium_confidence', {})
            unknown               = app.get('unknown', [])
            mention_id = mention_data["mention_id"]

            if len(entity_names) >= 1:
                entity = entity_names[0]
                score = conf_scores[0]
                version = versions[0]

                mention_words = mention.split(' ')
                if self.__class_type_mapper['mappings'][entity] == general_term_key:
                    ## Technology
                    insert = False
                    found = False
                    m_to_remove = []
                    for m in app[general_term_key]:
                        if entity.split('|')[0] == list(app[general_term_key][m].keys())[0].split('|')[0] and\
                                len(intersection(m.split(' '),mention_words)) > 0  and \
                                mentions_to_combos[mention_id] == mentions_to_combos[app[general_term_key][m]['mention_id']]: # .split('|')[0] .split('|')[0]

                            if (app[general_term_key][m]['score'] < score and \
                                len(mention) > len(m)) or \
                                    (abs(app[general_term_key][m]['score'] - score) < 0.1 and (
                                             len(mention) > len(m)) or \
                                     (mention.split(' ')[-1].replace('.', '').isdigit() and not m.split(' ')[
                                         -1].replace('.', '').isdigit())):

                                insert = True
                                m_to_remove.append(m)
                            else:
                                found = True

                    if len(m_to_remove) > 0:
                        for m in m_to_remove:
                            app[general_term_key].pop(m)

                    if found is False or insert is True:

                        if mention not in app[general_term_key]:
                            app[general_term_key][mention] = {}
                        app[general_term_key][mention][entity] = version
                        app[general_term_key][mention]['score'] = score
                        app[general_term_key][mention]['mention_id'] = mention_id
                else:
                    if score >= self.high_threshold:
                        if mention not in app[self.__class_type_mapper['mappings'][entity]]:
                            insert = False
                            found = False
                            m_to_remove = []

                            for m in app[self.__class_type_mapper['mappings'][entity]]:

                                if entity.split('|')[0] == list(app[self.__class_type_mapper['mappings'][entity]][m].keys())[0].split('|')[0] and \
                                        len(intersection(m.split(' '),mention_words)) > 0 and \
                                        mentions_to_combos[mention_id] == mentions_to_combos[app[self.__class_type_mapper['mappings'][entity]][m]['mention_id']]:  # .split('|')[0]  .split('|')[0]

                                    if (app[self.__class_type_mapper['mappings'][entity]][m]['score'] < score and \
                                        len(mention) > len(m) )  or \
                                            (abs(app[self.__class_type_mapper['mappings'][entity]][m]['score'] - score) < 0.1 and (
                                                    len(mention) > len(m)) or \
                                             (mention.split(' ')[-1].replace('.', '').isdigit() and not m.split(' ')[
                                                 -1].replace('.', '').isdigit())):

                                        insert = True
                                        m_to_remove.append(m)
                                    else:
                                        found = True

                            if not found or insert is True:
                                if len(m_to_remove) > 0:
                                    for m in m_to_remove:
                                        app[self.__class_type_mapper['mappings'][entity]].pop(m)

                                app[self.__class_type_mapper['mappings'][entity]][mention] = {}
                                app[self.__class_type_mapper['mappings'][entity]][mention][entity] = version
                                app[self.__class_type_mapper['mappings'][entity]][mention]['score'] = score
                                app[self.__class_type_mapper['mappings'][entity]][mention]['mention_id'] = mention_id
                                # break
                    else:
                        # low or medium confidence
                        if mention not in low_medium_confidence:
                            low_medium_confidence[mention] = {}
                        low_medium_confidence[mention][entity] = version
                        low_medium_confidence[mention]['score'] = score

            elif len(entity_names) == 0:
                unknown.append(mention)

            if low_medium_confidence:
                app['low_medium_confidence'] = low_medium_confidence
            if unknown:
                app['unknown'] = unknown

        # remove redundant mentions and entity matching scores
        app_data = self.remove_redundant_mentions(app_data)
        app_data = self.remove_scores(app_data)

        return app_data
