#!/usr/bin/env python3
import argparse
import os


parser = argparse.ArgumentParser()
parser.add_argument("-t", "--times", action="store_true",
help="preserve modification times")
parser.add_argument("-p", "--perms", action="store_true",
help="preserve permissions")
parser.add_argument("SRC_FILE", type=str)
parser.add_argument("DESTINATION", type=str)
args = parser.parse_args()

def copy(src,des):
    content = os.open(src, os.O_RDONLY)
    
