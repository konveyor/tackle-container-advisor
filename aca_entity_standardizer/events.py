import json
import sys

if __name__ == '__main__':
    try:
        events = json.loads(sys.argv[1])
    except Exception as e:
        print(sys.argv[1])
