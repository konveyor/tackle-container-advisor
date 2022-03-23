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


class utils:


  
    @staticmethod
    def remove_non_asciichar(tech_stack):
        """
        Remove non-ascii characters

        :param tech_stack: input charaters
        :type tech_stack: string

        :returns: tech_stack , string  containing non-ascci characters
        :rtype: string

        """
        tech_stack = re.sub(r'[^\x00-\x7F]+', " ", " " + str(tech_stack) + " ").strip()
        return tech_stack

     
    @staticmethod
    def remove_duplicate(old_list):

        """
        Remove duplicate 

        :param old_list: A list of Technlogy stack and may include  OS ,APPS , APP SERVERS ,LIBS , LANG or RUNTIMES
        :type old_list: list 

    
        :returns: A single list with no duplicate
        :rtype: list
        """
      
        list1 = []
        for element in old_list:
        
            if element=="" or element==" " or element=="  ":
                continue
                
            if (element not in list1):
                list1.append(element)
        return list1
        
    
    @staticmethod
    def remove_duplicate_tuple(old_list):
        """
        Remove duplicate tuple
        :param old_list:
        :type old_list: list 
        :returns: list1
        :rtype: list
        """
        list1 = []
        category_list=[]    
        for  element in old_list: 
             category, sim=element
             if (category not in category_list):
                        list1.append(element)
                        category_list.append(category)
        
        return list1
    
    
    @staticmethod
    def split_subtext(text):

        """
        Clean input technology (OS ,APPS , APP SERVERS ,LIBS , LANG or RUNTIMES)

        :param text: String input representing a particular technology
        :type text: string

        :returns: 
        :rtype: list

        """



        split_list = ("other -  ",":", "        ","~","ibm - ibm",";","....","    "," and ", "\t","\n","\r"," / ","   ","  ","/", "&") #,#," - ", ) tomcat 3/4/5/6/7,cobol/c/c++/vb/java/c#
        keep_list=("/os","os/","PL/","I/O","n/a","pi/po","amd/emt")
        pattern=(r'(/[0-9])+')
        stop_word_list=("of","for","on","in")
        
        text=text.replace("c#","  c#  ")
        
        text=text.replace("jquery","  jquery")
        text=text.strip()
        text=text.strip("\(")
        text=text.strip("\)")
        text=text.strip("\"")
        
            
        for r in split_list:
             replaced=True
            
                 
             if r=="/" and text.strip().lower().find(r)>=0:
                if re.search(pattern, text)!=None: #3/4/5/6/7  not replace
                  
                    replaced=False
                
                for each in keep_list:
                      
                     if text.strip().lower().find(each.strip().lower())>=0:
                    
                         replaced=False
                         break
                 
                
                 
             if replaced:            
                 text = text.replace(r, ",")
              
        
        tech_list=text.split(",")
        return tech_list
        
    @staticmethod
    def remove_noise_snippet(text):
        """
        Check if  a single technology input string contains noise. 

        :param text: Technology input( OS ,APPS , APP SERVERS ,LIBS , LANG or RUNTIMES).
        :type text: string

        :returns: A boolean True or False signaling if the input text contains noise or not.
        :rtype: bool

        """
      
    
        remove_list=(":no","unknown","none", "value updated as per rule id",)#
        
        exact_remove_list=("n/a","yes","tbd", "etc","custom","none")#,"other-"),"n",
        temp=text
        if text=="" or text==" " or text=="  " or text=="(" or text==")" or text=="\"":
             return True
        
        
        for each in remove_list:
            if text.lower().find (each.lower())>0:
                 return True
                 
        text0=text.replace(" ","")
        for each in exact_remove_list:
            if text0.lower()==each.lower():
                return True
        return False
        

    
    
    @staticmethod
    def my_tokenization0(text):

         """
         Tokenize String

         :param text:
         :type text: input technology

         :returns: list of tokens
         :rtype: list 

         """
        
        # stop_flag = ['x', 'c', 'u','d', 'p', 't', 'uj', 'm', 'f', 'r'] 
         stop_list=("on","of","for","version","edition")
             
         result = []
            
         words = text.split()    
         for word in words:
                is_stop_word=False
                word.replace(" ","")
                if len(word)==0:
                     continue;
                     
                for each in stop_list:
                     if word.strip().lower()==each:
                            is_stop_word=True
                            break
                if is_stop_word: 
                    continue
                
                result.append(word)
         return result

   
    @staticmethod
    def my_tokenization0_str(text):

         """
         Removes stop words from texts. i.e : ("on","of","for","version","edition")

         :param text: keywords
         :type text: string 
         
         :returns: text
         :rtype: string
         """

       
        # stop_flag = ['x', 'c', 'u','d', 'p', 't', 'uj', 'm', 'f', 'r'] 
         stop_list=("on","of","for","version","edition")
             
         result = []
         result_str=""
            
         words = text.split()    
         
         for word in words:
                is_stop_word=False
                word.replace(" ","")
                if len(word)==0:
                     continue;
                     
                for each in stop_list:
                     if word.strip().lower()==each:
                            is_stop_word=True
                            break
                if is_stop_word: 
                    continue
                
                result.append(word)
                if result_str=="":
                    result_str=word
                else:
                    result_str+=" "+word
         return result_str


    
    @staticmethod
    def remove_low_frequency_token(texts,freq_threshold):
        
        """
        Remove words that appear only once

        :param texts: List of keywords 
        :type  texts: list

        :param freq_threshold:
        :type freq_threshold: int 

        :returns: text
        :rtype: list

        
        """
        frequency = defaultdict(int)
        for text in texts:
            for token in text:
                frequency[token] += 1

        texts = [
            [token for token in text if frequency[token] > freq_threshold]
            for text in texts
        ]
        return texts
        
    
    
   
    @staticmethod
    def replace_special_character(text):
        """
        Replace c# to c-sharp, c++ to c-plus-plus

        :param text: Raw text input
        :type  text: string

        :returns: A clean text containing no special characteres
        :rtype: string

        """
        
        text=text.lower().replace("c#","c-sharp")
        text=text.lower().replace("c++","c-plus-plus")
         
        return text
        
    
   
    @staticmethod
    def input_preprocess(text):

     """
     Preprocess input Strings

     :param text: Raw input text
     :type text: string

     :returns: Preprocessed string input
     :rtype: string
     """

        
     text=utils.replace_special_character(text) 
     
     words=text.split(" ")
     text0=""      
     for each in words:
        
        if not (each.isalpha() or each.isdigit()):
             if "." in each:    #remove version
                    each=re.sub("\d+", "", each, count=0)
                    each.replace(".","")
        text0=text0+" "+each
        
     return text0
     

    
    @staticmethod
    def preprocess (tech_stack):

        """
        Preprocess input tech_stack
        
        
        :param tech_stack: input technology names
        :type tech_stack: list

        :returns: preproccessed tech strings
        :rtype: list

        """
           
        text0 = tech_stack          
        tech_list0=text0.split(",")
             
        tech_list=[]
        for each in tech_list0:
           
            if utils.remove_noise_snippet(each):
              
                continue
            
                
            sublist=utils.split_subtext(each)
            for sub_each in sublist:
                tech_list.append(sub_each)
                    
        tech_list=utils.remove_duplicate(tech_list)   
        return  tech_list
