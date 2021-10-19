import json
import sys

if __name__ == '__main__':
    events = json.loads(sys.argv[1])
    print(events)    