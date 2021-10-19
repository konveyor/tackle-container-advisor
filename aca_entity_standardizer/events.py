import json
import sys

if __name__ == '__main__':
    try:
        events = json.loads(sys.argv[1])
    except Exception as e:
        print("Exception = ", e, sys.argv[1])
   
    print(events["head_commit"]["timestamp"], events["head_commit"]["url"])