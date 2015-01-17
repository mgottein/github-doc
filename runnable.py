'''
Created on Jan 16, 2015

@author: Dan Green
'''

from javadoc_parser import *

def collateData(repodir):
    javadocs = getJavadocs(open('Test.java', 'r'))
    tags, text = extractTags(javadocs)
    print tags, text

if __name__ == '__main__':
    repodir = 'C:\Users\Dan\Documents\GitHub\github-doc\testapp'
    collateData(repodir)