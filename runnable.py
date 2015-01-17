'''
Created on Jan 16, 2015

@author: Dan Green
'''

from os import path
from javadoc_parser import *

def collateData(repodir):
    javadocs = getJavadocText(open(path.join(repodir, 'Test.java'), 'r'))
    tags, text = extractTags(javadocs)
    print tags

if __name__ == '__main__':
    repodir = path.join(path.dirname(path.realpath(__file__)), 'testapp')
    collateData(repodir)
