'''
Created on Jan 16, 2015

@author: Dan Green
'''

from os import path
from javadoc_parser import *

def collateData(repodir):
    javadocs = getJavadocs(open('Test.java', 'r'))
    tags, text = extractTags(javadocs)
    print tags, text

if __name__ == '__main__':
    repodir = path.dirname(path.realpath(__file__)) + '\\testapp'
    collateData(repodir)
    print repodir