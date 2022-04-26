import json
import sys

def main():
    lines = list()
    for line in sys.stdin:
        if not line.startswith('>'): # only need tracing output
            continue
        line = line.replace(">", "")
        line = json.loads(line)
        # print(line)
        lines.append(line)
    prog = {'functions' : [{"name" : "main", "instrs" : lines}]}
    print(json.dumps(prog, indent=2))

if __name__ == "__main__":
    # parser = argparse.ArgumentParser()
    # parser.add_argument('-f', dest='filename', 
    #                     action='store', type=str, help='json file')
    # args = parser.parse_args()
    main()