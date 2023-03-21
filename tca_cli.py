import sys
# sys.path.append('/app')

import argparse
import json
import time
from service.standardization import Standardization
from service.assessment import Assessment
from service.planning import Plan
from service.infer_tech import InferTech
from service.clustering import Clustering

# input argument parser
def parser():
    parser = argparse.ArgumentParser(description="TCA command line: standardize applications entities and recommend container images")
    parser.add_argument("-input_json", dest="input_json", type=str, help="input json", required=False)
    parser.add_argument("-input_string", dest="input_string", type=str, help="input string", required=False)
    parser.add_argument("-operation", dest="operation", type=str, default="standardize", help="operation to perform: standardize (default) | containerize | clustering | all | standardize+containerize | standardize+clustering | containerize+clustering ")
    parser.add_argument("-output_json", dest="output_json", type=str, help="output json", required=False)
    parser.add_argument("-catalog", dest="catalog", type=str, help="catalog", default="ibmcloud", required=False)
    return parser.parse_args()


# main
def main():

    # parse inputs
    args = parser()

    input_json = args.input_json
    operation = args.operation
    output_json = args.output_json

    #input_string = "[{\"application_name\": \"app1\", \"application_description\": \"my application\", \"technology_summary\": \"rhel,db2,java\"}]"
    input_string = args.input_string
    if input_string != None:
        input_string = "[{" + input_string + "}]";

    if input_json == None and input_string == None:
        print("Provide -input_json or -input_string")
        exit()

    # load input
    if (input_json != None):
        with open(input_json) as fin:
            app_data = json.load(fin)
            #print(app_data)
    elif (input_string != None):
        app_data = json.loads(input_string)
        # print(type(app_data))

    oplist = []

    if operation == 'all':
        oplist.append('standardize')
        oplist.append('containerize')
        oplist.append('clustering')
    elif operation == 'standardize+containerize':
        oplist.append('standardize')
        oplist.append('containerize')
    elif operation == 'standardize+clustering':
        oplist.append('standardize')
        oplist.append('clustering')
    elif operation == 'containerize+clustering':
        oplist.append('containerize')
        oplist.append('clustering')
    else:
        oplist.append(operation)

    result_list = {}

    # start_time = time.time()
    for op in oplist:

        result_data = ''

        # entity standardization
        print("Invoking TCA for op: ", op)
        if op == 'standardize':
            standardizer = Standardization()
            result_data = standardizer.app_standardizer(app_data)
            assessment = Assessment()
            result_data = assessment.app_validation(result_data)
            result_data = assessment.output_to_ui_assessment(result_data)


        elif op == 'containerize':
            plan = Plan(catalog="ibmcloud")
            inferTech  = InferTech()

            result_data = plan.ui_to_input_assessment(app_data)
            
            result_data = inferTech.infer_missing_tech(result_data)
            #print(json.dumps(result_data, indent=4))
            result_data = plan.validate_app(result_data)
            
            result_data = plan.map_to_docker(result_data, 'ibmcloud')
            

            result_data = plan.output_to_ui_planning(result_data)
           

        elif op == 'clustering':
            cluster = Clustering()
            result_data = cluster.output_to_ui_clustering(app_data)

        else:
            print('invalid operation')

        result_list[op] = result_data
        if 'standardize' in result_list:
            app_data = result_list['standardize']

    # save json output
    result_data_final = ''
    if len(oplist) > 1:
        result_data_final = result_list
    else:
        result_data_final = result_list[operation]

    if result_data_final != '':
        if output_json != None:
            with open(output_json, "w") as fot:
                 json.dump(result_data_final, fot, indent=4)
        else:
            if operation == "standardize+containerize":
                result_data_final_str = "^^^" + json.dumps(result_data_final) + "$$$"
                print(result_data_final_str)

    # end_time = time.time()
    # tot_time = end_time - start_time
    # print("Total time: ", tot_time)

if __name__ == "__main__":
    main()
