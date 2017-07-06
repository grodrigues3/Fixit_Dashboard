from csv import DictReader
import sys
import os, pdb
from collections import defaultdict
import time 
import re

def getSigList():
    with open("sigList.txt", "r") as f:
        sigSet = set([s.strip() for s in f])
    return sigSet

def parse_test_owners(k8s_root_dir, print_stats=False):
    """
    Read the test_owners file
    Return dict[string]set().  "sig name" -> "testName"
    """
    rel_file_path = "./test/test_owners.csv"
    sigMap = defaultdict(set)
    with open(os.path.join(k8s_root_dir, rel_file_path), 'r') as f:
        for i, line in enumerate(DictReader(f)):
            sigMap[line['sig']].add(line['name'])
    if print_stats:
        for sig in sorted(sigMap, key=lambda x: len(sigMap[x]),
                reverse=True):
            print sig, len(sigMap[sig])
        print sum([len(sigMap[x]) for x in sigMap]), ' total tests'
    return sigMap

def find_tests(k8s_root_dir):
    """
        find all the e2e tests in the Kubernetes directory
    """
    cmd = "go run " + os.path.join(k8s_root_dir, "test/list/main.go")
    cmd += " " + k8s_root_dir
    print cmd
    out = os.popen(cmd).readlines()
    fNames = set()
    for line in out:
        line = line.strip()[1:-1]
        tokens = line.split()
        loc = tokens[0]
        if loc.startswith(os.path.join(k8s_root_dir, "test/e2e")):
            end_ind = loc.find(":") #this gives the line where the test starts
            fNames.add(loc[:end_ind])
    if False:
        print len(fNames)
        raw_input("waiting")
        print fNames
    return fNames
   
def split_tests(testFiles):
    start = time.time()
    hasOwner, needsOwner = set(), set()
    sigs = getSigList()
    for tF in testFiles:
        with open(tF, 'r') as f:
            matcher = re.compile(r"^//\s?OWNER\s?=\s?sig/(.+)", re.MULTILINE)
            this = matcher.search(f.read())
            if this and this.groups()[0] in sigs:
                hasOwner.add(tF)
            else:
                needsOwner.add(tF)
    print "Has Owners", len(hasOwner)
    print "Needs Owners", len(needsOwner)
    print time.time() - start, ' second have elapsed'
    return hasOwner, needsOwner


def main():
    args = sys.argv
    if len(args) < 2:
        print "Provide the full path to the kubernetes root dir"
        exit()
    path = args[1]
    testFile = os.path.join(path, "test/e2e/addon_update.go") 
    tests = find_tests(path)
    #split_tests(set([testFile]))    
    split_tests(tests)    

if __name__ == "__main__":
    main()
