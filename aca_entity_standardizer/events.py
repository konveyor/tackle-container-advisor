import json
import sys
from datetime import datetime

if __name__ == '__main__':
    try:
        events = json.loads(sys.argv[1])
        date   = events["head_commit"]["timestamp"].split('T')[0]
        url    = events["head_commit"]["url"]
    except Exception as e:
        date   = datetime.today().strftime('%Y-%m-%d')
        url    = ""
        print("Exception = ", e)

    print("----------- COPY MESSAGE BELOW AND PASTE INTO README -------------")
    print("")
    print("")
    print(f"### {date} ([View diff]({url}))")
