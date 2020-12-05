import sys

logfile = sys.argv[1]
tgt_pattern = sys.argv[2]

lines = open(logfile, 'r').readlines()

lines = [l.strip() for l in lines]

leaks = []
lpos = 0

tgt_file = 'rimatch.cc'

while lpos < len(lines):
    if 'SUMMARY' in lines[lpos]:
        print(lines[lpos])
        break    
    elif 'leak' in lines[lpos] :
        leakset = []

        while len(lines[lpos]) > 0:
            leakset.append(lines[lpos])
            lpos += 1
        leaks.append(leakset)

              
    lpos +=1

print("there are ", len(leaks), "leaks")
leaks_that_match = []
for l in leaks:
    leak_str = "\n".join(l)
    if tgt_pattern in leak_str:
        print(leak_str)
        leaks_that_match.append(l)

print("there are", len(leaks_that_match), "matching leaks")
