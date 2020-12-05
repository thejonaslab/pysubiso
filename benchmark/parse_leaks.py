import sys

logfile = sys.argv[1]

lines = open(logfile, 'r').readlines()

lines = [l.strip() for l in lines]
