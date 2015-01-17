from os import path
from javadoc_parser import *
from wikibuilder import *

APPNAME = 'testapp'
REPODIR = ''

def buildWiki():
    wikidir = REPODIR + '\\' + APPNAME + '.wiki\\'
    wiki = Wiki(wikidir)
    wiki.create()
    wiki.setTag('title', 'TEST TITLE')
    wiki.setTag('subtitle', 'test subtitle')

def collateData():
    javadocs = getJavadocText(open(path.join(REPODIR, 'Test.java'), 'r'))
    tags, text = extractTags(javadocs)
    print tags

if __name__ == '__main__':
    REPODIR = path.join(path.dirname(path.realpath(__file__)), APPNAME)
    #collateData()
    buildWiki()