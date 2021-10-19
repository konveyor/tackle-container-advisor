import json
import sys

if __name__ == '__main__':
    try:
        events = json.loads(sys.argv[1])
    except Exception as e:
        print("Exception = ", e, sys.argv[1])
   
    date = events["head_commit"]["timestamp"].split('T')[0]
    url  = events["head_commit"]["url"]
    print(f"### {date}, [changes]({url})")