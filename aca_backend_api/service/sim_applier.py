# *****************************************************************
# Copyright IBM Corporation 2021
# Licensed under the Eclipse Public License 2.0, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# *****************************************************************

 
 
import string
import pickle
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity 
from pathlib import Path
import logging
import re
from service.utils_nlp import  utils
import numpy as np
import configparser

config = configparser.ConfigParser()
config.read('config.ini')
print('config',config.sections())

class sim_applier:
    def __init__(self, logger=False):
        """
        Init method for sim_applier class
        Initializes tfs,tfidf,all_instances by loading the model objects. Also, sets the default vaules for category,
        variant and all threshold variables.
        """
        logging.basicConfig(level=logging.INFO)
        
        self.all_instances=[]
        
        self.sim_threshold= float(config['Thresholds']['sim_threshold'])
        self.top= int(config['Thresholds']['top'])

        self.NA_CATEGORY=config['NA_VALUES']['NA_CATEGORY']
        self.NA_VARIANT=config['NA_VALUES']['NA_VARIANT']
        
        self.HIGH_THRESHOLD=float(config['Thresholds']['HIGH_THRESHOLD'])
        self.MEDIUM_THRESHOLD=float(config['Thresholds']['MEDIUM_THRESHOLD'])

        model_name=config['filepaths']['model_name']
        tfidf_name=config['filepaths']['tfidf_name']
        instances_name=config['filepaths']['instances_name']

        if Path(model_name).is_file():
            self.tfs = pickle.load(open(model_name, "rb"), encoding="utf8") 
        else:
            self.tfs = None
            logging.error(f'model_name file[{model_name}] is empty or not exists') 
        
        if Path(tfidf_name).is_file():
            self.tfidf=pickle.load(open(tfidf_name, "rb"), encoding="utf8") 
        else:
            self.tfidf = None
            logging.error(f'tfidf_name file[{tfidf_name}] is empty or not exists')
        
        if Path(instances_name).is_file():
            self.all_instances=pickle.load(open(instances_name, "rb"), encoding="utf8")
        else:
            logging.error(f'instances_name file[{instances_name}] is empty or not exists')
        


    def calc_CosineSimilarity(self,tfs_text):
        '''
        calc_CosineSimilarity takes the input tfs_text and calculate the cosine similarity between the input tfs_text and
        entities present in the model objects and return the sorted entity list based on similarity score
        '''

        sims=[]

        try :
           matrixValue = cosine_similarity(tfs_text, self.tfs)


           id = 0
           for each in matrixValue[0]:
               # if each>0:
               #    print ("each:",id,each)
               sims.append(np.round(each,3))
               id += 1

           sims_sorted = sorted(enumerate(sims), key=lambda item: -item[1])

           return sims_sorted

        except Exception as e:
           logging.error(str(e))


    def remove_duplicate_category(self,old_list):
        """
        remove_duplicate_category checks the category for each element in the given old_list and remove the elements
        if its respective category is already present.
        """
        list1 = []
        category_list=[]
         
        try:
            for element in old_list:
                sim_id_, sim = element

                category, variant, keywords = self.all_instances[sim_id_]
                if (category.strip() not in category_list):
                    list1.append(element)
                    category_list.append(category.strip())

            return list1

        except Exception as e:
            logging.error(str(e))

    def entity_standardization(self,id_, text):
        """
        entity_standardization preprocesses the input text and removes stop words in input text. Then it performs tfidf
        transform, find the cosinesimilarity with all the entities and remove duplicate categories. The number of
        standardized entities are added to score list based on comparison between similarity score and threshold values
        """
        try:
            text1 = utils.input_preprocess(text)

            query = utils.my_tokenization0(text1.strip().lower())

            score = []
            if query == " " or query == "":
                return score

            find = False

            sims = []
            if len(query) > 0:

                tfs_text = self.tfidf.transform([text1])
                sims = self.calc_CosineSimilarity(tfs_text)

                if len(sims) > 0:
                    i = 0

                    sims1 = self.remove_duplicate_category(sims)

                    top = 1
                    sim_id_, similarity = sims1[i]
                    if similarity >= self.HIGH_THRESHOLD:
                        top = 1
                    elif similarity >= self.MEDIUM_THRESHOLD:
                        top = 3
                    else:
                        top = 2

                    while i < top:
                        sim_id_, similarity = sims1[i]

                        if similarity <= self.sim_threshold:
                            score.append([id_, text, self.NA_CATEGORY, self.NA_VARIANT, 0])
                            break

                        category, variant, keywords = self.all_instances[sim_id_]
                        score.append([id_, text, category, keywords, similarity])

                        i += 1

            return score

        except Exception as e:
            logging.error(str(e))
      


    def tech_stack_standardization(self,tech_stack):
        """
        tech_stack_standardization splits the input text with comma delimiter, remove duplicates in the splitted text,
        remove the predefined stop words and invoke entity_standardization function
        """
        id_=0
  
    
        text0 = tech_stack
       
        try:
            tech_list0 = text0.split(",")
            tech_list0 = utils.remove_duplicate(tech_list0)

            tech_list = []
            for each in tech_list0:
                if utils.remove_noise_snippet(each):
                    continue

                sublist = utils.split_subtext(each)

                for sub_each in sublist:
                    tech_list.append(sub_each)
                    x = re.search(r"(\w+)\s+\d+\.*\d*", sub_each)
                    if x and len(x.groups()) >= 1:
                        tech_list.append(x.group(1))


            tech_scores_sim = []
            category_list = ""

            tech_list0 = tech_list
            tech_list = utils.remove_duplicate(tech_list)

            for each in tech_list:

                if each == "" or each == " " or each == "  " or each.isdigit():
                    continue

                if utils.remove_noise_snippet(each):
                    continue

                if each != "":
                    scores = self.entity_standardization(id_, each)

                    for each in scores:
                        id_, query_text, category, keywords, max_sim = each

                        if category != self.NA_CATEGORY:
                            tech_scores_sim.append([category, max_sim])


                if len(tech_scores_sim) == 0:
                    tech_scores_sim.append([self.NA_CATEGORY, self.sim_threshold])


            tech_scores_sim = sorted(tech_scores_sim, reverse=True, key=lambda x: x[1])

            tech_scores_sim_final = utils.remove_duplicate_tuple(tech_scores_sim)


            return tech_scores_sim_final

        except Exception as e:
            logging.error(str(e))

