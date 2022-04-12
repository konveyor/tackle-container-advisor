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


from collections import defaultdict
import re
import logging

logger = logging.getLogger('tfidf')
logger.setLevel(logging.INFO)

class utils:

    @staticmethod
    def remove_duplicate(old_list):
        """Removes the duplicate elements present in the input list"""
        list1 = []

        try:
            for element in old_list:
                if element.strip() and (element.strip() not in list1):
                    list1.append(element.strip())
            return list1
        except Exception as e:
            logger.error(str(e))
        
    @staticmethod
    def remove_duplicate_tuple(old_list):
        """ Removes the duplicate elements which belongs to same category in the input list"""
        list1 = []
        category_list=[]
         
        try:
            for element in old_list:
                category, sim = element
                if (category not in category_list):
                    list1.append(element)
                    category_list.append(category)

            return list1
        except Exception as e:
            logger.error(str(e))
    
     
    @staticmethod
    def split_subtext(text):
        """
        Formats the input text based on predefined split_list, keep_list values
        """
        try:
            split_list = (
            "other -  ", ":", "        ", "~", "ibm - ibm", ";", "....", "    ", " and ", "\t", "\n", "\r", " / ",
            "   ", "  ", "/", "&")  # ,#," - ", ) tomcat 3/4/5/6/7,cobol/c/c++/vb/java/c#
            keep_list = ("/os", "os/", "PL/", "I/O", "n/a", "pi/po", "amd/emt")
            pattern = (r'(/[0-9])+')
            stop_word_list = ("of", "for", "on", "in")

            text = text.replace("_", " ")

            text = text.replace("c#", "  c#  ")

            text = text.replace("jquery", "  jquery")

            # print("subtext input:",text)
            text = text.strip()
            text = text.strip("\(")
            text = text.strip("\)")
            text = text.strip("\"")

            for r in split_list:
                replaced = True

                if r == "/" and text.strip().lower().find(r) >= 0:
                    if re.search(pattern, text) != None:  # 3/4/5/6/7  not replace
                        # print("not split subtext:",text)
                        replaced = False

                    for each in keep_list:

                        if text.strip().lower().find(each.strip().lower()) >= 0:
                            # print("not split subtext:",text, each)
                            replaced = False
                            break

                if replaced:
                    text = text.replace(r, ",")
                # print("split subtext /:",text)

            tech_list = text.split(",")
            return tech_list

        except Exception as e:
            logger.error(str(e))
        
    @staticmethod
    def remove_noise_snippet(text):
        """ Check if any of the values in remove_list or exact_remove_list are present in the input text"""
        try:
            remove_list = (":no", "unknown", "none", "value updated as per rule id", "string")  #

            exact_remove_list = ("n/a", "yes", "tbd", "etc", "custom", "none")  # ,"other-"),"n",
            temp = text
            if text == "" or text == " " or text == "  " or text == "(" or text == ")" or text == "\"":
                return True
            for each in remove_list:
                if text.lower().find(each.lower()) > -1:
                    return True
            text0 = text.replace(" ", "")
            for each in exact_remove_list:
                if text0.lower() == each.lower():
                    # print("remove:",text)
                    return True
            return False
        except Exception as e:
            logger.error(str(e))
        
    @staticmethod
    def my_tokenization0(text):
        """Remove the stop list words in the input text """

        try:
            # stop_flag = ['x', 'c', 'u','d', 'p', 't', 'uj', 'm', 'f', 'r']

            stop_list = ("on", "of", "for", "version", "edition")

            result = []

            words = text.split()

            for word in words:
                is_stop_word = False
                word.replace(" ", "")
                if len(word) == 0:
                    continue;

                for each in stop_list:
                    if word.strip().lower() == each:
                        is_stop_word = True
                        break
                if is_stop_word:
                    continue

                result.append(word)
            # print("words:", result)
            return result

        except Exception as e:
            logger.error(str(e))



    @staticmethod
    def replace_special_character(text):
        """ Replace special characters such as c# to c-sharp, c++ to c-plus-plus """
        try:
            text = text.lower().replace("c#", "c-sharp")
            text = text.lower().replace("c++", "c-plus-plus")
            return text

        except Exception as e:
            logger.error(str(e))
    
    @staticmethod
    def input_preprocess(text):
        """ Preprocess the input text by replacing the special characters"""

        try:
            text = utils.replace_special_character(text)

            words = text.split(" ")
            text0 = ""

            for each in words:

                if not (each.isalpha() or each.isdigit()):
                    if "." in each:  # remove version
                        each = re.sub("\d+", "", each, count=0)
                        each.replace(".", "")
                text0 = text0 + " " + each

            return text0

        except Exception as e:
            logger.error(str(e))

    @staticmethod
    def preprocess(tech_stack):
        """Split the text with comma delimiter and remove if any stop words to be removed in the subtext and remove
        duplicates"""
        try:
            text0 = tech_stack

            tech_list0 = text0.split(",")

            tech_list = []
            for each in tech_list0:
                if utils.remove_noise_snippet(each):
                    continue

                sublist = utils.split_subtext(each)

                for sub_each in sublist:
                    tech_list.append(sub_each)

            tech_list = utils.remove_duplicate(tech_list)

            return tech_list

        except Exception as e:
            logger.error(str(e))
