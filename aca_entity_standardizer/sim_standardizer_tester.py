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


import os
import configparser
from sim_applier import sim_applier

config_obj = configparser.ConfigParser()
config_obj.read("./config.ini")


if __name__ == '__main__':
      
    model_path=config_obj["model"]["model_path"]
         
    sim_applier=sim_applier(model_path)
      
    tech_stack = "Windows, WebSphere App Server"

    tech_sim_scores=sim_applier.tech_stack_standardization(tech_stack)
    
    print("input tech_stack:", tech_stack)
    print("tech_sim_scoes:",tech_sim_scores)
    print("***************")
    
    tech_stack = "Linux"

    tech_sim_scores=sim_applier.tech_stack_standardization(tech_stack)
    
    print("input tech_stack:", tech_stack)
    print("tech_sim_scoes:",tech_sim_scores)
    print("***************")
    
    tech_stack = "c"

    tech_sim_scores=sim_applier.tech_stack_standardization(tech_stack)
    
    print("input tech_stack:", tech_stack)
    print("tech_sim_scoes:",tech_sim_scores)
    print("***************")
    
    tech_stack = "c#"

    
    tech_sim_scores=sim_applier.tech_stack_standardization(tech_stack)
    
    print("input tech_stack:", tech_stack)
    print("tech_sim_scoes:",tech_sim_scores)
    print("***************")
    
    tech_stack = "c++"

    tech_sim_scores=sim_applier.tech_stack_standardization(tech_stack)
    
    print("input tech_stack:", tech_stack)
    print("tech_sim_scoes:",tech_sim_scores)
    print("***************")
    
    tech_stack = "c-sharp"

    tech_sim_scores=sim_applier.tech_stack_standardization(tech_stack)
    
    print("input tech_stack:", tech_stack)
    print("tech_sim_scoes:",tech_sim_scores)
    print("***************")
    
  
    tech_stack = ".net"

    tech_sim_scores=sim_applier.tech_stack_standardization(tech_stack)
    
    print("input tech_stack:", tech_stack)
    print("tech_sim_scoes:",tech_sim_scores)
    print("***************")
    
    
    tech_stack = "Windows 2012"

    tech_sim_scores=sim_applier.tech_stack_standardization(tech_stack)
    
    print("input tech_stack:", tech_stack)
    print("tech_sim_scoes:",tech_sim_scores)
    print("***************")
   
    
    
    
