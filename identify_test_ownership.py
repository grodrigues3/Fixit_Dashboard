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
    # just reuse the existing tooling that test infra wrote to get all tests
    cmd = "go run " + os.path.join(k8s_root_dir, "test/list/main.go")
    cmd += " " + k8s_root_dir
    out = os.popen(cmd).readlines()

    
    fNames = set()
    testNames = set()
    for line in out:
        line = line.strip()[1:-1]
        tokens = line.split()
        loc = tokens[0]
        if loc.startswith(os.path.join(k8s_root_dir, "test/e2e")):
            testName = " ".join(tokens[2:])
            end_ind = loc.find(":") #this gives the line where the test starts
            testNames.add(testName)
            fNames.add(loc[:end_ind])
    if True:
        print "Total Files {}\tTotal Tests {}".format(len(fNames), len(testNames))
        # raw_input("waiting")
        # print fNames
        # print list(testNames)[:10]
    return fNames, testNames
   
def split_tests(testFiles, k8s_root_dir):
    start = time.time()
    hasOwner, needsOwner = set(), set()
    sigs = getSigList()
    ownerMap = defaultdict(set)
    for tF in testFiles:
        with open(tF, 'r') as f:
            matcher = re.compile(r"^//\s?OWNER\s?=\s?sig/(.+)", re.MULTILINE)
            this = matcher.search(f.read())
        rel_to_k8s = os.path.relpath(tF, k8s_root_dir)
        if this and this.groups()[0] in sigs:
            sig = this.groups()[0]
            ownerMap[sig].add(rel_to_k8s)
            hasOwner.add(rel_to_k8s)
        else:
            needsOwner.add(rel_to_k8s)
    print "{} files have Owners".format(len(hasOwner))
    print "{} fies need Owners".format(len(needsOwner))
    print time.time() - start, ' second have elapsed'
    return hasOwner, needsOwner, ownerMap


def main():
    args = sys.argv
    if len(args) < 2:
        print "Provide the full path to the kubernetes root dir"
        exit()
    path = args[1]
    sigMap = parse_test_owners(path)
    # get all Test Names from sigMap
    fromSigMap = set().union(*sigMap.values())
    
    testFile = os.path.join(path, "test/e2e/addon_update.go") 
    testFiles, testNames = find_tests(path)
    inBoth = testNames.intersection(fromSigMap)
    print "Number of e2e files: {}".format(len(testFiles))
    print "Number of tests from list/main.go: {}".format(len(testNames))
    print "Number of tests from test_owners.csv: {}".format(len(fromSigMap))
    print "Overlap between the two {} ".format(len(inBoth))
    hasOwner, needsOwner, ownerMap = split_tests(testFiles, path)

if __name__ == "__main__":
    main()
