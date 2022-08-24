import argparse
import json
from service.standardization import Standardization
from service.assessment import Assessment
from service.planning import Plan
from service.infer_tech import InferTech
from service.clustering import Clustering

# input argument parser
def parser():
    parser = argparse.ArgumentParser(description="TCA command line: standardize applications entities and recommend container images")
    parser.add_argument("-input_json", dest="input_json", type=str, help="input json", required=True)
    parser.add_argument("-operation", dest="operation", type=str, default="standardize", help="operation to perform: standardize (default) | containerize | clustering")
    parser.add_argument("-output_json", dest="output_json", type=str, help="output json", required=True)
    return parser.parse_args()


# main
def main():

    # parse inputs
    args = parser()

    input_json = args.input_json
    operation = args.operation
    output_json = args.output_json

    result_data = ''

    # load json input
    with open(input_json) as fin:
        app_data = json.load(fin)

    # entity standardization
    if operation == 'standardize':
        standardizer = Standardization()
        result_data = standardizer.app_standardizer(app_data)

        assessment = Assessment()
        result_data = assessment.app_validation(result_data)
        result_data = assessment.output_to_ui_assessment(result_data)


    elif operation == 'containerize':
        plan = Plan()
        inferTech  = InferTech()

        result_data = plan.ui_to_input_assessment(app_data)
        result_data = inferTech.infer_missing_tech(result_data)
        result_data = plan.validate_app(result_data)
        result_data = plan.map_to_docker(result_data, 'docker')
        result_data = plan.output_to_ui_planning(result_data)

    elif operation == 'clustering':
        cluster = Clustering()
        result_data = cluster.output_to_ui_clustering(app_data)

    else:
        print('invalid operation')

    # print(result_data)
    # print(type(result_data[0]['num_elements']))
    # for r in result_data:
    #     r['num_elements'] = int(r['num_elements'])

    # save json output
    if result_data != '':
        with open(output_json, "w") as fot:
             json.dump(result_data, fot, indent=4)


if __name__ == "__main__":
    main()